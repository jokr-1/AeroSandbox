import aerosandbox as asb
import aerosandbox.numpy as np
import pytest
from scipy import integrate

u_e_0 = 100
v_e_0 = 0
w_e_0 = -100
speed_0 = (u_e_0 ** 2 + w_e_0 ** 2) ** 0.5
gamma_0 = np.arctan2(-w_e_0, u_e_0)
track_0 = 0

time=np.linspace(0, 10, 1001)

def get_trajectory(
        parameterization: type = asb.DynamicsPointMass3DCartesian,
        gravity=True,
        drag=True,
        plot=False
):
    if parameterization is asb.DynamicsPointMass3DCartesian:
        dyn = parameterization(
            mass_props=asb.MassProperties(mass=1),
            x_e=0,
            y_e=0,
            z_e=0,
            u_e=u_e_0,
            w_e=w_e_0,
        )
    elif parameterization is asb.DynamicsPointMass3DSpeedGammaTrack:
        dyn = parameterization(
            mass_props=asb.MassProperties(mass=1),
            x_e=0,
            z_e=0,
            speed=speed_0,
            gamma=gamma_0,
        )
    else:
        raise ValueError("Bad value of `parameterization`!")

    def derivatives(t, y):
        this_dyn = dyn.get_new_instance_with_state(y)
        if gravity:
            this_dyn.add_gravity_force()
        if drag:
            this_dyn.add_force(
                Fx=-0.01 * this_dyn.speed ** 2,
                axes="wind"
            )

        return this_dyn.unpack_state(this_dyn.state_derivatives())

    res = integrate.solve_ivp(
        fun=derivatives,
        t_span=(time[0], time[-1]),
        t_eval=time,
        y0=dyn.unpack_state(),
        vectorized=True,
        rtol=1e-9,
        atol=1e-9,
    )

    dyn = dyn.get_new_instance_with_state(res.y)

    if plot:
        import matplotlib.pyplot as plt;
        import aerosandbox.tools.pretty_plots as p

        fig, ax = plt.subplots()
        p.plot_color_by_value(dyn.x_e, dyn.altitude, c=dyn.speed, colorbar=True)
        p.equal()
        p.show_plot("Trajectory", "$x_e$", "$z_e$")

    return dyn


def test_final_position_Cartesian_with_drag():
    dyn = get_trajectory(
        parameterization=asb.DynamicsPointMass2DCartesian,
        drag=True
    )
    assert dyn[-1].x_e == pytest.approx(198.53465, abs=1e-2)
    assert dyn[-1].z_e == pytest.approx(44.452918, abs=1e-2)


def test_final_position_Cartesian_no_drag():
    dyn = get_trajectory(
        parameterization=asb.DynamicsPointMass2DCartesian,
        drag=False
    )
    assert dyn[-1].x_e == pytest.approx(1000, abs=1e-2)
    assert dyn[-1].z_e == pytest.approx(-509.5, abs=1e-2)


def test_final_position_SpeedGamma_with_drag():
    dyn = get_trajectory(
        parameterization=asb.DynamicsPointMass2DSpeedGamma,
        drag=True
    )
    assert dyn[-1].x_e == pytest.approx(198.53465, abs=1e-2)
    assert dyn[-1].z_e == pytest.approx(44.452918, abs=1e-2)


def test_final_position_SpeedGamma_no_drag():
    dyn = get_trajectory(
        parameterization=asb.DynamicsPointMass2DSpeedGamma,
        drag=False
    )
    assert dyn[-1].x_e == pytest.approx(1000, abs=1e-2)
    assert dyn[-1].z_e == pytest.approx(-509.5, abs=1e-2)


#
if __name__ == '__main__':
    dyn = get_trajectory(
        asb.DynamicsPointMass2DSpeedGamma,
        plot=True
    )
    pytest.main()
