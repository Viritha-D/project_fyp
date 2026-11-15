// Usage: node app/tools/lfs_proof/drive_app.js <port> <precomputed|live>  (needs Playwright with Chromium)
const { chromium } = require('playwright');
const [port, mode] = process.argv.slice(2);
const LIVE_QUERIES = [
  'A differential evolution variant with a new constraint handling method for real-valued problems that have many equality and inequality constraints and a very small feasible region.',
  'uni course timetabling: rooms, periods, curricula, soft constraints for student clashes. what instance sets are used in papers?',
  'what is a good recipe for banana bread',
];
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(String(e)));
  await p.goto(`http://localhost:${port}`, { waitUntil: 'networkidle' }); await p.waitForTimeout(3000);
  await p.getByText('Gallery: precomputed examples').waitFor({ timeout: 120000 });
  const ids = ['Q01', 'Q11', 'Q21', 'Q31', 'Q41', 'Q51']; let opened = 0;
  for (const id of ids) {
    const s = p.locator('[data-testid="stExpander"] summary', { hasText: id + ' [' }).first();
    const exp = p.locator('[data-testid="stExpander"]', { hasText: id + ' [' }).first();
    let txt = '';
    for (let a = 0; a < 3 && !txt.includes('1.'); a++) {
      if (a === 0 || !(await exp.locator('details[open]').count())) { await s.scrollIntoViewIfNeeded(); await s.click(); }
      await p.waitForTimeout(1500); txt = await exp.innerText();
    }
    if (txt.includes('1.')) opened++; else console.log('gallery item without content:', id);
  }
  console.log(`gallery items opened with content: ${opened}/6`);
  if (mode === 'live') {
    for (const q of LIVE_QUERIES) {
      await p.locator('textarea').first().fill(q);
      await p.getByRole('button', { name: 'Recommend' }).click();
      const spin = p.getByText('Ranking with the frozen system');
      await spin.waitFor({ state: 'visible', timeout: 15000 }).catch(() => {});
      await spin.waitFor({ state: 'hidden', timeout: 240000 });
      await p.waitForTimeout(1500);
      const body = await p.innerText('body');
      console.log('live query answered:', JSON.stringify(q.slice(0, 40)),
        '| answer shown:', body.includes('Produced by v2.3'), '| low-confidence banner:', body.includes('Low confidence.'),
        '| stored:', (body.match(/Stored as unverified record \S+/) || ['no'])[0], '| out-of-scope:', body.includes('does not look like an optimisation problem'),
        '| timeout/error:', /timed out|took longer|Error/i.test(body));
    }
  }
  const body = await p.innerText('body');
  console.log('page exceptions:', errs.length, '| Traceback on page:', body.includes('Traceback'), '| mode line:', (body.match(/Mode: \w+/) || [''])[0]);
  await b.close();
})();
