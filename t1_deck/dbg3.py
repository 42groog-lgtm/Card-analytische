import t1sim, decks, random
from t1sim import *
d, cmds, cz = decks.build('A')
rng = random.Random(11)
for i in range(12):
    lib = list(d); rng.shuffle(lib)
    hand = lib[:8]; rest = lib[8:]
    st = new_state(hand, rest, 1, cz, True)
    r, path = plan(planning_view(st), 20000)
    print(sorted(hand)); print('   ->', r, [a[:2] for a, l in path][-4:])
