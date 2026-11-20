"""Validation of t1sim on decks whose turn-1 win probability can be computed exactly."""
import sys, time
from math import comb
from itertools import product
import t1sim

O, C, W, E, L, P, D = "Thassa's Oracle", 'Demonic Consultation', 'Worldly Tutor', 'Elvish Spirit Guide', 'City of Brass', 'Lotus Petal', 'Dark Ritual'
F = 'Silas Renn, Seeker Adept'   # blank card

def deck_of(cnt):
    d = []
    for k, v in cnt.items(): d += [k] * v
    assert len(d) == 99, len(d)
    return d

def exact_T1(cnt):
    """win iff Oracle & Consult & (min(lands,1) + petals >= 3) in 8 cards"""
    keys = [O, C, L, P]; rest = 99 - sum(cnt[k] for k in keys)
    tot = 0
    for o, c in product(range(min(cnt[O], 8) + 1), range(min(cnt[C], 8) + 1)):
        for l in range(9):
            for p in range(9):
                k = o + c + l + p
                if k > 8: continue
                ways = comb(cnt[O], o) * comb(cnt[C], c) * comb(cnt[L], l) * comb(cnt[P], p) * comb(rest, 8 - k)
                if o and c and min(l, 1) + p >= 3: tot += ways
    return tot / comb(99, 8)

def exact_T3(cnt):
    keys = [O, C, W, E, L, P]; rest = 99 - sum(cnt[k] for k in keys)
    tot = 0
    for o, c, w, e in product(*[range(min(cnt[x], 7) + 1) for x in (O, C, W, E)]):
        for l in range(8):
            for p in range(8):
                k = o + c + w + e + l + p
                if k > 7: continue
                ways7 = comb(cnt[O], o) * comb(cnt[C], c) * comb(cnt[W], w) * comb(cnt[E], e) * comb(cnt[L], l) * comb(cnt[P], p) * comb(rest, 7 - k)
                left = {O: cnt[O] - o, C: cnt[C] - c, L: cnt[L] - l, P: cnt[P] - p}
                nleft = 92
                a7 = min(l, 1) + p
                if o and c:
                    # 8th card random: win iff mana with 8th >= 3
                    pr = 0
                    if a7 >= 3: pr = 1
                    elif a7 == 2:
                        pr = (left[P] + (left[L] if l == 0 else 0)) / nleft
                    tot += ways7 * pr
                elif (not o) and c and w and e:
                    tot += ways7 * (1 if a7 >= 3 else 0)
                elif (not o) and c:
                    tot += ways7 * (left[O] / nleft if a7 >= 3 else 0)
                elif o and not c:
                    tot += ways7 * (left[C] / nleft if a7 >= 3 else 0)
    return tot / comb(99, 7)

DT = 'Demonic Tutor'
def exact_T4(cnt):
    """Oracle, Consult, Demonic Tutor (1B, any card to hand); mana sources: 1 land drop + petals"""
    keys = [O, C, DT, L, P]; rest = 99 - sum(cnt[k] for k in keys)
    tot = 0
    for o, c, d in product(*[range(min(cnt[x], 8) + 1) for x in (O, C, DT)]):
        for l in range(9):
            for p in range(9):
                k = o + c + d + l + p
                if k > 8: continue
                ways = comb(cnt[O], o) * comb(cnt[C], c) * comb(cnt[DT], d) * comb(cnt[L], l) * comb(cnt[P], p) * comb(rest, 8 - k)
                a = min(l, 1) + p
                need = None
                if o and c: need = 3
                elif (o or c) and d: need = 5
                elif d >= 2: need = 7
                if need is not None and a >= need: tot += ways
    return tot / comb(99, 8)

def sim(deck, n, seed):
    t0 = time.time()
    w, n = t1sim.run(deck, 1, n, seed, max_mull=0)
    lo, hi = t1sim.wilson(w, n)
    return w / n, lo, hi, time.time() - t0

if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100000
    tests = {
        'T1 10 Oracle + 10 Consult, 30 City of Brass, 10 Lotus Petal': ({O: 10, C: 10, L: 30, P: 10, F: 39}, exact_T1),
        'T2 = T1 + 5 Dark Ritual (ne doit rien changer : BBB ne paie pas UU)': ({O: 10, C: 10, L: 30, P: 10, D: 5, F: 34}, exact_T1),
        'T4 10 Oracle + 10 Consult + 10 Demonic Tutor, 30 City, 10 Petal': ({O: 10, C: 10, DT: 10, L: 30, P: 10, F: 29}, exact_T4),
        'T3 = T1 + 6 Worldly Tutor + 6 Elvish Spirit Guide (entretien)': ({O: 10, C: 10, W: 6, E: 6, L: 30, P: 10, F: 27}, exact_T3),
    }
    for name, (cnt, ex) in tests.items():
        e = ex(cnt)
        p, lo, hi, dt = sim(deck_of(cnt), n, 2026)
        ok = lo <= e <= hi
        print(f'{name}\n   exact = {e:.5f}   sim = {p:.5f}  IC95 [{lo:.5f}, {hi:.5f}]  n={n}  {"OK" if ok else "ECART"}  ({dt:.0f}s)')
