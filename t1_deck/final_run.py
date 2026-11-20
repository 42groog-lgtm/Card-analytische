"""Final measurements: python3 final_run.py LABEL SEAT N SEED '{"max_mull":1,"free_mull":1,"K":4}' [draw=1]"""
import sys, json, time, random
from multiprocessing import Process, Queue
import t1sim, decks

def worker(seat, n, seed, kw, draw, q, deck_spec):
    t1sim.DRAW_T1 = bool(draw)
    d, cz = deck_spec
    rng = random.Random(seed); w = 0; m = 0; err = 0
    for i in range(n):
        try:
            win, mm = t1sim.game(d, seat, rng, cz, return_info=True, **kw)
        except Exception:
            win, mm = False, 0; err += 1
        w += win; m += mm
    q.put((w, n, m, err))

def run(label, seat, n, seed, kw, draw=1, deck_spec=None, nproc=4):
    if deck_spec is None:
        import os
        d, cmds, cz = decks.build(os.environ.get('DECK', 'A')); deck_spec = (d, cz)
    q = Queue(); ps = []
    for i in range(nproc):
        p = Process(target=worker, args=(seat, n // nproc, seed * 1000 + i, kw, draw, q, deck_spec)); p.start(); ps.append(p)
    rs = [q.get() for _ in ps]
    for p in ps: p.join()
    w = sum(r[0] for r in rs); N = sum(r[1] for r in rs); m = sum(r[2] for r in rs); e = sum(r[3] for r in rs)
    lo, hi = t1sim.wilson(w, N)
    return {'label': label, 'seat': seat, 'n': N, 'wins': w, 'p': w / N, 'lo': lo, 'hi': hi, 'avg_mull': m / N,
            'errors': e, 'kw': kw, 'draw': draw, 'seed': seed}

if __name__ == '__main__':
    label, seat, n, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    kw = json.loads(sys.argv[5]); draw = int(sys.argv[6]) if len(sys.argv) > 6 else 1
    t0 = time.time()
    import os
    r = run(label, seat, n, seed, kw, draw)
    r['deck'] = os.environ.get('DECK', 'A')
    r['seconds'] = round(time.time() - t0)
    print(json.dumps(r), flush=True)
    with open('results.jsonl', 'a') as f: f.write(json.dumps(r) + '\n')
