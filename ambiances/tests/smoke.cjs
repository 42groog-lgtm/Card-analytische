// Test de fumée : node ambiances/tests/smoke.cjs
// Vérifie : chargement sans erreur, chaque scène démarre, signal non nul en sortie, effets, arrêt, jonction de boucle.
// NE VÉRIFIE PAS le rendu sonore (impossible à écouter ici).
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const root = path.resolve(__dirname, '..');
const port = 8765 + Math.floor(Math.random() * 500);
const scenesData = JSON.parse(fs.readFileSync(path.join(root, 'scenes.json'), 'utf8'));
let failed = 0;
const check = (ok, msg) => { console.log((ok ? 'OK   ' : 'ÉCHEC') + ' ' + msg); if (!ok) failed++; };

(async () => {
  const server = spawn('python3', ['-m', 'http.server', String(port), '--directory', root], { stdio: 'ignore' });
  await new Promise((r) => setTimeout(r, 800));
  const browser = await chromium.launch({ args: ['--autoplay-policy=no-user-gesture-required'] });
  const page = await (await browser.newContext({ viewport: { width: 1180, height: 820 }, hasTouch: true })).newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  page.on('console', (m) => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
  page.on('requestfailed', (r) => errors.push('requestfailed: ' + r.url()));
  page.on('response', (r) => { if (r.status() >= 400) errors.push(`HTTP ${r.status()}: ${r.url()}`); });

  try {
    await page.goto(`http://localhost:${port}/`);
    await page.waitForSelector('.scene');
    const nScenes = await page.locator('.scene').count();
    check(nScenes === scenesData.scenes.length, `${nScenes} boutons de scène affichés`);
    check((await page.locator('.effect').count()) === scenesData.effects.length, 'boutons d\'effets affichés');

    for (let i = 0; i < scenesData.scenes.length; i++) {
      const sc = scenesData.scenes[i];
      await page.locator('.scene').nth(i).click();
      await page.waitForFunction((n) => window.__amb.engine.activeLayerCount === n && !document.querySelector('.scene.loading'), sc.layers.length, { timeout: 15000 });
      check(true, `scène « ${sc.name} » : ${sc.layers.length} couches en lecture`);
      check((await page.locator('#layers input[type=range]').count()) === sc.layers.length, `  ${sc.layers.length} curseurs affichés`);
      const state = await page.evaluate(() => window.__amb.engine.ctx.state);
      check(state === 'running', `  AudioContext : ${state}`);
      // Signal en sortie (après le fondu d'entrée)
      await page.waitForTimeout(3000);
      const peak = await page.evaluate(async () => {
        const e = window.__amb.engine; const an = e.ctx.createAnalyser(); e.master.connect(an);
        const buf = new Float32Array(an.fftSize); let max = 0;
        for (let k = 0; k < 10; k++) { await new Promise((r) => setTimeout(r, 50)); an.getFloatTimeDomainData(buf); for (const v of buf) max = Math.max(max, Math.abs(v)); }
        e.master.disconnect(an); return max;
      });
      check(peak > 0.005, `  signal non nul en sortie (crête ${peak.toFixed(3)})`);
      // Curseur : mettre une couche à 0 ne doit pas planter
      await page.locator('#layers input[type=range]').first().fill('0');
    }

    if (scenesData.effects.length) {
      await page.locator('.effect').first().click();
      await page.waitForTimeout(300);
      check(true, 'effet déclenché sans erreur');
    }

    await page.click('#stop');
    await page.waitForTimeout(500);
    check((await page.evaluate(() => window.__amb.engine.activeLayerCount)) === 0, 'Arrêt : plus de couche active');

    // Jonction de boucle : la saut entre dernier et premier échantillon doit être faible.
    const seam = await page.evaluate(async () => {
      const { makeLoopable } = await import('./js/engine.js');
      const e = window.__amb.engine;
      const buf = e.ctx.createBuffer(1, 44100 * 6, 44100); // rampe 0 -> 1 : coupure maximale sans fondu
      const r = buf.getChannelData(0); for (let i = 0; i < r.length; i++) r[i] = i / (r.length - 1);
      const jump = (b) => { const d = b.getChannelData(0); return Math.abs(d[d.length - 1] - d[0]); };
      const loop = makeLoopable(e.ctx, buf, 2);
      const d = loop.getChannelData(0);
      let maxStep = 0; for (let i = 1; i < 20000; i++) maxStep = Math.max(maxStep, Math.abs(d[i] - d[i - 1]));
      return { before: jump(buf), after: jump(loop), maxStep, len: [buf.length, loop.length] };
    });
    check(seam.before > 0.9 && seam.after < 0.05, `jonction de boucle : saut ${seam.before.toFixed(3)} -> ${seam.after.toFixed(3)} (pas max ${seam.maxStep.toFixed(3)})`);
  } catch (e) {
    check(false, 'exception : ' + e.message);
  }

  check(errors.length === 0, 'aucune erreur console / réseau' + (errors.length ? '\n  ' + errors.join('\n  ') : ''));
  await page.screenshot({ path: path.join(process.env.SHOT_DIR || '/tmp', 'ambiances.png') });
  await browser.close();
  server.kill();
  console.log(failed ? `\n${failed} échec(s)` : '\nTout passe');
  process.exit(failed ? 1 : 0);
})();
