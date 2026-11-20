"""Paired comparison (common random numbers) of deck variants.
Each variant replaces card OUT by card IN at the same position, so shuffles are identical."""
import sys, random, math, json, time
from multiprocessing import Process, Queue
import t1sim

def worker(base, variants, cz, n, seed0, kw, q):
    res = {'base': 0}
    disc = {v: [0, 0, 0] for v in variants}      # wins variant, base-only, variant-only
    for i in range(n):
        s = seed0 + i
        try: wb = t1sim.game(base, 1, random.Random(s), cz, **kw)
        except Exception: wb = False
        res['base'] += wb
        for v, deck in variants.items():
            try: wv = t1sim.game(deck, 1, random.Random(s), cz, **kw)
            except Exception: wv = False
            disc[v][0] += wv; disc[v][1] += (wb and not wv); disc[v][2] += (wv and not wb)
    q.put((res, disc))

def compare(base, swaps, cz, n, seed=1, nproc=4, **kw):
    variants = {}
    for out, inn in swaps:
        d = list(base); d[d.index(out)] = inn; variants[f'{out} -> {inn}'] = d
    q = Queue(); ps = []
    for i in range(nproc):
        p = Process(target=worker, args=(base, variants, cz, n // nproc, seed * 10**7 + i * 10**6, kw, q)); p.start(); ps.append(p)
    rs = [q.get() for _ in ps]
    for p in ps: p.join()
    nb = sum(r[0]['base'] for r in rs); N = (n // nproc) * nproc
    out = []
    for v in variants:
        w = sum(r[1][v][0] for r in rs); b = sum(r[1][v][1] for r in rs); c = sum(r[1][v][2] for r in rs)
        z = (c - b) / math.sqrt(b + c) if b + c else 0.0
        out.append((v, w, b, c, z))
    return nb, N, out
