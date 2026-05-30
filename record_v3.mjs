import pkg from '/opt/node22/lib/node_modules/playwright/index.js';
const { chromium } = pkg;
import { fileURLToPath } from 'url';
import path from 'path';
import fs from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const htmlFile = path.join(__dirname, 'tiktok_viral_v3.html');
const outDir   = path.join(__dirname, 'video_out_v3');
const RECORD_MS = 72_000;

if (!fs.existsSync(outDir)) fs.mkdirSync(outDir);

console.log('Launching browser…');
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 390, height: 844 },
  recordVideo: { dir: outDir, size: { width: 390, height: 844 } },
});

const page = await context.newPage();
await page.goto('file://' + htmlFile);
console.log(`Recording ${RECORD_MS/1000}s…`);
await page.waitForTimeout(RECORD_MS);

const video = await page.video();
await context.close();
await browser.close();

const webmPath = await video.path();
const dest = path.join(__dirname, 'sublimontes_v3.webm');
fs.copyFileSync(webmPath, dest);
console.log('Done:', dest);
