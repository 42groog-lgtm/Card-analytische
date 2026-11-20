"""plan_de_jeu.md = plan_de_jeu_base.md + one simulated winning game per pattern (examples.json)."""
import json
from t1sim import S
ex = json.load(open('examples.json'))

def fr(a, led):
    t = a[0]
    if t == 'cmdr': s = 'Lancer Rograkh depuis la zone de commandement'
    elif t == 'land': s = f'Jouer {a[1]} (mana {a[2] if a[2] != "A" else "de n’importe quelle couleur"})'
    elif t == 'fetch': s = f'Jouer {a[1]}, aller chercher {a[2]} (mana {a[3]})'
    elif t == 'rock': s = f'Lancer {a[1]}'
    elif t == 'freecre': s = f'Lancer {a[1]} (0)'
    elif t == 'chrome': s = f'Lancer Chrome Mox en exilant {a[2]} (mana {a[3]})'
    elif t == 'diamond': s = f'Lancer Mox Diamond en défaussant {a[2]}'
    elif t == 'drumtap': s = 'Engager Springleaf Drum en engageant une créature'
    elif t == 'opaltap': s = 'Engager Mox Opal (3 artefacts)'
    elif t == 'ambertap': s = f'Engager Mox Amber ({a[1]})'
    elif t == 'treastap': s = 'Sacrifier le Trésor'
    elif t == 'caverns': s = 'Engager Gemstone Caverns'
    elif t == 'guide': s = f'Exiler {a[1]} de la main'
    elif t in ('tutor', 'toptutor', 'transmute'):
        how = {'tutor': 'en main', 'toptutor': 'sur la bibliothèque', 'transmute': 'en main (transmutation)'}[t]
        s = f'Lancer {a[1]} : chercher {a[2]} {how}'
    elif t == 'beseech': s = f'Lancer Beseech the Mirror{" avec bargain" if a[3] else ""} : chercher {a[2]}' + (' et la lancer gratuitement' if a[3] else '')
    elif t == 'consult': s = f'Lancer {a[1]} (nommer une carte absente du deck pour Consultation) : bibliothèque vide'
    elif t == 'oracle': s = 'Lancer Thassa’s Oracle'
    elif t == 'jace': s = 'Lancer Jace, Wielder of Mysteries (puis +1 : pioche avec bibliothèque vide)'
    elif t == 'labman': s = 'Lancer Laboratory Maniac'
    elif t == 'adnaus': s = 'Lancer Ad Nauseam'
    elif t == 'wheel': s = f'Lancer {a[1]}'
    elif t == 'cycle': s = f'Cycler {a[1]} (2 PV)'
    else: s = f'Lancer {a[1]}'
    if led: s += ', en sacrifiant Lion’s Eye Diamond pendant le paiement'
    return s

pats = [('Combinaison directe', lambda acts: len(acts) <= 7 and any(a[0] == 'oracle' for a in acts)),
        ('Rograkh + Culling the Weak + tutor', lambda acts: any(len(a) > 1 and a[1] == 'Culling the Weak' for a in acts) and any(a[0] in ('tutor', 'toptutor') for a in acts) and not any(a[0] in ('adnaus', 'wheel') for a in acts)),
        ('Ad Nauseam', lambda acts: any(a[0] == 'adnaus' for a in acts) and len(acts) < 24),
        ('Beseech the Mirror avec bargain', lambda acts: any(a[0] == 'beseech' and a[3] for a in acts) and not any(a[0] in ('adnaus',) for a in acts)),
        ('Jace ou Laboratory Maniac', lambda acts: any(a[0] in ('jace', 'labman') for a in acts) and not any(a[0] == 'adnaus' for a in acts))]
out = [open('plan_de_jeu_base.md').read(), '\n## Exemples tirés de la simulation (place 1, sans mulligan)\n',
       'Chaque exemple est une partie gagnée par le simulateur, avec la main réelle. Les étapes « cartes révélées » indiquent les pioches inconnues au moment de la décision.\n']
used = set()
for name, f in pats:
    for i, e in enumerate(ex):
        if i in used: continue
        acts = [tuple(a) for st in e['log'] if st[0] == 'plan' for a in st[1]]
        if f(acts):
            used.add(i)
            out.append(f'### {name}\n')
            out.append(f'Main de départ : {", ".join(e["hand7"])} ; pioche du tour : {e["draw"]}.\n')
            k = 1
            for st in e['log']:
                if st[0] == 'upkeep': out.append(f'{k}. Entretien : {st[1]}'); k += 1
                elif st[0] == 'plan':
                    for a, l in zip(st[1], st[2]):
                        out.append(f'{k}. {fr(a, l)}'); k += 1
                elif st[0] == 'reveal':
                    out.append(f'   - cartes révélées : {", ".join(st[1]) if st[1] else "aucune utile"}')
            out.append('\nLes trois adversaires perdent la partie.\n')
            break
open('plan_de_jeu.md', 'w').write('\n'.join(out) + '\n')
print('ok', len(used), 'exemples')
