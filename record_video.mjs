import pkg from '/opt/node22/lib/node_modules/playwright/index.js';
const { chromium } = pkg;
import { fileURLToPath } from 'url';
import path from 'path';
import fs from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const htmlFile = path.join(__dirname, 'tiktok_viral.html');
const outDir  = path.join(__dirname, 'video_out');
const finalMp4 = path.join(__dirname, 'sublimontes_tiktok.mp4');

// Total video duration in ms (match sum of scene durations + a bit extra)
const RECORD_MS = 70_000;

if (!fs.existsSync(outDir)) fs.mkdirSync(outDir);

console.log('Launching browser…');
const browser = await chromium.launch({ headless: true });

const context = await browser.newContext({
  viewport: { width: 390, height: 844 },
  recordVideo: {
    dir: outDir,
    size: { width: 390, height: 844 },
  },
});

const page = await context.newPage();
await page.goto('file://' + htmlFile);

console.log(`Recording for ${RECORD_MS / 1000}s…`);
await page.waitForTimeout(RECORD_MS);

console.log('Stopping recording…');
const video = await page.video();
await context.close();
await browser.close();

// Playwright saves the webm, rename/move it
const webmPath = await video.path();
console.log('Raw video at:', webmPath);

// Copy to project root
fs.copyFileSync(webmPath, finalMp4.replace('.mp4', '.webm'));
console.log('Saved:', finalMp4.replace('.mp4', '.webm'));
console.log('Done!');
