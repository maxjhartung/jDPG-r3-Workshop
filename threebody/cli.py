"""Kommandozeile: simuliert und schreibt die Trajektorie in eine Datei.

Beispiel:
    threebody --start figure8 --integrator verlet --dt 0.01 --t-end 20 --output output/trajectory.npz
"""
import argparse

import numpy as np

from . import __version__, initial_conditions, integrators
from .simulation import save_trajectory, simulate


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="threebody",
        description="Simuliert das Dreikörperproblem und speichert die Trajektorie "
                    "(t, Orte, Geschwindigkeiten, Massen) als .npz-Datei.")
    p.add_argument("--start", default="figure8",
                   help="Name eines Beispiels (siehe --list) oder Pfad zu einer "
                        ".json/.yaml-Datei mit Anfangswerten. Standard: figure8")
    p.add_argument("--integrator", default="verlet",
                   help="Name eines Integrators (siehe --list) oder Pfad zu einer eigenen "
                        ".py-Datei mit einer Funktion step(x, v, a, dt). Standard: verlet")
    p.add_argument("--dt", type=float, default=0.01, help="Zeitschritt. Standard: 0.01")
    p.add_argument("--t-end", type=float, default=20.0, help="Simulationsdauer. Standard: 20")
    p.add_argument("--G", type=float, default=1.0, help="Gravitationskonstante. Standard: 1")
    p.add_argument("--masses", type=float, nargs="+",
                   help="Massen überschreiben, z. B. --masses 1 1 2")
    p.add_argument("--perturbation", type=float, default=0.0,
                   help="Verschiebt Körper 1 um diesen Betrag in x-Richtung "
                        "(z. B. 1e-8 für Chaos-Experimente). Standard: 0")
    p.add_argument("--save-every", type=int, default=1,
                   help="Nur jeden n-ten Schritt speichern (kleinere Dateien). Standard: 1")
    p.add_argument("--output", default="output/trajectory.npz",
                   help="Ausgabedatei. Standard: output/trajectory.npz")
    p.add_argument("--list", action="store_true",
                   help="Verfügbare Beispiele und Integratoren anzeigen und beenden")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = p.parse_args(argv)

    if args.list:
        print("Anfangswerte (--start):")
        for name, preset in initial_conditions.PRESETS.items():
            print(f"  {name:12s} {preset['description']}")
        print("Integratoren (--integrator):")
        print("  " + ", ".join(integrators.available()))
        return

    try:
        m, x, v = initial_conditions.load(args.start)
        integrators.load(args.integrator)   # meldet früh einen unbekannten Namen
    except ValueError as error:
        p.error(str(error))
    if args.masses is not None:
        if len(args.masses) != len(m):
            p.error(f"--masses braucht {len(m)} Werte, nicht {len(args.masses)}")
        m = np.array(args.masses, dtype=float)
    x[0, 0] += args.perturbation

    t, xs, vs = simulate(m, x, v, integrator=args.integrator, dt=args.dt,
                         t_end=args.t_end, G=args.G, save_every=args.save_every)

    save_trajectory(args.output, t, xs, vs, m, args.G,
                    start=args.start, integrator=args.integrator, dt=args.dt,
                    t_end=args.t_end, perturbation=args.perturbation,
                    save_every=args.save_every, version=__version__)
    print(f"{len(t)} Zeitpunkte ({args.integrator}, dt = {args.dt:g}, "
          f"t_end = {args.t_end:g}) -> {args.output}")
