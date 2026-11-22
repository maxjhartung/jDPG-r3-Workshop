# threebody

Dieses Repo ist das Beispielprojekt für einen Workshop zu [r3](https://github.com/matthias-k/r3),
einem Werkzeug, das Rechnungen als unveränderliche Jobs mit festen Abhängigkeiten speichert.
So weiß man auch Monate später noch, mit welchem Code und welchen Eingaben ein Ergebnis
entstanden ist. Zum Einstieg in r3:
[Tutorial](https://kalliope2.matthias-k.org/bethgelab/r3-tutorial/playbook.html).

Das Paket selbst simuliert das Dreikörperproblem
(Newtonsche Gravitation) mit austauschbaren Integratoren und schreibt die
Trajektorie in eine Datei. Einzige Abhängigkeit: NumPy.

## Aufbau

```
threebody/
├── physics.py             Beschleunigung a(x) und Energie E(x, v)
├── initial_conditions.py  Beispiele (figure8, lagrange, pythagorean) oder Startwerte aus einer Datei
├── integrators/           ein Verfahren pro Datei
│   ├── euler.py
│   ├── rk4.py
│   └── verlet.py
├── simulation.py          Zeitschleife, Trajektorie speichern und laden
└── cli.py                 Kommandozeile
tests/                     Achterbahn-Lösung mit allen Integratoren
```

## Entwickeln mit uv

```bash
uv sync                    # legt .venv an, installiert numpy und pytest (aus uv.lock)
uv run pytest              # Tests
uv run threebody --list    # welche Startwerte und Integratoren gibt es?
uv build                   # baut dist/threebody-0.1.0-py3-none-any.whl
```

## Benutzen

```bash
threebody --start figure8 --integrator verlet --dt 0.01 --t-end 20 --output output/trajectory.npz
```

Installieren geht mit `uv pip install .` (oder `pip install .`), direkt von GitHub mit
`uv pip install git+https://github.com/<nutzer>/threebody-sim`. Ohne Installation reicht es,
wenn der Repo-Ordner im `PYTHONPATH` liegt: `PYTHONPATH=pfad/zum/repo python -m threebody ...`

| Option | Bedeutung | Standard |
|---|---|---|
| `--start` | Beispielname oder Pfad zu `.json`/`.yaml` mit Startwerten | `figure8` |
| `--integrator` | Integratorname oder Pfad zu einer eigenen `.py`-Datei | `verlet` |
| `--dt`, `--t-end` | Zeitschritt, Simulationsdauer | `0.01`, `20` |
| `--G` | Gravitationskonstante (die Beispiele gelten für G = 1) | `1` |
| `--masses` | Massen überschreiben, z. B. `--masses 1 1 2` | aus `--start` |
| `--perturbation` | Körper 1 um diesen Betrag in x verschieben (Chaos-Experiment) | `0` |
| `--save-every` | nur jeden n-ten Schritt speichern | `1` |
| `--output` | Ausgabedatei | `output/trajectory.npz` |

### Die Ausgabedatei

Eine NumPy-Datei `.npz` mit

| Name | Form | Inhalt |
|---|---|---|
| `t` | (T,) | Zeitpunkte |
| `x` | (T, 3, 2) | Orte: Zeitpunkt, Körper, Koordinate |
| `v` | (T, 3, 2) | Geschwindigkeiten |
| `m` | (3,) | Massen |
| `G` | Zahl | Gravitationskonstante |
| `info` | Text (JSON) | alle Parameter des Laufs |

```python
from threebody import load_trajectory, energy

d = load_trajectory("output/trajectory.npz")
E = energy(d["x"], d["v"], d["m"], d["G"])      # Energie zu jedem Zeitpunkt
print(d["info"]["integrator"], abs(E - E[0]).max() / abs(E[0]))
```

**Warum steht die Energie nicht in der Datei?** Weil sie eindeutig aus Orten,
Geschwindigkeiten und Massen folgt. Sie zu berechnen ist eine eigene Auswertung,
also in r3 ein eigener Job, der von den Simulationen abhängt. So kann man die
Auswertung ändern (z. B. Drehimpuls dazunehmen), ohne neu zu simulieren.

### Eigene Startwerte

`start.json`:
```json
{
  "masses": [1, 1, 1],
  "positions": [[-1, 0], [1, 0], [0, 0]],
  "velocities": [[0.347111, 0.532728], [0.347111, 0.532728], [-0.694222, -1.065456]]
}
```
`threebody --start start.json`. Das ist wieder die Acht, nur anders gedreht und
skaliert (Periode 6.3244), in der Form von Šuvakov & Dmitrašinović, Phys. Rev. Lett. 110
(2013). Dort stehen viele weitere periodische Bahnen im selben Format.

## Einen Integrator hinzufügen

Jeder Integrator ist eine Datei in `threebody/integrators/` mit genau einer Funktion:

```python
def step(x, v, a, dt):
    """x, v: Orte und Geschwindigkeiten, a: Funktion a(x), dt: Zeitschritt."""
    ...
    return x_new, v_new
```

Der Integrator weiß nichts über Gravitation, er bekommt nur `a(x)`. Beispiel
`euler_cromer.py` (semi-implizites Euler, ebenfalls symplektisch):

```python
def step(x, v, a, dt):
    v_new = v + dt * a(x)
    x_new = x + dt * v_new      # schon die neue Geschwindigkeit verwenden
    return x_new, v_new
```

Datei in `integrators/` legen, fertig: `threebody --integrator euler_cromer`.
Zum schnellen Ausprobieren, ohne das Paket zu ändern, geht auch
`threebody --integrator ./euler_cromer.py`.

## In einem r3-Job verwenden

r3 kann ein Git-Repository als Abhängigkeit auschecken (derzeit nur von github.com).
Beim `r3 commit` wird `branch` in eine feste Commit-ID aufgelöst und im Job gespeichert,
der Job weiß also für immer, mit welchem Code er gerechnet hat.

`r3.yaml`:
```yaml
dependencies:
  - repository: https://github.com/<nutzer>/threebody-sim.git
    branch: main            # oder tag: v0.1.0, oder commit: <volle ID>
    destination: sim
```

`run.sh` (nach `r3 checkout` in der Arbeitskopie):
```bash
PYTHONPATH=sim python3 -m threebody --start figure8 --integrator verlet \
    --dt 0.05 --t-end 2000 --save-every 20 --output output/trajectory.npz
```

Das Paket liegt bewusst direkt im Repo und nicht unter `src/`, damit `PYTHONPATH=sim`
reicht und im Job nichts installiert werden muss. Wer lieber installiert:
`uv pip install ./sim`.

## Welche Parameter zeigen etwas?

Gemessen mit diesem Paket, Achterbahn-Lösung, größter relativer Energiefehler:

| | dt = 0.01, t = 100 | dt = 0.05, t = 500 | dt = 0.05, t = 2000 |
|---|---|---|---|
| Euler | 6e-1 | | |
| RK4 | 4e-8 | 7e-4 | 3e-3 (wächst weiter) |
| Verlet | 6e-5 | 2e-3 | 2e-3 (bleibt) |

Kurz und mit kleinem dt gewinnt RK4. Lang und mit größerem dt driftet RK4
gleichmäßig weg, Verlet bleibt beschränkt. Fairer Vergleich bei gleichem Aufwand:
RK4 braucht 4 Kraftauswertungen pro Schritt, Verlet 2, also RK4 mit doppeltem dt
gegen Verlet antreten lassen.
