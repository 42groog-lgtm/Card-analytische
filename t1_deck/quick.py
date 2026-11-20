import sys, time, t1sim, decks
n = int(sys.argv[1]); seat = int(sys.argv[2]) if len(sys.argv) > 2 else 1
for code in sys.argv[3] if len(sys.argv) > 3 else 'ABCD':
    d, cmds, cz = decks.build(code)
    t0 = time.time()
    w, n_ = t1sim.run(d, seat, n, 7, cz)
    lo, hi = t1sim.wilson(w, n_)
    print(f'{code} {"+".join(c.split(",")[0] for c in cmds):30s} seat{seat} P={w/n_:.4f} [{lo:.4f},{hi:.4f}] n={n_} {time.time()-t0:.0f}s', flush=True)
