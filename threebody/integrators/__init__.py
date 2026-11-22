"""Integratoren: Jede Datei in diesem Ordner ist ein Verfahren.

Eine Datei `name.py` muss genau eine Funktion enthalten:

    def step(x, v, a, dt):
        ...
        return x_new, v_new

    x, v  aktuelle Orte und Geschwindigkeiten (NumPy-Arrays, Form (N, d))
    a     Funktion, die zu Orten x die Beschleunigungen a(x) liefert
    dt    Zeitschritt

Der Integrator weiß also nichts über Gravitation, er bekommt nur a(x).
Ein neuer Integrator ist einfach eine neue Datei: Er taucht automatisch in
`available()` und in der Kommandozeile (--integrator name) auf.

Für Experimente ohne das Paket zu ändern, kann statt eines Namens auch ein Pfad
zu einer eigenen .py-Datei mit einer Funktion `step` angegeben werden.
"""
import importlib
import importlib.util
import pkgutil
from pathlib import Path


def available():
    """Namen aller mitgelieferten Integratoren (= Dateinamen ohne .py)."""
    return sorted(m.name for m in pkgutil.iter_modules(__path__) if not m.name.startswith("_"))


def load(name):
    """Gibt die `step`-Funktion des Integrators `name` zurück.

    `name` ist entweder ein mitgelieferter Integrator (z. B. "verlet") oder
    ein Pfad zu einer eigenen Datei (z. B. "my_integrator.py").
    """
    if name.endswith(".py"):
        path = Path(name)
        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    elif name in available():
        module = importlib.import_module(f"{__name__}.{name}")
    else:
        raise ValueError(f"Unbekannter Integrator {name!r}. Verfügbar: {', '.join(available())}")
    return module.step
