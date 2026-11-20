import t1sim, decks, random
from t1sim import *
d, cmds, cz = decks.build('A')
def test(hand, label):
    lib = [c for c in d]
    for c in hand: lib.remove(c)
    random.Random(1).shuffle(lib)
    st = new_state(hand, lib, 1, cz, True)
    v = planning_view(st)
    r, path = plan(v, 3000)
    print(label, r, [a for a, l in path][:12])
test(['Underground Sea', "Thassa's Oracle", 'Demonic Consultation', 'Lotus Petal', 'Brainstorm', 'Ponder', 'Opt', 'Doomsday'], 'basic')
test(['Underground Sea', 'Demonic Tutor', 'Dark Ritual', 'Lotus Petal', "Thassa's Oracle", 'Ponder', 'Opt', 'Doomsday'], 'tutor')
test(['Underground Sea', 'Sol Ring', 'Lotus Petal', 'Chrome Mox', "Thassa's Oracle", 'Demonic Consultation', 'Opt', 'Doomsday'], 'chrome')
