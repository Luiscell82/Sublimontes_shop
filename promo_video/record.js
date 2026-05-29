const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const FFMPEG = '/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2';
const HTML_PATH = path.resolve(__dirname, 'promo_arlo.html');
const OUT_DIR = __dirname;
const WEBM_OUT = path.join(OUT_DIR, 'promo_arlo.webm');
const MP4_OUT  = path.join(OUT_DIR, 'promo_arlo.mp4');

(async () => {
  console.log('Iniciando grabación...');

  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    recordVideo: {
      dir: OUT_DIR,
      size: { width: 1920, height: 1080 },
    },
  });

  const page = await context.newPage();
  await page.goto(`file://${HTML_PATH}`);

  console.log('Grabando 61 segundos...');
  await page.waitForTimeout(61000);

  await context.close();
  await browser.close();

  // Playwright names the file with a random UUID — find it
  const files = fs.readdirSync(OUT_DIR).filter(f => f.endsWith('.webm') && f !== 'promo_arlo.webm');
  if (files.length === 0) { console.error('No se encontró el .webm'); process.exit(1); }
  const rawWebm = path.join(OUT_DIR, files[0]);
  fs.renameSync(rawWebm, WEBM_OUT);
  console.log(`WebM guardado: ${WEBM_OUT}`);

  console.log('Convirtiendo a MP4...');
  execSync(
    `${FFMPEG} -y -i "${WEBM_OUT}" -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p "${MP4_OUT}"`,
    { stdio: 'inherit' }
  );

  console.log(`\n✅ Video listo: ${MP4_OUT}`);
  fs.unlinkSync(WEBM_OUT);
})();
