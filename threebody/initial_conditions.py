"""Anfangsbedingungen: mitgelieferte Beispiele oder aus einer Datei.

Alle mitgelieferten Beispiele gelten für G = 1.
"""
import json
from pathlib import Path

import numpy as np

PRESETS = {
    "figure8": {
        "description": "Achterbahn-Lösung: drei gleiche Massen jagen sich auf einer Acht. "
                       "Periode T ≈ 6.326. Stabil, ideal zum Testen von Integratoren.",
        "source": "Chenciner & Montgomery, Annals of Math. 152 (2000); Werte nach C. Simó",
        "masses": [1.0, 1.0, 1.0],
        "positions": [[0.97000436, -0.24308753], [-0.97000436, 0.24308753], [0.0, 0.0]],
        "velocities": [[0.46620368, 0.43236573], [0.46620368, 0.43236573],
                       [-0.93240737, -0.86473146]],
    },
    "lagrange": {
        "description": "Gleichseitiges Dreieck, das starr rotiert (Lagrange 1772). "
                       "Für gleiche Massen instabil: kleine Fehler wachsen, die Form zerfällt.",
        "source": "J.-L. Lagrange, Essai sur le problème des trois corps (1772)",
        "masses": [1.0, 1.0, 1.0],
        # Ecken auf dem Einheitskreis, Bahngeschwindigkeit v = 3^(-1/4) für G = m = r = 1
        "positions": [[1.0, 0.0], [-0.5, 0.8660254037844386], [-0.5, -0.8660254037844386]],
        "velocities": [[0.0, 0.7598356856515925],
                       [-0.6580370064762462, -0.37991784282579627],
                       [0.6580370064762462, -0.37991784282579627]],
    },
    "pythagorean": {
        "description": "Pythagoreisches Problem: Massen 3, 4, 5 starten in Ruhe an den Ecken "
                       "eines 3-4-5-Dreiecks. Chaotisch, mit sehr engen Begegnungen.",
        "source": "Burrau 1913; Szebehely & Peters, Astron. J. 72 (1967)",
        "masses": [3.0, 4.0, 5.0],
        "positions": [[1.0, 3.0], [-2.0, -1.0], [1.0, -1.0]],
        "velocities": [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0]],
    },
}


def load(name_or_file):
    """Gibt (m, x, v) als NumPy-Arrays zurück.

    `name_or_file` ist entweder ein Name aus PRESETS (z. B. "figure8") oder ein
    Pfad zu einer .json-Datei (oder .yaml, falls PyYAML installiert ist) mit den
    Schlüsseln "masses", "positions" und "velocities", aufgebaut wie oben.
    """
    if name_or_file in PRESETS:
        data = PRESETS[name_or_file]
    else:
        path = Path(name_or_file)
        if not path.is_file():
            raise ValueError(f"{name_or_file!r} ist weder ein Beispiel "
                             f"({', '.join(PRESETS)}) noch eine Datei.")
        if path.suffix in (".yaml", ".yml"):
            import yaml
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        else:
            data = json.loads(path.read_text(encoding="utf-8"))

    m = np.array(data["masses"], dtype=float)
    x = np.array(data["positions"], dtype=float)
    v = np.array(data["velocities"], dtype=float)
    if not (x.shape == v.shape and x.shape[0] == len(m)):
        raise ValueError(f"Passt nicht zusammen: {len(m)} Massen, Orte {x.shape}, "
                         f"Geschwindigkeiten {v.shape}")
    return m, x, v
