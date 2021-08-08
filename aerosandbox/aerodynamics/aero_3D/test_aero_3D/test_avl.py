import aerosandbox as asb
import aerosandbox.numpy as np
import pytest
from aerosandbox.aerodynamics.aero_3D.test_aero_3D.geometries.conventional import airplane


def test_avl():
    avl = asb.AVL(
        airplane=airplane,
        op_point=asb.OperatingPoint()
    )
    return avl.run()


if __name__ == '__main__':
    test_avl()
    # pytest.main()