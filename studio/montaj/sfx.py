#!/usr/bin/env python3
"""Efecte sonore scurte, generate (fără drepturi de autor): whoosh la tăieturi, pop la text, ding la final, boom la hook.
Le folosește reel_lista.py când specul are "sfx": true. Rulat singur, scrie wav-urile în studio/montaj/sfx/ ca să le asculți."""
import math, os, wave
import numpy as np
SR = 48000

def _env(n, a, r):
    """anvelopă: urcă în a secunde, coboară exponențial pe restul"""
    t = np.arange(n) / SR; e = np.minimum(1, t / max(a, 1e-4)); return e * np.exp(-np.maximum(0, t - a) / r)

def whoosh(d=0.42):
    n = int(SR * d); rng = np.random.default_rng(7); x = rng.standard_normal(n)
    # bandă care urcă (filtru rezonant simplu, frecvența crește în timp) = senzația de „trecere”
    out = np.zeros(n); y1 = y2 = 0.0
    for i in range(n):
        f = 350 + 3200 * (i / n) ** 1.6; w = 2 * math.pi * f / SR; q = 0.92
        y = x[i] * (1 - q) + 2 * q * math.cos(w) * y1 - q * q * y2; y2, y1 = y1, y; out[i] = y
    t = np.arange(n) / n; env = np.sin(np.pi * t) ** 1.5
    return 0.55 * out / (np.abs(out).max() + 1e-9) * env

def pop(d=0.12):
    n = int(SR * d); t = np.arange(n) / SR; f = 300 + 700 * np.exp(-t / 0.018)
    ph = 2 * np.pi * np.cumsum(f) / SR; return 0.6 * np.sin(ph) * _env(n, 0.002, 0.03)

def ding(d=1.1):
    n = int(SR * d); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * 1318.5 * t) + 0.45 * np.sin(2 * np.pi * 2637 * t) + 0.2 * np.sin(2 * np.pi * 3955.5 * t)
    return 0.35 * s * _env(n, 0.003, 0.32)

def boom(d=0.7):
    n = int(SR * d); t = np.arange(n) / SR; f = 38 + 70 * np.exp(-t / 0.06)
    ph = 2 * np.pi * np.cumsum(f) / SR; return 0.9 * np.sin(ph) * _env(n, 0.004, 0.22)

def write(path, x):
    x = np.clip(x, -1, 1); d = (x * 32767).astype('<i2')
    with wave.open(path, 'wb') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes())

def timeline(events, total, path):
    """events: [(secunda, 'whoosh'|'pop'|'ding'|'boom', volum)] → un singur wav cu toate sunetele la locul lor"""
    out = np.zeros(int(SR * (total + 1.5))); gen = {'whoosh': whoosh, 'pop': pop, 'ding': ding, 'boom': boom}; cache = {}
    for t, kind, vol in events:
        s = cache.setdefault(kind, gen[kind]()); i = max(0, int(SR * t)); out[i:i + len(s)] += vol * s[:len(out) - i]
    write(path, out[:int(SR * total)] * 0.9)

if __name__ == '__main__':
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sfx'); os.makedirs(d, exist_ok=True)
    for k, f in (('whoosh', whoosh), ('pop', pop), ('ding', ding), ('boom', boom)): write(os.path.join(d, k + '.wav'), f())
    print(d)
