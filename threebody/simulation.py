"""Die eigentliche Simulation und das Speichern/Laden der Trajektorie."""
import json
from pathlib import Path

import numpy as np

from . import integrators
from .physics import acceleration


def simulate(m, x, v, integrator="verlet", dt=0.01, t_end=10.0, G=1.0, save_every=1):
    """Integriert die Bewegungsgleichungen von t = 0 bis t = t_end.

    Gibt (t, xs, vs) zurück: Zeiten (T,), Orte (T, N, d), Geschwindigkeiten (T, N, d).
    Gespeichert wird jeder `save_every`-te Schritt (der Anfangszustand immer).
    """
    step = integrators.load(integrator)

    def a(x):
        return acceleration(x, m, G)

    n_steps = int(round(t_end / dt))
    ts, xs, vs = [0.0], [x.copy()], [v.copy()]
    for k in range(1, n_steps + 1):
        x, v = step(x, v, a, dt)
        if k % save_every == 0:
            ts.append(k * dt)
            xs.append(x.copy())
            vs.append(v.copy())
    return np.array(ts), np.array(xs), np.array(vs)


def save_trajectory(path, t, x, v, m, G, **info):
    """Schreibt die Trajektorie als NumPy-Datei (.npz).

    Inhalt: t, x, v, m, G und `info` (alle Parameter des Laufs als JSON-Text).
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, t=t, x=x, v=v, m=m, G=G, info=json.dumps(info, ensure_ascii=False))


def load_trajectory(path):
    """Liest eine mit `save_trajectory` geschriebene Datei. Gibt ein dict zurück:
    t, x, v, m, G (NumPy) und info (dict mit den Parametern des Laufs)."""
    with np.load(path) as d:
        data = {k: d[k] for k in ("t", "x", "v", "m")}
        data["G"] = float(d["G"])
        data["info"] = json.loads(str(d["info"]))
    return data
