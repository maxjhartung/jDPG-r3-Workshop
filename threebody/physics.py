"""Newtonsche Gravitation für N Körper (hier meist N = 3).

Bezeichnungen, die im ganzen Paket gleich sind:
    x  Orte               Form (N, d)   N Körper in d Dimensionen
    v  Geschwindigkeiten  Form (N, d)
    m  Massen             Form (N,)
    G  Gravitationskonstante (Standard: 1, "natürliche Einheiten")
"""
import numpy as np


def acceleration(x, m, G=1.0):
    """Beschleunigung jedes Körpers durch die Anziehung aller anderen:

        a_i = G * Summe_{j != i}  m_j * (x_j - x_i) / |x_j - x_i|^3
    """
    d = x[np.newaxis, :, :] - x[:, np.newaxis, :]   # d[i, j] = x_j - x_i
    r = np.linalg.norm(d, axis=-1)                   # r[i, j] = |x_j - x_i|
    np.fill_diagonal(r, np.inf)                      # kein Körper zieht an sich selbst
    return G * np.sum(m[np.newaxis, :, np.newaxis] * d / r[:, :, np.newaxis] ** 3, axis=1)


def energy(x, v, m, G=1.0):
    """Gesamtenergie E = kinetische + potentielle Energie.

    Funktioniert für einen einzelnen Zustand (x, v mit Form (N, d)) und für eine
    ganze Trajektorie (x, v mit Form (T, N, d)); dann kommt ein Array der Länge T zurück.
    Wird NICHT von der Simulation geschrieben: Sie folgt eindeutig aus der Trajektorie
    und kann in einem eigenen Auswerte-Job berechnet werden.
    """
    x, v, m = np.asarray(x), np.asarray(v), np.asarray(m)
    kinetic = 0.5 * np.sum(m[:, np.newaxis] * v**2, axis=(-2, -1))
    potential = 0.0
    for i in range(len(m)):
        for j in range(i + 1, len(m)):
            r_ij = np.linalg.norm(x[..., i, :] - x[..., j, :], axis=-1)
            potential = potential - G * m[i] * m[j] / r_ij
    return kinetic + potential
