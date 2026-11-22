"""Klassisches Runge-Kutta-Verfahren (4. Ordnung).

Wertet die Ableitung an vier Stellen im Zeitschritt aus und mittelt geschickt.
Sehr genau pro Schritt (Fehler pro Zeit ~ dt^4), aber nicht symplektisch:
Über lange Zeiten driftet die Energie trotzdem langsam weg.
"""


def step(x, v, a, dt):
    # Jeder k-Wert ist ein Paar (Änderung der Orte, Änderung der Geschwindigkeiten)
    k1x, k1v = v,                 a(x)
    k2x, k2v = v + dt / 2 * k1v,  a(x + dt / 2 * k1x)
    k3x, k3v = v + dt / 2 * k2v,  a(x + dt / 2 * k2x)
    k4x, k4v = v + dt * k3v,      a(x + dt * k3x)

    x_new = x + dt / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
    v_new = v + dt / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
    return x_new, v_new
