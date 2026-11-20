import t1sim, decks, random, time
d, cmds, cz = decks.build('A')
for limit in (1000, 3000, 20000):
    rng = random.Random(5); w = 0; t0 = time.time()
    for i in range(400):
        w += t1sim.game(d, 1, rng, cz, max_mull=0, limit=limit)
    print(limit, w, f'{time.time()-t0:.0f}s')
