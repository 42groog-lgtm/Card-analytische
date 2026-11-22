import { Engine } from './engine.js';

const $ = (s) => document.querySelector(s);
const store = {
  get(k, d) { try { const v = localStorage.getItem('amb:' + k); return v == null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem('amb:' + k, JSON.stringify(v)); } catch { /* stockage indisponible */ } },
};

const engine = new Engine();
let data = null;
let activeScene = null;
let wakeLock = null;

// Clé de cache / URL d'une couche ou d'un effet (étape 4 : surcharge par fichier perso).
const keyOf = (item) => item.file;
const urlOf = (item) => item.file;

const status = (msg) => { $('#status').textContent = msg || ''; };

async function requestWake() {
  try {
    if ('wakeLock' in navigator && !wakeLock) {
      wakeLock = await navigator.wakeLock.request('screen');
      wakeLock.addEventListener('release', () => { wakeLock = null; });
    }
  } catch { /* refusé ou non supporté : l'écran pourra s'éteindre */ }
}
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') { requestWake(); if (engine.ctx && engine.ctx.state !== 'running') engine.ctx.resume().catch(() => {}); }
});

const levelsFor = (scene) => {
  const saved = store.get('levels:' + scene.id, {});
  return Object.fromEntries(scene.layers.map((l) => [l.id, saved[l.id] ?? l.volume ?? 0.7]));
};

function renderLayers(scene, missing = []) {
  const levels = levelsFor(scene);
  $('#scene-title').textContent = `${scene.icon ?? ''} ${scene.name}`.trim();
  const box = $('#layers');
  box.replaceChildren();
  for (const layer of scene.layers) {
    const row = document.createElement('div');
    row.className = 'layer' + (missing.includes(layer.id) ? ' missing' : '');
    row.innerHTML = '<span class="name"></span><input type="range" min="0" max="1" step="0.01"><span class="val"></span>';
    row.querySelector('.name').textContent = layer.name;
    const input = row.querySelector('input');
    const val = row.querySelector('.val');
    input.value = levels[layer.id];
    input.setAttribute('aria-label', 'Volume : ' + layer.name);
    val.textContent = Math.round(levels[layer.id] * 100);
    input.addEventListener('input', () => {
      const v = Number(input.value);
      levels[layer.id] = v;
      val.textContent = Math.round(v * 100);
      engine.setLayerLevel(layer.id, v);
      store.set('levels:' + scene.id, levels);
    });
    box.append(row);
  }
}

async function startScene(scene, btn) {
  await engine.unlock();
  requestWake();
  if (activeScene === scene.id && engine.current) return;
  activeScene = scene.id;
  document.querySelectorAll('.scene').forEach((b) => b.classList.toggle('active', b === btn));
  btn.classList.add('loading');
  status('Chargement…');
  renderLayers(scene);
  const effectKeys = data.effects.map(keyOf);
  const res = await engine.playScene(scene, levelsFor(scene), { keyOf, urlOf, extraKeys: effectKeys });
  btn.classList.remove('loading');
  if (!res) return; // remplacé par un appui plus récent
  if (res.missing.length) {
    renderLayers(scene, res.missing);
    status('Fichier introuvable pour : ' + scene.layers.filter((l) => res.missing.includes(l.id)).map((l) => l.name).join(', '));
  } else status('');
}

function stopAll() {
  engine.stop();
  activeScene = null;
  document.querySelectorAll('.scene').forEach((b) => b.classList.remove('active'));
  $('#scene-title').textContent = 'Arrêté';
  $('#layers').replaceChildren();
  status('');
}

async function showCredits() {
  const body = $('#credits-body');
  body.replaceChildren();
  const h = document.createElement('h2'); h.textContent = 'Crédits sonores'; body.append(h);
  try {
    const list = await (await fetch('credits.json')).json();
    if (!list.length) { const p = document.createElement('p'); p.textContent = 'Aucun son tiers pour le moment (sons de test générés localement).'; body.append(p); }
    const ul = document.createElement('ul');
    for (const c of list) {
      const li = document.createElement('li');
      li.append(`« ${c.title} » — ${c.author} — ${c.license} — `);
      const a = document.createElement('a'); a.href = c.url; a.textContent = c.url; a.target = '_blank'; a.rel = 'noopener';
      li.append(a, ` — ${c.scene} / ${c.layer}`);
      ul.append(li);
    }
    body.append(ul);
  } catch { const p = document.createElement('p'); p.textContent = 'Crédits indisponibles hors ligne.'; body.append(p); }
  $('#credits').showModal();
}

async function init() {
  data = await (await fetch('scenes.json')).json();

  const nav = $('#scenes');
  for (const scene of data.scenes) {
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'scene'; b.dataset.scene = scene.id;
    b.innerHTML = '<span class="ico"></span><span class="label"></span>';
    b.querySelector('.ico').textContent = scene.icon ?? '♪';
    b.querySelector('.label').textContent = scene.name;
    b.addEventListener('click', () => startScene(scene, b));
    nav.append(b);
  }

  const fx = $('#effects');
  for (const e of data.effects) {
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'effect'; b.dataset.effect = e.id; b.textContent = e.name;
    b.addEventListener('click', async () => {
      await engine.unlock();
      try { await engine.playEffect(keyOf(e), urlOf(e), e.volume ?? 0.9); }
      catch (err) { console.warn(err); status('Effet introuvable : ' + e.name); }
    });
    fx.append(b);
  }

  const master = $('#master');
  const m = store.get('master', 0.8);
  master.value = m; engine.masterLevel = m;
  master.addEventListener('input', () => { const v = Number(master.value); engine.setMaster(v); store.set('master', v); });
  $('#stop').addEventListener('click', stopAll);
  $('#credits-btn').addEventListener('click', showCredits);
  $('#credits-close').addEventListener('click', () => $('#credits').close());

  // Aide au test automatisé
  window.__amb = { engine, get active() { return activeScene; } };
}

init().catch((e) => { console.error(e); status('Erreur de démarrage : ' + e.message); });
