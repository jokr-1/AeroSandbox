from aerosandbox.tools.fitting import fit
import pytest
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(palette=sns.color_palette("husl"))

plot = False # Should we plot during testing?

def test_single_dimensional_quadratic_fitting():
    np.random.seed(0)  # Set a seed for repeatability.

    ### Make some data
    x = np.linspace(0, 10, 50)
    noise = 5 * np.random.randn(len(x))
    y = x ** 2 - 8 * x + 5 + noise

    ### Fit data
    def model(x, p):
        return (
                p["a"] * x["x1"] ** 2 +
                p["b"] * x["x1"] +
                p["c"]
        )

    x_data = {
        "x1": x
    }

    fitted_parameters = fit(
        model=model,
        x_data=x_data,
        y_data=y,
        param_guesses={
            "a": 1,
            "b": 1,
            "c": 1,
        },
        param_bounds={
            "a": (None, None),
            "b": (None, None),
            "c": (None, None),
        },
    )

    ### Plot data and fit
    if plot:
        fig, ax = plt.subplots(1, 1, figsize=(6.4, 4.8), dpi=200)
        plt.plot(x, y, ".", label="Data")
        plt.plot(x, model(x_data, fitted_parameters), "-", label="Fit")
        plt.xlabel(r"$x$")
        plt.ylabel(r"$y$")
        plt.title(r"Automatic-Differentiable Fitting")
        plt.tight_layout()
        plt.legend()
        # plt.savefig("C:/Users/User/Downloads/temp.svg")
        plt.show()

    ### Check that the fit is right
    assert fitted_parameters["a"] == pytest.approx(1.046091, abs=1e-3)
    assert fitted_parameters["b"] == pytest.approx(-9.166716, abs=1e-3)
    assert fitted_parameters["c"] == pytest.approx(9.984351, abs=1e-3)


def test_multidimensional_power_law_fitting():
    np.random.seed(0)  # Set a seed for repeatability.

    ### Make some data z(x,y)
    x = np.logspace(0, 3)
    y = np.logspace(0, 3)
    X, Y = np.meshgrid(x, y, indexing="ij")
    noise = np.random.lognormal(mean=0, sigma=0.05)
    Z = 0.5 * X ** 0.75 * Y ** 1.25 * noise

    ### Fit data
    def model(x, p):
        return (
                p["multiplier"] *
                x["X"] ** p["X_power"] *
                x["Y"] ** p["Y_power"]
        )

    x_data = {
        "X": X.flatten(),
        "Y": Y.flatten(),
    }

    fitted_parameters = fit(
        model=model,
        x_data=x_data,
        y_data=Z.flatten(),
        param_guesses={
            "multiplier": 1,
            "X_power"   : 1,
            "Y_power"   : 1,
        },
        param_bounds={
            "multiplier": (None, None),
            "X_power"   : (None, None),
            "Y_power"   : (None, None),
        },
        put_residuals_in_logspace=True
        # Putting residuals in logspace minimizes the norm of log-error instead of absolute error
    )

    ### Check that the fit is right
    assert fitted_parameters["multiplier"] == pytest.approx(0.546105, abs=1e-3)
    assert fitted_parameters["X_power"] == pytest.approx(0.750000, abs=1e-3)
    assert fitted_parameters["Y_power"] == pytest.approx(1.250000, abs=1e-3)

def test_error_from_no_flattening():
    np.random.seed(0)  # Set a seed for repeatability.

    ### Make some data z(x,y)
    x = np.logspace(0, 3)
    y = np.logspace(0, 3)
    X, Y = np.meshgrid(x, y, indexing="ij")
    noise = np.random.lognormal(mean=0, sigma=0.05)
    Z = 0.5 * X ** 0.75 * Y ** 1.25 * noise

    ### Fit data
    def model(x, p):
        return (
                p["multiplier"] *
                x["X"] ** p["X_power"] *
                x["Y"] ** p["Y_power"]
        )

    x_data = {
        "X": X.flatten(),
        "Y": Y,
    }

    with pytest.raises(ValueError):
        fitted_parameters = fit(
            model=model,
            x_data=x_data,
            y_data=Z.flatten(),
            param_guesses={
                "multiplier": 1,
                "X_power"   : 1,
                "Y_power"   : 1,
            },
            param_bounds={
                "multiplier": (None, None),
                "X_power"   : (None, None),
                "Y_power"   : (None, None),
            },
            put_residuals_in_logspace=True
            # Putting residuals in logspace minimizes the norm of log-error instead of absolute error
        )


if __name__ == '__main__':
    # test_single_dimensional_quadratic_fitting()
    # test_multidimensional_power_law_fitting()
    # test_error_from_no_flattening()
    pytest.main()
