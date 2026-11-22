"""Explizites Euler-Verfahren (1. Ordnung).

Das einfachste Verfahren: Man nimmt an, dass Geschwindigkeit und Beschleunigung
während des ganzen Zeitschritts konstant bleiben. Fehler pro Zeit ~ dt.
Die Energie wächst systematisch: Umlaufbahnen spiralen nach außen.
"""


def step(x, v, a, dt):
    x_new = x + dt * v
    v_new = v + dt * a(x)
    return x_new, v_new
