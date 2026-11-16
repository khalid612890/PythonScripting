// Drives the Autopsy 2.24 Forensic Browser (web UI) with Playwright to create the case,
// register both workstation images and capture GENUINE screenshots of the analysis views.
// Usage: NODE_PATH=$(npm root -g) node autopsy_drive.js
const {chromium} = require('playwright');
const ROOT = '/home/user/PythonScripting/TechNova_Forensics/';
const S = ROOT + 'screenshots/';
const BASE = 'http://localhost:9999/autopsy';
const step = process.argv[2] || 'explore';

async function forms(p) {
  return p.$$eval('input,select,textarea', es => es.map(e => `${e.tagName} name=${e.name} type=${e.type} value=${(e.value || '').slice(0, 60)}`).join('\n'));
}
async function text(p) { return (await p.content()).replace(/<script[\s\S]*?<\/script>/g, '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').slice(0, 900); }
async function submit(p) { await Promise.all([p.waitForLoadState('load'), p.click('input[type=image], input[type=submit]')]); await p.waitForTimeout(500); }

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: 1280, height: 850}, deviceScaleFactor: 2});
  if (step === 'case') {
    await p.goto(BASE + '?mod=0&view=1');
    await p.fill('input[name=case]', 'TechNova_IR_2026_014');
    await p.fill('[name=desc]', 'NovaLock ransomware incident - TechNova Solutions');
    const inv = await p.$$('input[name^=inv]'); await inv[0].fill('Forensic_Analyst');
    await p.screenshot({path: S + 'autopsy_01_new_case.png'});
    await submit(p);
    console.log(await text(p)); console.log(await forms(p));
  } else if (step === 'addimg') {
    const host = process.argv[3], img = process.argv[4];
    await p.goto(`${BASE}?mod=0&view=13&case=TechNova_IR_2026_014&inv=Forensic_Analyst&host=${host}`);
    await p.fill('input[name=img_path]', img);
    await p.check('input[name=imgtype][value=disk]');
    await p.check('input[name=sort][value="1"]');
    await p.screenshot({path: S + `autopsy_03_add_image_${host}.png`});
    await submit(p);
    console.log(await text(p)); console.log(await forms(p));
    // calculate MD5 on import if offered
    const md5 = await p.$('input[name=do_md5][value="2"]');
    if (md5) await md5.check();
    await p.screenshot({path: S + `autopsy_04_image_details_${host}.png`, fullPage: true});
    await submit(p);
    console.log('--- after add ---'); console.log(await text(p));
    await p.screenshot({path: S + `autopsy_05_image_added_${host}.png`, fullPage: true});
  } else if (step === 'analyse') {
    const host = process.argv[3];
    const ba = `case=TechNova_IR_2026_014&host=${host}&inv=Forensic_Analyst&vol=vol2`;
    const shot = async (n) => { await p.waitForTimeout(1500); await p.screenshot({path: S + `autopsy_${host}_${n}.png`}); };
    const clickIn = async (txt) => {
      for (const f of p.frames()) { const l = f.getByText(txt, {exact: false}).first(); if (await l.count()) { await l.click(); return true; } }
      return false; };
    // 1. File system details (fsstat in GUI)
    await p.goto(`${BASE}?mod=1&submod=7&${ba}`); await shot('10_fs_details');
    // 2. File analysis - browse to the user's Documents folder
    await p.goto(`${BASE}?mod=1&submod=2&${ba}`); await p.waitForTimeout(1500);
    await clickIn('Users/'); await p.waitForTimeout(800); await clickIn(host === 'WS01' ? 'jharris/' : 'mpatel/');
    await p.waitForTimeout(800); await clickIn('Documents/'); await shot('11_documents_encrypted');
    // 3. All deleted files
    await p.goto(`${BASE}?mod=1&submod=2&${ba}`); await p.waitForTimeout(1500);
    await clickIn('ALL DELETED FILES'); await shot('12_all_deleted_files');
    // 4. Metadata (istat) view of a deleted entry
    if (host === 'WS01') { await p.goto(`${BASE}?mod=1&submod=3&${ba}&meta=98`); await shot('13_meta_winupd_deleted');
      await p.goto(`${BASE}?mod=1&submod=3&${ba}&meta=100`); await shot('14_meta_tn_data_deleted'); }
    // 5. Keyword search for the ransomware marker
    await p.goto(`${BASE}?mod=1&submod=4&${ba}`); await p.waitForTimeout(1500);
    for (const f of p.frames()) { const i = await f.$('input[name=str]'); if (i) { await i.fill(host === 'WS01' ? 'cdn-update-sync' : 'NOVALOCK');
        await Promise.all([p.waitForTimeout(6000), f.click('input[type=image]')]); break; } }
    await shot('15_keyword_search');
  } else if (step === 'url') {
    await p.goto(BASE + process.argv[3]);
    if (process.argv[4]) await p.screenshot({path: S + process.argv[4], fullPage: true});
    console.log(await text(p)); console.log(await forms(p));
    const links = await p.$$eval('a,frame', es => es.map(e => (e.href || e.src)).filter(Boolean));
    console.log(links.join('\n'));
  }
  await b.close();
})();
