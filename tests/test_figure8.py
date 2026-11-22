"""Kurze Tests: Achterbahn-Lösung mit allen Integratoren.   Ausführen mit:  uv run pytest"""
import numpy as np
import pytest

from threebody import energy, initial_conditions, integrators, load_trajectory, simulate
from threebody.cli import main

PERIOD = 6.3259  # Periode der Achterbahn-Lösung


def relative_energy_error(xs, vs, m):
    E = energy(xs, vs, m)
    return np.max(np.abs((E - E[0]) / E[0]))


@pytest.mark.parametrize("name", integrators.available())
def test_every_integrator_runs(name):
    m, x, v = initial_conditions.load("figure8")
    t, xs, vs = simulate(m, x, v, integrator=name, dt=0.01, t_end=1.0)
    assert t.shape == (101,) and xs.shape == vs.shape == (101, 3, 2)
    assert np.isfinite(xs).all()


@pytest.mark.parametrize("name, limit", [("rk4", 1e-6), ("verlet", 1e-3)])
def test_energy_over_ten_periods(name, limit):
    m, x, v = initial_conditions.load("figure8")
    _, xs, vs = simulate(m, x, v, integrator=name, dt=0.01, t_end=10 * PERIOD)
    assert relative_energy_error(xs, vs, m) < limit


@pytest.mark.parametrize("name", ["rk4", "verlet"])
def test_back_at_start_after_one_period(name):
    m, x, v = initial_conditions.load("figure8")
    _, xs, _ = simulate(m, x, v, integrator=name, dt=0.001, t_end=PERIOD)
    assert np.abs(xs[-1] - x).max() < 1e-3


def test_euler_is_worse_than_the_others():
    m, x, v = initial_conditions.load("figure8")
    error = {}
    for name in ("euler", "rk4", "verlet"):
        _, xs, vs = simulate(m, x, v, integrator=name, dt=0.01, t_end=PERIOD)
        error[name] = relative_energy_error(xs, vs, m)
    assert error["euler"] > 100 * error["verlet"]
    assert error["euler"] > 100 * error["rk4"]


def test_energy_same_for_single_state_and_trajectory():
    m, x, v = initial_conditions.load("pythagorean")
    _, xs, vs = simulate(m, x, v, dt=0.001, t_end=0.1)
    E = energy(xs, vs, m)
    assert E.shape == (len(xs),)
    assert np.isclose(E[-1], energy(xs[-1], vs[-1], m))


def test_all_presets_load():
    for name in initial_conditions.PRESETS:
        m, x, v = initial_conditions.load(name)
        assert x.shape == v.shape == (len(m), 2)


def test_cli_writes_trajectory(tmp_path):
    path = tmp_path / "trajectory.npz"
    main(["--start", "figure8", "--integrator", "rk4", "--dt", "0.01", "--t-end", "1",
          "--masses", "1", "1", "2", "--output", str(path)])
    d = load_trajectory(path)
    assert d["x"].shape == (101, 3, 2)
    assert list(d["m"]) == [1, 1, 2]
    assert d["info"]["integrator"] == "rk4"


def test_custom_integrator_from_file_and_start_from_json(tmp_path):
    (tmp_path / "euler_cromer.py").write_text(
        "def step(x, v, a, dt):\n"
        "    v_new = v + dt * a(x)\n"
        "    return x + dt * v_new, v_new\n")
    (tmp_path / "start.json").write_text(
        '{"masses": [1, 1], "positions": [[1, 0], [-1, 0]], '
        '"velocities": [[0, 0.35], [0, -0.35]]}')
    m, x, v = initial_conditions.load(str(tmp_path / "start.json"))
    _, xs, vs = simulate(m, x, v, integrator=str(tmp_path / "euler_cromer.py"),
                         dt=0.01, t_end=50)
    assert relative_energy_error(xs, vs, m) < 0.05
