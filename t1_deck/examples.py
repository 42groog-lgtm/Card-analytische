"""Collect example winning turns (hand + executed actions) to write the game plan."""
import random, json, collections, sys
import t1sim, decks
from t1sim import *

def play_logged(st, rng, limit=2000, max_iter=25):
    log = []
    st0 = st
    st = upkeep_phase(st, rng, limit)
    if st is not st0: log.append(('upkeep', 'tutor au-dessus de la bibliothèque pendant l’entretien'))
    st = do_draw(st, 1, True, rng)
    if st is None: return False, log
    log.append(('draw', 'pioche du tour'))
    st.phase = 'main'; st.pool = (0,) * 8
    for _ in range(max_iter):
        res, path = plan(planning_view(st), limit)
        if res == 'stuck': return False, log
        before = Counter(st.hand)
        n = execute(st, path, rng)
        if n is None: return False, log
        log.append(('plan', [a for a, l in path], [l for a, l in path]))
        if n.won: return True, log
        if res == 'dig':
            log.append(('reveal', sorted((Counter(n.hand) - before).elements())))
        st = n; st.unk = 0
    return False, log

if __name__ == '__main__':
    d, cmds, cz = decks.build('A')
    n = int(sys.argv[1]); out = []
    for i in range(n):
        rng = random.Random(900000 + i)
        lib = list(d); rng.shuffle(lib)
        st = new_state(lib[:7], lib[7:], 1, cz, True)
        hand8 = lib[:8]
        win, log = play_logged(st, rng)
        if win: out.append({'hand7': sorted(lib[:7]), 'draw': lib[7], 'log': log})
    json.dump(out, open('examples.json', 'w'), indent=1, ensure_ascii=False)
    print(len(out), 'wins of', n)
