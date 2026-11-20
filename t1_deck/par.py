"""Parallel runner: python3 par.py CODE SEAT N SEED [max_mull] [K] -> prints wins/n and Wilson CI"""
import sys, time, random, json
from multiprocessing import Process, Queue
import t1sim, decks

def worker(code, seat, n, seed, max_mull, K, q, deck_override, taus=(0.34, 0.2, 0.1, 0.0)):
    if deck_override:
        d, cz = deck_override
    else:
        d, cmds, cz = decks.build(code)
    rng = random.Random(seed)
    w = 0; mulls = 0
    for i in range(n):
        try:
            win, m = t1sim.game(d, seat, rng, cz, max_mull=max_mull, K=K, limit=2000, return_info=True, taus=taus)
        except Exception as e:
            import traceback; traceback.print_exc(); win, m = False, 0
        w += win; mulls += m
    q.put((w, n, mulls))

def run_par(code, seat, n, seed, max_mull=3, K=4, nproc=4, deck_override=None, taus=(0.34, 0.2, 0.1, 0.0)):
    q = Queue(); ps = []
    per = n // nproc
    for i in range(nproc):
        p = Process(target=worker, args=(code, seat, per, seed * 1000 + i, max_mull, K, q, deck_override, taus)); p.start(); ps.append(p)
    res = [q.get() for _ in ps]
    for p in ps: p.join()
    w = sum(r[0] for r in res); n = sum(r[1] for r in res); m = sum(r[2] for r in res)
    return w, n, m

if __name__ == '__main__':
    code, seat, n, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    mm = int(sys.argv[5]) if len(sys.argv) > 5 else 3
    K = int(sys.argv[6]) if len(sys.argv) > 6 else 4
    taus = tuple(float(x) for x in sys.argv[7].split(',')) if len(sys.argv) > 7 else (0.34, 0.2, 0.1, 0.0)
    t0 = time.time()
    w, n, m = run_par(code, seat, n, seed, mm, K, taus=taus)
    lo, hi = t1sim.wilson(w, n)
    print(f'{code} seat{seat} mull<={mm} taus={taus} P={w/n:.5f} IC95[{lo:.5f},{hi:.5f}] n={n} avg_mull={m/n:.2f} {time.time()-t0:.0f}s', flush=True)
