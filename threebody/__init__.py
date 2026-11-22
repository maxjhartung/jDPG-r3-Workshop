"""Dreikörperproblem zum Ausprobieren von Integratoren.

    from threebody import initial_conditions, simulate, energy
    m, x, v = initial_conditions.load("figure8")
    t, xs, vs = simulate(m, x, v, integrator="rk4", dt=0.01, t_end=20)
    E = energy(xs, vs, m)
"""
from importlib.metadata import PackageNotFoundError, version

from . import initial_conditions, integrators
from .physics import acceleration, energy
from .simulation import load_trajectory, save_trajectory, simulate

try:
    __version__ = version("threebody")
except PackageNotFoundError:   # z. B. ohne Installation über PYTHONPATH eingebunden
    __version__ = "0.1.0"
