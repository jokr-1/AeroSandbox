from scipy import interpolate
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from typing import Callable


def plot_with_bootstrapped_uncertainty(
        x: np.ndarray,
        y: np.ndarray,
        y_stdev: float,
        ci: float = 0.95,
        color=None,
        label_line=None,
        label_ci=None,
        label_scatter=None,
        n_bootstraps=2000,
        n_fit_points=300,
        spline_degree=3,
):
    if not (ci > 0 and ci < 1):
        raise ValueError("Confidence interval `ci` should be in the range of (0, 1).")

    x_fit = np.linspace(x.min(), x.max(), n_fit_points)

    y_bootstrap_fits = np.empty((n_bootstraps, len(x_fit)))

    for i in tqdm(range(n_bootstraps), desc="Bootstrapping", unit=" samples"):

        ### Obtain a bootstrap resample
        ### Here, instead of truly resampling, we just pick weights that effectively mimic a resample.
        ### A computationally-efficient way to pick weights is the following clever trick with uniform sampling:
        splits = np.random.rand(len(x) + 1) * len(x)  # "limit" bootstrapping
        splits[0] = 0
        splits[-1] = len(x)

        weights = np.diff(np.sort(splits))

        y_bootstrap_fits[i, :] = interpolate.UnivariateSpline(
            x=x,
            y=y,
            w=weights,
            s=len(x) * y_stdev,
            k=spline_degree,
            ext='extrapolate'
        )(x_fit)

    ### Compute a confidence interval using equal-tails method
    y_median_and_ci = np.nanquantile(
        y_bootstrap_fits,
        q=[
            (1 - ci) / 2,
            0.5,
            1 - (1 - ci) / 2
        ],
        axis=0
    )

    print(
        np.std(
            interpolate.InterpolatedUnivariateSpline(x_fit, y_median_and_ci[1, :])(x) - y
        )
    )

    line, = plt.plot(
        x_fit,
        y_median_and_ci[1, :],
        color=color,
        label=label_line
    )
    plt.fill_between(
        x_fit,
        y_median_and_ci[0, :],
        y_median_and_ci[2, :],
        color=line.get_color(),
        label=label_ci,
        alpha=0.25,
        linewidth=0
    )
    plt.plot(
        x,
        y,
        ".",
        color=line.get_color(),
        label=label_scatter,
        alpha=0.5
    )
    return x_fit, y_bootstrap_fits


if __name__ == '__main__':

    import matplotlib.pyplot as plt
    import aerosandbox.tools.pretty_plots as p

    np.random.seed(0)

    ### Generate data
    x = np.linspace(0, 10, 101)
    y_true = np.abs(x - 5)  # np.sin(x)
    y_noisy = y_true + 0.1 * np.random.randn(len(x))

    ### Plot spline regression
    fig, ax = plt.subplots(dpi=300)
    x_fit, y_bootstrap_fits = plot_with_bootstrapped_uncertainty(
        x,
        y_noisy,
        y_stdev=0.1,
        label_line="Best Estimate",
        label_scatter="Data",
        label_ci="95% CI",
    )
    ax.plot(x, y_true, "k", label="True Function", alpha=0.2)

    p.show_plot(
        "Spline Bootstrapping Test",
        r"$x$",
        r"$y$",
    )
