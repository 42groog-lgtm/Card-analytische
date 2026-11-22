// Moteur audio : Web Audio, vrais fichiers, boucles sans coupure, fondu enchaîné.

const CURVE_STEPS = 64;
const fadeInCurve = Float32Array.from({ length: CURVE_STEPS }, (_, i) => Math.sin((i / (CURVE_STEPS - 1)) * Math.PI / 2));
const fadeOutCurve = Float32Array.from({ length: CURVE_STEPS }, (_, i) => Math.cos((i / (CURVE_STEPS - 1)) * Math.PI / 2));

/** Curseur linéaire 0..1 -> gain perceptif. */
export const toGain = (v) => v * v;

/**
 * Rend un buffer bouclable : la fin (F échantillons) est fondue dans le début.
 * Le buffer résultant fait N - F échantillons, et sa fin enchaîne sans saut avec son début.
 */
export function makeLoopable(ctx, buf, fadeSec) {
  const N = buf.length;
  const F = Math.min(Math.floor(fadeSec * buf.sampleRate), Math.floor(N / 3));
  if (F <= 0) return buf;
  const out = ctx.createBuffer(buf.numberOfChannels, N - F, buf.sampleRate);
  for (let ch = 0; ch < buf.numberOfChannels; ch++) {
    const src = buf.getChannelData(ch);
    const dst = out.getChannelData(ch);
    for (let i = 0; i < F; i++) {
      const t = (i / F) * Math.PI / 2;
      dst[i] = src[i] * Math.sin(t) + src[N - F + i] * Math.cos(t);
    }
    dst.set(src.subarray(F, N - F), F);
  }
  return out;
}

// Petit WAV silencieux, joué en boucle dans un <audio> pour passer outre le mode silencieux iOS.
function silentWavUrl() {
  const rate = 8000, n = rate; // 1 s
  const buf = new ArrayBuffer(44 + n);
  const v = new DataView(buf);
  const w = (o, s) => [...s].forEach((c, i) => v.setUint8(o + i, c.charCodeAt(0)));
  w(0, 'RIFF'); v.setUint32(4, 36 + n, true); w(8, 'WAVEfmt ');
  v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true);
  v.setUint32(24, rate, true); v.setUint32(28, rate, true); v.setUint16(32, 1, true); v.setUint16(34, 8, true);
  w(36, 'data'); v.setUint32(40, n, true);
  new Uint8Array(buf, 44).fill(128);
  return URL.createObjectURL(new Blob([buf], { type: 'audio/wav' }));
}

export class Engine {
  constructor({ fetchSource } = {}) {
    this.ctx = null;
    this.master = null;
    this.masterLevel = 0.8;
    this.fadeTime = 2.5;
    this.raw = new Map();      // clé -> AudioBuffer décodé (non bouclé)
    this.loopable = new Map(); // clé+fade -> AudioBuffer bouclable
    this.current = null;       // { sceneId, bus, layers: {id: {gain, src}} }
    this.token = 0;
    this.fetchSource = fetchSource || (async (url) => {
      const r = await fetch(url);
      if (!r.ok) throw new Error(`HTTP ${r.status} pour ${url}`);
      return r.arrayBuffer();
    });
    this.silentEl = null;
  }

  /** À appeler dans un geste utilisateur (toucher). Idempotent. */
  async unlock() {
    if (!this.ctx) {
      const AC = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AC({ latencyHint: 'playback' });
      const comp = this.ctx.createDynamicsCompressor();
      comp.threshold.value = -10; comp.knee.value = 12; comp.ratio.value = 4;
      comp.attack.value = 0.01; comp.release.value = 0.3;
      this.master = this.ctx.createGain();
      this.master.gain.value = toGain(this.masterLevel);
      this.master.connect(comp).connect(this.ctx.destination);
      this.ctx.addEventListener('statechange', () => this.onState?.(this.ctx.state));
    }
    try { if (navigator.audioSession) navigator.audioSession.type = 'playback'; } catch { /* non supporté */ }
    if (!this.silentEl) {
      const a = new Audio(silentWavUrl());
      a.loop = true; a.preload = 'auto'; a.setAttribute('playsinline', '');
      this.silentEl = a;
    }
    this.silentEl.play().catch(() => {});
    if (this.ctx.state !== 'running') await this.ctx.resume().catch(() => {});
    return this.ctx.state;
  }

  async load(key, url) {
    if (this.raw.has(key)) return this.raw.get(key);
    const data = await this.fetchSource(url, key);
    const buf = await this.ctx.decodeAudioData(data.slice(0));
    this.raw.set(key, buf);
    return buf;
  }

  /** Oublie le cache d'une clé (après remplacement par un fichier perso). */
  invalidate(key) {
    this.raw.delete(key);
    for (const k of [...this.loopable.keys()]) if (k.startsWith(key + '|')) this.loopable.delete(k);
  }

  /** Libère les buffers qui ne servent ni à la scène courante ni aux effets. */
  retain(keys) {
    const keep = new Set(keys);
    for (const k of [...this.raw.keys()]) if (!keep.has(k)) this.raw.delete(k);
    for (const k of [...this.loopable.keys()]) if (!keep.has(k.split('|')[0])) this.loopable.delete(k);
  }

  getLoopable(key, fade) {
    const ck = `${key}|${fade}`;
    if (!this.loopable.has(ck)) this.loopable.set(ck, makeLoopable(this.ctx, this.raw.get(key), fade));
    return this.loopable.get(ck);
  }

  setMaster(v) {
    this.masterLevel = v;
    if (this.master) this.master.gain.setTargetAtTime(toGain(v), this.ctx.currentTime, 0.05);
  }

  setLayerLevel(layerId, v) {
    const l = this.current?.layers[layerId];
    if (l) l.gain.gain.setTargetAtTime(toGain(v), this.ctx.currentTime, 0.05);
  }

  /**
   * Lance une scène avec fondu enchaîné depuis la précédente.
   * scene: {id, layers:[{id,file,loopFade}]}, levels: {layerId: 0..1}
   * keyOf(layer) -> clé de cache ; urlOf(layer) -> URL du fichier.
   * Retourne { missing: [layerId...] } ou null si annulé par un appel plus récent.
   */
  async playScene(scene, levels, { keyOf, urlOf, extraKeys = [] }) {
    const token = ++this.token;
    const missing = [];
    await Promise.all(scene.layers.map(async (layer) => {
      try { await this.load(keyOf(layer), urlOf(layer)); }
      catch (e) { console.warn('Chargement impossible', layer.id, e); missing.push(layer.id); }
    }));
    if (token !== this.token) return null;

    const ctx = this.ctx;
    const t = ctx.currentTime;
    const bus = ctx.createGain();
    bus.gain.value = 0;
    bus.connect(this.master);
    const layers = {};
    for (const layer of scene.layers) {
      if (missing.includes(layer.id)) continue;
      const key = keyOf(layer);
      const buffer = this.getLoopable(key, layer.loopFade ?? 1.5);
      const gain = ctx.createGain();
      gain.gain.value = toGain(levels[layer.id] ?? layer.volume ?? 0.7);
      const src = ctx.createBufferSource();
      src.buffer = buffer;
      src.loop = true;
      src.connect(gain).connect(bus);
      src.start(0, Math.random() * buffer.duration);
      layers[layer.id] = { gain, src };
    }
    bus.gain.setValueCurveAtTime(fadeInCurve, t, this.fadeTime);

    const old = this.current;
    this.current = { sceneId: scene.id, bus, layers };
    if (old) this.fadeOutAndDispose(old, this.fadeTime);

    this.retain([...scene.layers.map(keyOf), ...extraKeys]);
    return { missing };
  }

  fadeOutAndDispose(sc, time) {
    const t = this.ctx.currentTime;
    sc.bus.gain.cancelScheduledValues(t);
    sc.bus.gain.setValueAtTime(sc.bus.gain.value, t);
    sc.bus.gain.setTargetAtTime(0, t, time / 4);
    setTimeout(() => {
      for (const l of Object.values(sc.layers)) { try { l.src.stop(); } catch { /* déjà arrêté */ } }
      sc.bus.disconnect();
    }, time * 1000 + 300);
  }

  stop(time = 0.6) {
    this.token++;
    if (this.current) { this.fadeOutAndDispose(this.current, time); this.current = null; }
  }

  async playEffect(key, url, level = 0.9) {
    await this.load(key, url);
    const ctx = this.ctx;
    const g = ctx.createGain();
    g.gain.value = toGain(level);
    const src = ctx.createBufferSource();
    src.buffer = this.raw.get(key);
    src.connect(g).connect(this.master);
    src.start();
    src.onended = () => g.disconnect();
  }

  get activeLayerCount() { return this.current ? Object.keys(this.current.layers).length : 0; }
}
