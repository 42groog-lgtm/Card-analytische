"""Paired sensitivity: loss of one key piece (replaced by a blank card), no mulligan, seat 1."""
import json, sys, t1sim, decks
from pair import compare
d, cmds, cz = decks.build('A')
blank = 'Intuition'   # real card, not modeled -> blank
assert blank not in d
swaps = [(c, blank) for c in ["Lion's Eye Diamond", 'Culling the Weak', "Thassa's Oracle", 'Demonic Consultation',
                               'Tainted Pact', 'Ad Nauseam', 'Beseech the Mirror', 'Demonic Tutor']]
n = int(sys.argv[1])
nb, N, out = compare(d, swaps, cz, n, seed=3, max_mull=0)
res = {'n': N, 'base_wins': nb, 'variants': [dict(zip(['swap', 'wins', 'base_only', 'variant_only', 'z'], o)) for o in out]}
# commander without Rograkh being castable (cz=False): same deck
import random
from final_run import run
r = run('sans_Rograkh_castable', 1, N, 3, {'max_mull': 0}, 1, deck_spec=(d, False))
res['no_rograkh'] = r
json.dump(res, open('sensitivity.json', 'w'), indent=1)
print(json.dumps(res, indent=1))
