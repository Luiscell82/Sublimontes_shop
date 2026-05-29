/**
 * Generates photo1.jpg, photo2.jpg, photo3.jpg
 * using Playwright to render HTML product mockups.
 */
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path');
const OUT = __dirname;
const W = 900, H = 1080;

const scenes = [
  // ── PHOTO 1: Box front ─────────────────────────────────
  { file: 'photo1.jpg', html: `
<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:${W}px;height:${H}px;overflow:hidden;
  background:radial-gradient(ellipse at 60% 40%,#2a1f1a 0%,#0f0a08 100%);
  font-family:'Arial',sans-serif;display:flex;align-items:center;justify-content:center;}
/* granite countertop */
body::before{content:'';position:absolute;inset:0;
  background:
    radial-gradient(ellipse at 30% 80%,rgba(140,120,100,0.25) 0%,transparent 50%),
    radial-gradient(ellipse at 70% 90%,rgba(100,90,80,0.3) 0%,transparent 40%),
    repeating-linear-gradient(45deg,transparent,transparent 2px,rgba(255,255,255,0.01) 2px,rgba(255,255,255,0.01) 4px);
}
.countertop{position:absolute;bottom:0;left:0;right:0;height:320px;
  background:linear-gradient(180deg,transparent 0%,rgba(80,65,55,0.4) 100%);
  border-top:1px solid rgba(255,255,255,0.05);}
.box{position:relative;width:320px;height:540px;
  background:linear-gradient(160deg,#f8f8f8 0%,#eeeeee 50%,#f5f5f5 100%);
  border-radius:12px;
  box-shadow:
    0 40px 80px rgba(0,0,0,0.7),
    0 10px 30px rgba(0,0,0,0.5),
    inset 1px 1px 0 rgba(255,255,255,0.8);
  display:flex;flex-direction:column;align-items:center;
  padding:28px 24px 20px;overflow:hidden;}
.box::before{content:'';position:absolute;top:0;left:0;right:0;height:60%;
  background:linear-gradient(180deg,rgba(255,255,255,0.4) 0%,transparent 100%);}
.box-top{width:100%;display:flex;justify-content:space-between;align-items:flex-start;z-index:1;}
.arlo-logo{font-size:36px;font-weight:900;color:#1a2a4a;letter-spacing:-1px;font-style:italic;}
.badge-2k{width:52px;height:52px;background:linear-gradient(135deg,#0057cc,#0099ff);
  border-radius:10px;display:flex;align-items:center;justify-content:center;
  font-size:22px;font-weight:900;color:#fff;
  box-shadow:0 4px 12px rgba(0,100,255,0.4);}
.device-img{flex:1;display:flex;align-items:center;justify-content:center;position:relative;z-index:1;margin:10px 0;}
.device{width:110px;height:260px;border-radius:55px;
  background:linear-gradient(160deg,#2a2a2a 0%,#111 60%,#1e1e1e 100%);
  position:relative;
  box-shadow:0 8px 24px rgba(0,0,0,0.5),inset 2px 2px 6px rgba(255,255,255,0.04);}
.device-trim{position:absolute;inset:-8px;border-radius:63px;
  background:linear-gradient(160deg,#e8e8e8,#d0d0d0,#e0e0e0);z-index:-1;
  box-shadow:2px 4px 12px rgba(0,0,0,0.3);}
.d-lens{position:absolute;top:30px;left:50%;transform:translateX(-50%);
  width:44px;height:44px;border-radius:50%;
  background:radial-gradient(circle at 35% 35%,#1a3a5c,#0a1a2e,#000);
  border:2px solid rgba(255,255,255,0.12);}
.d-lens::after{content:'';position:absolute;top:22%;left:22%;width:26%;height:26%;
  border-radius:50%;background:rgba(255,255,255,0.3);}
.d-btn{position:absolute;bottom:30px;left:50%;transform:translateX(-50%);
  width:50px;height:50px;border-radius:50%;
  background:radial-gradient(circle,#2a2a2a,#111);
  border:2px solid rgba(255,255,255,0.15);}
.box-bottom{z-index:1;text-align:center;width:100%;}
.prod-name{font-size:26px;font-weight:900;color:#1a2a4a;letter-spacing:-0.5px;line-height:1;}
.gen-pill{display:inline-block;border:1.5px solid #1a2a4a;border-radius:20px;
  font-size:12px;color:#1a2a4a;padding:3px 12px;margin:6px 0;}
.features{font-size:10.5px;color:#444;line-height:1.6;margin-top:4px;}
/* light gradient at bottom of box */
.box::after{content:'';position:absolute;bottom:0;left:0;right:0;height:140px;
  background:linear-gradient(0deg,rgba(230,230,235,0.8) 0%,transparent 100%);}
/* subtle bg glow */
.glow{position:absolute;width:400px;height:400px;border-radius:50%;
  background:radial-gradient(circle,rgba(0,100,200,0.08) 0%,transparent 70%);
  top:50%;left:50%;transform:translate(-50%,-60%);}
</style></head><body>
<div class="countertop"></div>
<div class="glow"></div>
<div class="box">
  <div class="box-top">
    <div class="arlo-logo">arlo</div>
    <div class="badge-2k">2K</div>
  </div>
  <div class="device-img">
    <div class="device">
      <div class="device-trim"></div>
      <div class="d-lens"></div>
      <div class="d-btn"></div>
    </div>
  </div>
  <div class="box-bottom">
    <div class="prod-name">Video Doorbell</div>
    <div class="gen-pill">2nd Generation</div>
    <div class="features">
      Battery Powered or Wired &nbsp;|&nbsp; Live 2K Video &nbsp;|&nbsp; 2-Way Audio<br>
      Integrated Siren &nbsp;|&nbsp; Night Vision
    </div>
  </div>
</div>
</body></html>` },

  // ── PHOTO 2: Unboxing ──────────────────────────────────
  { file: 'photo2.jpg', html: `
<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:${W}px;height:${H}px;overflow:hidden;
  background:linear-gradient(160deg,#e8e4de 0%,#d4cfc8 40%,#ccc8c0 100%);
  font-family:'Arial',sans-serif;display:flex;align-items:center;justify-content:center;}
body::before{content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse at 50% 0%,rgba(255,255,255,0.5) 0%,transparent 60%);}
/* outer box */
.outer-box{width:460px;height:720px;
  background:linear-gradient(180deg,#f5f2ec 0%,#ede8e0 100%);
  border-radius:8px;
  box-shadow:0 30px 70px rgba(0,0,0,0.35),0 8px 20px rgba(0,0,0,0.2),
    inset 0 1px 0 rgba(255,255,255,0.9);
  display:flex;flex-direction:column;align-items:center;
  padding:0;overflow:hidden;position:relative;}
.outer-box-top{width:100%;background:linear-gradient(180deg,#f8f5ef,#ede9e1);
  padding:20px 24px 16px;border-bottom:1px solid rgba(0,0,0,0.06);}
.arlo-top{font-size:22px;font-weight:900;color:#1a2a4a;font-style:italic;}
.welcome{font-size:11px;color:#666;margin-top:6px;line-height:1.5;}
.welcome strong{color:#333;display:block;font-size:13px;margin-bottom:2px;}
/* foam pad */
.foam{width:100%;height:90px;
  background:linear-gradient(180deg,#1a1a1a 0%,#222 100%);
  display:flex;align-items:center;justify-content:center;position:relative;}
.foam::after{content:'';position:absolute;
  width:40px;height:40px;border-radius:50%;
  background:rgba(255,255,255,0.08);
  box-shadow:inset 0 2px 4px rgba(0,0,0,0.5);}
/* inner tray */
.inner-tray{flex:1;width:90%;margin:10px auto;
  background:linear-gradient(180deg,#f0ece4,#e8e3db);
  border-radius:6px;
  box-shadow:inset 0 2px 8px rgba(0,0,0,0.1);
  display:flex;align-items:center;justify-content:center;
  position:relative;padding:20px;}
/* device in tray */
.tray-device{width:120px;height:290px;border-radius:60px;
  background:linear-gradient(160deg,#1e1e1e 0%,#111 60%,#181818 100%);
  position:relative;
  box-shadow:0 8px 24px rgba(0,0,0,0.5),2px 2px 0 rgba(255,255,255,0.03);}
.tray-trim{position:absolute;inset:-9px;border-radius:69px;
  background:linear-gradient(160deg,#f0f0f0,#d8d8d8,#e8e8e8);z-index:-1;
  box-shadow:0 4px 10px rgba(0,0,0,0.2);}
.t-lens{position:absolute;top:34px;left:50%;transform:translateX(-50%);
  width:50px;height:50px;border-radius:50%;
  background:radial-gradient(circle at 35% 35%,#1a3a5c,#0a1a2e,#000);
  border:2px solid rgba(255,255,255,0.1);
  box-shadow:0 0 12px rgba(0,80,180,0.3);}
.t-lens::after{content:'';position:absolute;top:22%;left:22%;width:26%;height:26%;
  border-radius:50%;background:rgba(255,255,255,0.3);}
/* blue tab */
.blue-tab{position:absolute;top:-6px;left:50%;transform:translateX(-50%);
  width:28px;height:44px;background:#00aaee;border-radius:0 0 4px 4px;z-index:10;}
/* charge label */
.charge-label{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
  text-align:center;color:rgba(255,255,255,0.9);
  font-size:14px;font-weight:700;letter-spacing:2px;line-height:1.6;}
.t-btn{position:absolute;bottom:36px;left:50%;transform:translateX(-50%);
  width:56px;height:56px;border-radius:50%;
  background:radial-gradient(circle,#1e1e1e,#0a0a0a);
  border:2px solid rgba(255,255,255,0.12);}
</style></head><body>
<div class="outer-box">
  <div class="outer-box-top">
    <div class="arlo-top">arlo <span style="font-style:normal;font-weight:300;font-size:14px;color:#999">✦</span></div>
    <div class="welcome"><strong>Welcome to the Arlo family.</strong>Now you can protect your everything.</div>
  </div>
  <div class="foam"></div>
  <div class="inner-tray">
    <div class="tray-device">
      <div class="tray-trim"></div>
      <div class="blue-tab"></div>
      <div class="t-lens"></div>
      <div class="charge-label">CHARGE<br>BEFORE<br>SETUP</div>
      <div class="t-btn"></div>
    </div>
  </div>
</div>
</body></html>` },

  // ── PHOTO 3: Accessories ───────────────────────────────
  { file: 'photo3.jpg', html: `
<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{width:${W}px;height:${H}px;overflow:hidden;
  background:linear-gradient(160deg,#e8e4de 0%,#d8d3cb 50%,#ccc7bf 100%);
  font-family:'Arial',sans-serif;display:flex;flex-direction:column;
  align-items:center;justify-content:flex-start;}
body::before{content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse at 50% 0%,rgba(255,255,255,0.45) 0%,transparent 55%);}
/* outer box - open top view */
.box-outer{width:480px;background:linear-gradient(180deg,#f5f2ec,#ede9e0);
  border-radius:0 0 12px 12px;
  box-shadow:0 20px 50px rgba(0,0,0,0.3),0 4px 12px rgba(0,0,0,0.15);
  padding:20px;position:relative;z-index:1;min-height:820px;}
/* header inside box */
.box-header{background:linear-gradient(180deg,#f8f5ef,#f0ece4);
  padding:16px 20px;border-radius:8px;margin-bottom:16px;
  box-shadow:inset 0 1px 0 rgba(255,255,255,0.8);}
.arlo-hdr{font-size:20px;font-weight:900;color:#1a2a4a;font-style:italic;}
.welcome-hdr{font-size:10px;color:#888;margin-top:4px;line-height:1.5;}
/* foam strip */
.foam-strip{width:100%;height:72px;background:linear-gradient(180deg,#1a1a1a,#242424);
  border-radius:6px;margin-bottom:16px;position:relative;
  box-shadow:0 4px 12px rgba(0,0,0,0.3);}
.foam-hole{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
  width:32px;height:32px;border-radius:50%;
  background:rgba(255,255,255,0.06);box-shadow:inset 0 2px 4px rgba(0,0,0,0.6);}
/* docs stack */
.docs{background:white;padding:14px 16px;border-radius:6px;margin-bottom:16px;
  box-shadow:0 2px 8px rgba(0,0,0,0.12);position:relative;}
.doc-title{font-size:13px;font-weight:700;color:#1a2a4a;}
.doc-sub{font-size:10px;color:#777;margin-top:3px;}
.arlo-doc-logo{font-size:16px;font-weight:900;color:#1a2a4a;font-style:italic;margin-bottom:8px;}
.doc-body{font-size:9px;color:#888;line-height:1.6;margin-top:6px;}
/* hardware section */
.hardware{display:flex;gap:14px;align-items:flex-start;}
/* mounting bracket */
.bracket{width:140px;min-height:220px;
  background:linear-gradient(160deg,#6a6a6a,#505050,#5a5a5a);
  border-radius:8px;
  box-shadow:0 6px 16px rgba(0,0,0,0.4),inset 1px 1px 0 rgba(255,255,255,0.1);
  display:flex;flex-direction:column;align-items:center;justify-content:space-around;
  padding:20px 16px;}
.screw-hole{width:14px;height:14px;border-radius:50%;
  background:radial-gradient(circle,#333,#111);
  box-shadow:inset 0 2px 4px rgba(0,0,0,0.8),0 1px 0 rgba(255,255,255,0.1);}
.bracket-slot{width:50px;height:70px;border-radius:25px;
  background:rgba(0,0,0,0.5);box-shadow:inset 0 2px 6px rgba(0,0,0,0.6);}
/* tools bag */
.tools-section{flex:1;display:flex;flex-direction:column;gap:12px;}
.tools-bag{background:rgba(200,200,200,0.5);border:1px solid rgba(0,0,0,0.1);
  border-radius:6px;padding:12px;
  box-shadow:0 2px 8px rgba(0,0,0,0.1);}
.bag-label{font-size:10px;color:#666;font-weight:600;letter-spacing:1px;
  text-transform:uppercase;margin-bottom:8px;}
.bag-items{display:flex;gap:10px;align-items:center;flex-wrap:wrap;}
.screw{width:8px;height:18px;background:linear-gradient(180deg,#bbb,#888);
  border-radius:4px;}
.anchor{width:10px;height:14px;background:linear-gradient(180deg,#cc8844,#aa6633);
  border-radius:3px;}
/* security tool */
.security-tool-wrap{background:rgba(200,200,200,0.3);border-radius:6px;
  padding:12px;display:flex;flex-direction:column;align-items:center;gap:8px;}
.sec-tool{width:6px;height:80px;background:linear-gradient(180deg,#ccc,#999,#bbb);
  border-radius:3px;position:relative;}
.sec-tool::before{content:'';position:absolute;bottom:-8px;left:50%;
  transform:translateX(-50%);
  width:18px;height:18px;border-radius:50%;
  background:linear-gradient(135deg,#ddd,#aaa);
  box-shadow:0 2px 4px rgba(0,0,0,0.3);}
.tool-label{font-size:9px;color:#777;letter-spacing:1px;text-align:center;}
</style></head><body>
<div class="box-outer">
  <div class="box-header">
    <div class="arlo-hdr">arlo ✦</div>
    <div class="welcome-hdr">Welcome to the Arlo family. Now you can protect your everything.</div>
  </div>
  <div class="foam-strip"><div class="foam-hole"></div></div>
  <div class="docs">
    <div class="arlo-doc-logo">arlo</div>
    <div class="doc-title">Quick Start Guide</div>
    <div class="doc-sub">Video Doorbell · 2nd Generation</div>
    <div class="doc-body">
      <strong style="color:#333;display:block;margin-bottom:4px">Arlo Safety and Compliance Information</strong>
      Safe Handling and Usage Guidelines for Non-removable and Rechargeable Battery Packs.<br>
      Battery packs can EXPLODE, CATCH FIRE, and/or CAUSE BURNS if disassembled, punctured, cut, crushed, short circuited, incinerated...
    </div>
  </div>
  <div class="hardware">
    <div class="bracket">
      <div class="screw-hole"></div>
      <div class="bracket-slot"></div>
      <div class="screw-hole"></div>
    </div>
    <div class="tools-section">
      <div class="tools-bag">
        <div class="bag-label">Hardware Kit</div>
        <div class="bag-items">
          <div class="screw"></div><div class="screw"></div>
          <div class="screw"></div><div class="screw"></div>
          <div class="anchor"></div><div class="anchor"></div>
          <div class="anchor"></div>
        </div>
      </div>
      <div class="security-tool-wrap">
        <div class="sec-tool"></div>
        <div class="tool-label">Security Pin</div>
      </div>
    </div>
  </div>
</div>
</body></html>` }
];

(async () => {
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args: ['--no-sandbox'],
  });

  for (const scene of scenes) {
    const page = await browser.newPage();
    await page.setViewportSize({ width: W, height: H });
    await page.setContent(scene.html, { waitUntil: 'networkidle' });
    await page.waitForTimeout(800);
    await page.screenshot({
      path: path.join(OUT, scene.file),
      type: 'jpeg', quality: 95,
    });
    console.log(`✅ ${scene.file}`);
    await page.close();
  }

  await browser.close();
  console.log('All photos generated.');
})();
