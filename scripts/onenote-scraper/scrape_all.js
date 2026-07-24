const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const URL = process.argv[2];
const OUT_DIR = process.argv[3] || path.join(__dirname, 'output');
const PROFILE_DIR = path.join(__dirname, 'edge-profile');

function sanitize(name) {
  return name.trim().replace(/[\\/:*?"<>|]/g, '-').replace(/\s+/g, ' ').trim();
}

(async () => {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const context = await chromium.launchPersistentContext(PROFILE_DIR, {
    channel: 'msedge',
    headless: false,
    viewport: { width: 1400, height: 900 },
  });
  const page = context.pages()[0] || (await context.newPage());
  await page.goto(URL, { waitUntil: 'domcontentloaded', timeout: 60000 }).catch(() => {});
  await page.waitForTimeout(8000);

  const frame = page.frames().find(fr => /onenote\.officeapps\.live\.com\/o\/onenoteframe/i.test(fr.url()));
  if (!frame) {
    console.log('No se encontró el frame de OneNote');
    await context.close();
    return;
  }

  async function getEditorText() {
    return frame.evaluate(() => {
      const el = document.getElementById('EditorContainer');
      return el ? el.innerText : '';
    });
  }

  const manifest = [];
  const sectionCount = await frame.locator('#NavPaneSectionList [role="treeitem"]').count();
  console.log(`Secciones encontradas: ${sectionCount}`);

  for (let s = 0; s < sectionCount; s++) {
    const sectionLoc = frame.locator('#NavPaneSectionList [role="treeitem"]').nth(s);
    const sectionName = (await sectionLoc.textContent() || `seccion-${s}`).trim();
    console.log(`\n== Sección [${s}]: ${sectionName} ==`);
    await sectionLoc.click();
    await page.waitForTimeout(2500);

    const pageCount = await frame.locator('#PageList [role="button"].navItem').count();
    console.log(`  Páginas: ${pageCount}`);

    const sectionDir = path.join(OUT_DIR, sanitize(sectionName));
    fs.mkdirSync(sectionDir, { recursive: true });

    for (let p = 0; p < pageCount; p++) {
      const pageLoc = frame.locator('#PageList [role="button"].navItem').nth(p);
      const pageName = (await pageLoc.textContent() || `pagina-${p}`).trim();
      await pageLoc.click({ force: true });

      let text = '';
      for (let attempt = 0; attempt < 12; attempt++) {
        await page.waitForTimeout(600);
        text = await getEditorText();
        const firstLine = (text.split('\n')[0] || '').trim().toLowerCase();
        const expected = pageName.toLowerCase().slice(0, Math.min(6, pageName.length));
        if (firstLine.startsWith(expected)) break;
      }

      const fileName = sanitize(pageName) + '.md';
      const filePath = path.join(sectionDir, fileName);
      const frontmatter = `---\nseccion: ${sectionName}\npagina: ${pageName}\ncapturado: ${new Date().toISOString()}\nfuente: OneNote "Cluster-OSS" (Norberto Nunez)\n---\n\n`;
      fs.writeFileSync(filePath, frontmatter + text, 'utf-8');
      console.log(`  [ok] ${pageName} -> ${path.relative(OUT_DIR, filePath)} (${text.length} chars)`);
      manifest.push({ seccion: sectionName, pagina: pageName, archivo: path.relative(OUT_DIR, filePath).replace(/\\/g, '/'), chars: text.length });
    }
  }

  fs.writeFileSync(path.join(OUT_DIR, 'manifest.json'), JSON.stringify(manifest, null, 2), 'utf-8');
  console.log('\nListo. Manifest:', path.join(OUT_DIR, 'manifest.json'));
  console.log(`Total páginas capturadas: ${manifest.length}`);

  await context.close();
})();
