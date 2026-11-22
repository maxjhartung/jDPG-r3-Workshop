"""Geschwindigkeits-Verlet / Leapfrog (2. Ordnung).

Halber Schritt für die Geschwindigkeit, ganzer Schritt für den Ort, dann wieder
ein halber Schritt für die Geschwindigkeit ("Kick - Drift - Kick").
Symplektisch und zeitumkehrbar: Der Energiefehler schwankt, wächst aber nicht.
Deshalb der Standard in Molekulardynamik und Himmelsmechanik.
"""


def step(x, v, a, dt):
    v_half = v + dt / 2 * a(x)           # Kick
    x_new = x + dt * v_half              # Drift
    v_new = v_half + dt / 2 * a(x_new)   # Kick
    return x_new, v_new
