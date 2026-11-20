import sys, random, collections
from multiprocessing import Pool
import t1sim, decks
d, cmds, cz = decks.build('A')
def job(seed):
    rng = random.Random(seed); wins = []
    for i in range(6000):
        lib = list(d); r2 = random.Random(seed * 100000 + i); r2.shuffle(lib)
        hand = lib[:8]
        st = t1sim.new_state(lib[:7], lib[7:], 1, cz, True)
        ok = t1sim.play_turn(st, r2, 2000)
        if ok: wins.append(tuple(sorted(hand)))
    return wins
with Pool(4) as p:
    res = p.map(job, range(4))
wins = [h for r in res for h in r]
print('wins', len(wins), 'of', 24000)
c = collections.Counter(card for h in wins for card in set(h))
base = collections.Counter()
for card, k in c.most_common(40):
    print(f'{k:4d} {card}')
