import {
  AbsoluteFill,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const oswald = "Oswald, sans-serif";
const bebas  = "BebasNeue, Impact, sans-serif";

const NAVY     = "#1B2A4A";
const RED      = "#C8102E";
const WHITE    = "#FFFFFF";
const CHARCOAL = "#13131A";
const GOLD     = "#C9A227";

const FPS  = 30;
const BPM  = 130;
const BEAT = FPS * 60 / BPM; // ≈15.4 frames

// ── Timeline (frames) ─────────────────────────────────────────────────────────
//  Each scene ≈ 4-5 s, total ~47 s
const T = {
  intro:    [0,   4  * FPS],   // logo reveal
  tag:      [4  * FPS, 8  * FPS],  // tagline
  car1:     [8  * FPS, 12 * FPS],  // vehicle 1 – rear angle
  s1:       [12 * FPS, 17 * FPS],  // 24/7 service card
  car2:     [17 * FPS, 21 * FPS],  // vehicle 2 – side
  s2:       [21 * FPS, 26 * FPS],  // fast response card
  car3:     [26 * FPS, 30 * FPS],  // vehicle 3 – front
  s3:       [30 * FPS, 35 * FPS],  // elite guards card
  flyer:    [35 * FPS, 39 * FPS],  // flyer showcase
  s4:       [39 * FPS, 44 * FPS],  // mobile patrol card
  nextdoor: [44 * FPS, 48 * FPS],  // nextdoor social proof
  outro:    [48 * FPS, 55 * FPS],  // logo + contact
};

export const PROMO_DURATION = T.outro[1];

// ── Helpers ───────────────────────────────────────────────────────────────────

const usePulse = (strength = 0.035) => {
  const frame = useCurrentFrame();
  const p = (frame % BEAT) / BEAT;
  return 1 + strength * Math.exp(-6 * p) * Math.sin(Math.PI * p * 3);
};

const Flash = () => {
  const frame = useCurrentFrame();
  const op = interpolate(frame, [0, 9], [1, 0], { extrapolateRight: "clamp" });
  return <AbsoluteFill style={{ backgroundColor: WHITE, opacity: op, pointerEvents: "none" }} />;
};

const ScanLine = ({ color = RED, speed = 40 }: { color?: string; speed?: number }) => {
  const frame = useCurrentFrame();
  const { height } = useVideoConfig();
  const y = interpolate(frame, [0, speed], [-4, height + 4], { extrapolateRight: "clamp" });
  return (
    <div style={{
      position: "absolute", left: 0, right: 0, top: y, height: 4, pointerEvents: "none",
      background: `linear-gradient(90deg, transparent 0%, ${color} 40%, ${color} 60%, transparent 100%)`,
      opacity: 0.85,
    }} />
  );
};

const Particles = ({ count = 28, dark = true }: { count?: number; dark?: boolean }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  return (
    <>
      {Array.from({ length: count }, (_, i) => {
        const sx = ((i * 137.5) % 1);
        const sy = ((i * 251.3) % 1);
        const ss = ((i * 89.7)  % 1);
        const x  = sx * width;
        const y  = ((sy * height - frame * (0.3 + ss * 0.6)) % height + height) % height;
        return (
          <div key={i} style={{
            position: "absolute", left: x, top: y,
            width: 2 + ss * 4, height: 2 + ss * 4, borderRadius: "50%",
            backgroundColor: i % 5 === 0 ? RED : dark ? WHITE : NAVY,
            opacity: 0.12 + sx * 0.2, pointerEvents: "none",
          }} />
        );
      })}
    </>
  );
};

const Corners = ({ color = RED, size = 72, op = 0.8 }: { color?: string; size?: number; op?: number }) => (
  <>
    {[{ top: 48, left: 48 }, { top: 48, right: 48 }, { bottom: 48, left: 48 }, { bottom: 48, right: 48 }].map((p, i) => (
      <div key={i} style={{ position: "absolute", ...p, width: size, height: size, opacity: op }}>
        <div style={{ position: "absolute", top: 0, left: 0, width: "100%", height: 3, backgroundColor: color }} />
        <div style={{ position: "absolute", top: 0, left: 0, width: 3, height: "100%", backgroundColor: color }} />
      </div>
    ))}
  </>
);

const GlitchText = ({ text, style }: { text: string; style: React.CSSProperties }) => {
  const frame = useCurrentFrame();
  const glitch = (frame % 47 < 3 || frame % 71 < 2) ? (frame % 2 === 0 ? 7 : -7) : 0;
  return (
    <div style={{ position: "relative" }}>
      {glitch !== 0 && (
        <div style={{ ...style, position: "absolute", color: RED, opacity: 0.55, transform: `translateX(${glitch + 4}px)` }}>{text}</div>
      )}
      <div style={{ ...style, transform: `translateX(${glitch}px)` }}>{text}</div>
    </div>
  );
};

// Ken Burns zoom on a full-screen photo
const KenBurns = ({
  src, fromScale = 1.18, toScale = 1.02, fromX = "50%", toX = "50%",
  fromY = "50%", toY = "50%", duration = 4 * FPS, overlay = 0.35,
}: {
  src: string; fromScale?: number; toScale?: number;
  fromX?: string; toX?: string; fromY?: string; toY?: string;
  duration?: number; overlay?: number;
}) => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, duration], [fromScale, toScale], { extrapolateRight: "clamp" });
  const ox    = interpolate(frame, [0, duration], [parseFloat(fromX), parseFloat(toX)], { extrapolateRight: "clamp" });
  const oy    = interpolate(frame, [0, duration], [parseFloat(fromY), parseFloat(toY)], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <Img src={staticFile(src)} style={{
        width: "100%", height: "100%", objectFit: "cover",
        transform: `scale(${scale})`,
        transformOrigin: `${ox}% ${oy}%`,
      }} />
      <AbsoluteFill style={{ background: `linear-gradient(to top, rgba(0,0,0,${overlay + 0.3}) 0%, rgba(0,0,0,${overlay}) 50%, rgba(0,0,0,${overlay * 0.5}) 100%)` }} />
    </AbsoluteFill>
  );
};

// Animated badge that slams in from a direction
const Badge = ({
  text, subtext, from = "bottom", startFrame = 20, bgColor = RED, textColor = WHITE,
}: {
  text: string; subtext?: string; from?: "bottom" | "left" | "right" | "top";
  startFrame?: number; bgColor?: string; textColor?: string;
}) => {
  const frame = useCurrentFrame();
  const sp = spring({ frame: frame - startFrame, fps: FPS, config: { damping: 11, stiffness: 190 } });
  const off = interpolate(sp, [0, 1], [200, 0]);
  const op  = interpolate(frame, [startFrame, startFrame + 10], [0, 1], { extrapolateRight: "clamp" });
  const transform =
    from === "bottom" ? `translateY(${off}px)` :
    from === "top"    ? `translateY(-${off}px)` :
    from === "left"   ? `translateX(-${off}px)` :
                        `translateX(${off}px)`;
  return (
    <div style={{ transform, opacity: op }}>
      <div style={{
        backgroundColor: bgColor, borderRadius: 7,
        paddingTop: 16, paddingBottom: 16, paddingLeft: 52, paddingRight: 52,
        boxShadow: `0 6px 40px rgba(200,16,46,0.65)`,
      }}>
        <div style={{ color: textColor, fontSize: 46, fontFamily: bebas, letterSpacing: 8, textAlign: "center" }}>{text}</div>
        {subtext && <div style={{ color: textColor, fontSize: 26, fontFamily: oswald, fontWeight: 300, letterSpacing: 4, textAlign: "center", opacity: 0.85 }}>{subtext}</div>}
      </div>
    </div>
  );
};

// ── Scene 1: Logo Intro ───────────────────────────────────────────────────────
const IntroScene = () => {
  const frame = useCurrentFrame();
  const pulse = usePulse(0.05);
  const sp    = spring({ frame, fps: FPS, config: { damping: 9, stiffness: 150 } });
  const scale = interpolate(sp, [0, 1], [0.3, 1]);
  const op    = interpolate(frame, [0, 14], [0, 1], { extrapolateRight: "clamp" });
  const nameOp = interpolate(frame, [22, 40], [0, 1], { extrapolateRight: "clamp" });
  const lineW  = interpolate(frame, [36, 55], [0, 1], { extrapolateRight: "clamp" });
  const ringS  = spring({ frame, fps: FPS, config: { damping: 22, stiffness: 70 } });
  const ringOp = interpolate(frame, [4, 40], [0.7, 0], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(frame, [T.intro[1] - T.intro[0] - 10, T.intro[1] - T.intro[0]], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 42%, #2A0810 0%, ${CHARCOAL} 68%)`, justifyContent: "center", alignItems: "center", flexDirection: "column", opacity: fadeOut }}>
      <Particles count={38} />
      <Corners />
      <div style={{ position: "absolute", width: 920 * ringS, height: 920 * ringS, borderRadius: "50%", border: `4px solid ${RED}`, opacity: ringOp }} />
      <div style={{ transform: `scale(${scale * pulse})`, opacity: op, filter: "drop-shadow(0 0 80px rgba(200,16,46,0.75)) drop-shadow(0 0 150px rgba(200,16,46,0.35))", zIndex: 2 }}>
        <Img src={staticFile("images/logo.jpg")} style={{ width: 820, height: 820, objectFit: "contain" }} />
      </div>
      <div style={{ opacity: nameOp, textAlign: "center", marginTop: -18, zIndex: 3 }}>
        <div style={{ display: "flex", justifyContent: "center", gap: 14 }}>
          <span style={{ color: WHITE, fontSize: 78, fontFamily: bebas, letterSpacing: 6 }}>MONTES</span>
          <span style={{ color: RED,   fontSize: 78, fontFamily: bebas, letterSpacing: 6 }}>PATROL</span>
        </div>
        <div style={{ width: `${lineW * 340}px`, height: 3, backgroundColor: RED, margin: "8px auto" }} />
        <div style={{ color: "#8AAAC8", fontSize: 26, fontFamily: oswald, letterSpacing: 14, opacity: interpolate(frame, [54, 70], [0, 1], { extrapolateRight: "clamp" }) }}>SECURITY LLC</div>
      </div>
      <ScanLine />
    </AbsoluteFill>
  );
};

// ── Scene 2: Tagline ──────────────────────────────────────────────────────────
const TaglineScene = () => {
  const frame  = useCurrentFrame();
  const pulse  = usePulse(0.022);
  const sp1    = spring({ frame,     fps: FPS, config: { damping: 10, stiffness: 210 } });
  const sp2    = spring({ frame: frame - 8, fps: FPS, config: { damping: 10, stiffness: 210 } });
  const x1     = interpolate(sp1, [0, 1], [-450, 0]);
  const x2     = interpolate(sp2, [0, 1], [450,  0]);
  const subOp  = interpolate(frame, [30, 50], [0, 1], { extrapolateRight: "clamp" });
  const subY   = interpolate(frame, [30, 50], [55, 0], { extrapolateRight: "clamp" });
  const lineW  = interpolate(frame, [36, 58], [0, 290], { extrapolateRight: "clamp" });
  const logoSp = spring({ frame: frame - 48, fps: FPS, config: { damping: 12, stiffness: 160 } });

  return (
    <AbsoluteFill style={{ backgroundColor: WHITE, justifyContent: "center", alignItems: "flex-start", flexDirection: "column" }}>
      <Flash />
      <div style={{ position: "absolute", top: 0,    left: 0, right: 0, height: 14, backgroundColor: RED }} />
      <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: 14, backgroundColor: NAVY }} />
      <div style={{ position: "absolute", top: 14, bottom: 14, left: 0, width: interpolate(frame, [0, 18], [1080, 0], { extrapolateRight: "clamp" }), backgroundColor: RED, opacity: 0.07 }} />

      <div style={{ paddingLeft: 65 }}>
        <div style={{ transform: `translateX(${x1}px) scale(${pulse})`, transformOrigin: "left center" }}>
          <GlitchText text="YOUR SAFETY" style={{ color: NAVY, fontSize: 128, fontFamily: bebas, letterSpacing: 2, lineHeight: 0.88 }} />
        </div>
        <div style={{ transform: `translateX(${x2}px) scale(${pulse})`, transformOrigin: "left center" }}>
          <GlitchText text="OUR PRIORITY" style={{ color: RED, fontSize: 128, fontFamily: bebas, letterSpacing: 2, lineHeight: 0.88 }} />
        </div>
        <div style={{ opacity: subOp, transform: `translateY(${subY}px)`, marginTop: 44 }}>
          <div style={{ display: "flex", gap: 12, marginBottom: 28 }}>
            <div style={{ width: lineW, height: 4, backgroundColor: NAVY }} />
            <div style={{ width: lineW, height: 4, backgroundColor: RED }} />
          </div>
          <div style={{ color: NAVY, fontSize: 34, fontFamily: oswald, fontWeight: 500, letterSpacing: 4, lineHeight: 1.3 }}>PROFESSIONAL SECURITY{"\n"}YOU CAN TRUST</div>
        </div>
      </div>

      <div style={{ position: "absolute", bottom: 52, right: 48, transform: `scale(${Math.max(0, logoSp)}) rotate(${interpolate(Math.max(0, logoSp), [0, 1], [-40, 0])}deg)`, width: 182, height: 182 }}>
        <Img src={staticFile("images/logo.jpg")} style={{ width: "100%", height: "100%", objectFit: "contain" }} />
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 3: Vehicle 1 – rear angle ──────────────────────────────────────────
const Car1Scene = () => {
  const frame = useCurrentFrame();
  const dur = T.car1[1] - T.car1[0];
  const tagOp = interpolate(frame, [18, 34], [0, 1], { extrapolateRight: "clamp" });
  const tagSp = spring({ frame: frame - 18, fps: FPS, config: { damping: 11, stiffness: 180 } });
  const tagY  = interpolate(tagSp, [0, 1], [120, 0]);
  const sub1Op = interpolate(frame, [32, 48], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill>
      <Flash />
      <KenBurns src="images/vehicle1.jpg" fromScale={1.2} toScale={1.0} fromX="70" toX="50" duration={dur} overlay={0.3} />
      <ScanLine color={GOLD} />
      <Corners color={GOLD} />

      {/* Bottom overlay block */}
      <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, background: "linear-gradient(to top, rgba(0,0,0,0.92) 0%, transparent 100%)", paddingBottom: 80, paddingTop: 120, paddingLeft: 65, paddingRight: 65 }}>
        <div style={{ opacity: tagOp, transform: `translateY(${tagY}px)` }}>
          <div style={{ color: GOLD, fontSize: 28, fontFamily: oswald, fontWeight: 600, letterSpacing: 6, marginBottom: 8 }}>◆ ON PATROL</div>
          <div style={{ color: WHITE, fontSize: 86, fontFamily: bebas, letterSpacing: 3, lineHeight: 0.9 }}>STAY BACK —{"\n"}SECURITY PATROL</div>
        </div>
        <div style={{ opacity: sub1Op, marginTop: 20, display: "flex", gap: 16, alignItems: "center" }}>
          <div style={{ width: 8, height: 8, borderRadius: "50%", backgroundColor: RED, boxShadow: "0 0 12px red" }} />
          <div style={{ color: "#CCC", fontSize: 28, fontFamily: oswald, fontWeight: 300, letterSpacing: 3 }}>24/7 LICENSED & INSURED</div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 4: Service – 24/7 ───────────────────────────────────────────────────
const ServiceScene = ({ iconChar, title, desc, dark, dir = "left" }: { iconChar: string; title: string; desc: string; dark: boolean; dir?: string }) => {
  const frame  = useCurrentFrame();
  const pulse  = usePulse(0.03);
  const iconSp = spring({ frame,      fps: FPS, config: { damping: 9, stiffness: 200 } });
  const textSp = spring({ frame: frame - 12, fps: FPS, config: { damping: 11, stiffness: 165 } });
  const off    = interpolate(textSp, [0, 1], [180, 0]);
  const tx     = dir === "left" ? `translateX(-${off}px)` : dir === "right" ? `translateX(${off}px)` : dir === "top" ? `translateY(-${off}px)` : `translateY(${off}px)`;
  const descOp = interpolate(frame, [35, 55], [0, 1], { extrapolateRight: "clamp" });
  const lineW  = interpolate(frame, [26, 46], [0, 255], { extrapolateRight: "clamp" });
  const logoOp = interpolate(frame, [50, 68], [0, 0.6], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: dark ? NAVY : "#F0F2F5", justifyContent: "center", alignItems: "center", flexDirection: "column" }}>
      <Flash />
      {dark && <Particles count={22} />}
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 9, backgroundColor: RED }} />

      <div style={{ width: 200, height: 200, borderRadius: "50%", backgroundColor: RED, display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${interpolate(iconSp, [0, 1], [0, 1])} ) scale(${pulse})`, border: `6px solid ${dark ? "#2D4470" : WHITE}`, boxShadow: "0 10px 50px rgba(200,16,46,0.45)", marginBottom: 48 }}>
        <span style={{ fontSize: 96, lineHeight: 1 }}>{iconChar}</span>
      </div>

      <div style={{ transform: tx, textAlign: "center", paddingLeft: 58, paddingRight: 58 }}>
        <div style={{ color: dark ? WHITE : NAVY, fontSize: 68, fontFamily: bebas, letterSpacing: 3, lineHeight: 1 }}>{title}</div>
        <div style={{ width: lineW, height: 4, backgroundColor: RED, margin: "20px auto" }} />
        <div style={{ opacity: descOp, color: dark ? "#8AAAC8" : "#4A5A70", fontSize: 36, fontFamily: oswald, fontWeight: 300, lineHeight: 1.5, letterSpacing: 1 }}>{desc}</div>
      </div>

      <div style={{ position: "absolute", bottom: 52, left: 58, display: "flex", gap: 12 }}>
        {[0, 5, 10].map(d => {
          const f = useCurrentFrame();
          const sc = interpolate((f + d) % BEAT, [0, BEAT / 2, BEAT], [1, 1.7, 1]);
          const op = interpolate((f + d) % BEAT, [0, BEAT / 2, BEAT], [1, 0.2, 1]);
          return <div key={d} style={{ width: 15, height: 15, borderRadius: "50%", backgroundColor: RED, transform: `scale(${sc})`, opacity: op }} />;
        })}
      </div>

      <div style={{ position: "absolute", bottom: 36, right: 46, opacity: logoOp, width: 80, height: 80 }}>
        <Img src={staticFile("images/logo.jpg")} style={{ width: "100%", height: "100%", objectFit: "contain" }} />
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 5: Vehicle 2 – side view ───────────────────────────────────────────
const Car2Scene = () => {
  const frame = useCurrentFrame();
  const dur   = T.car2[1] - T.car2[0];
  const sp    = spring({ frame: frame - 15, fps: FPS, config: { damping: 11, stiffness: 175 } });
  const tagX  = interpolate(sp, [0, 1], [-350, 0]);
  const tagOp = interpolate(frame, [15, 32], [0, 1], { extrapolateRight: "clamp" });
  const subOp = interpolate(frame, [34, 50], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill>
      <Flash />
      <KenBurns src="images/vehicle2.jpg" fromScale={1.1} toScale={1.22} fromX="30" toX="50" duration={dur} overlay={0.25} />
      <Corners color={WHITE} op={0.5} />

      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 9, backgroundColor: RED }} />

      {/* Left text panel */}
      <div style={{ position: "absolute", top: 0, bottom: 0, left: 0, width: 520, display: "flex", flexDirection: "column", justifyContent: "flex-end", padding: 65, paddingBottom: 100, background: "linear-gradient(to right, rgba(0,0,0,0.82) 0%, transparent 100%)" }}>
        <div style={{ opacity: tagOp, transform: `translateX(${tagX}px)` }}>
          <div style={{ color: GOLD, fontSize: 26, fontFamily: oswald, fontWeight: 600, letterSpacing: 6, marginBottom: 10 }}>◆ ARMED PATROL</div>
          <div style={{ color: WHITE, fontSize: 80, fontFamily: bebas, letterSpacing: 2, lineHeight: 0.9 }}>WE PROTECT{"\n"}& SERVE</div>
        </div>
        <div style={{ opacity: subOp, marginTop: 24, display: "flex", flexDirection: "column", gap: 10 }}>
          {["On-Site Security", "Mobile Patrols", "Armed Services"].map((s, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 14 }}>
              <div style={{ width: 10, height: 10, backgroundColor: RED, borderRadius: "50%", boxShadow: "0 0 10px red" }} />
              <div style={{ color: WHITE, fontSize: 26, fontFamily: oswald, fontWeight: 300, letterSpacing: 2 }}>{s}</div>
            </div>
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 7: Vehicle 3 – front angle ─────────────────────────────────────────
const Car3Scene = () => {
  const frame = useCurrentFrame();
  const dur   = T.car3[1] - T.car3[0];
  const sp    = spring({ frame: frame - 12, fps: FPS, config: { damping: 12, stiffness: 170 } });
  const tagY  = interpolate(sp, [0, 1], [-100, 0]);
  const tagOp = interpolate(frame, [12, 28], [0, 1], { extrapolateRight: "clamp" });
  const num   = interpolate(frame, [28, 50], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill>
      <Flash />
      <KenBurns src="images/vehicle3.jpg" fromScale={1.08} toScale={1.2} fromX="50" toX="40" duration={dur} overlay={0.28} />
      <ScanLine color={RED} speed={45} />

      {/* Top banner */}
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, padding: "55px 65px 30px", background: "linear-gradient(to bottom, rgba(0,0,0,0.88) 0%, transparent 100%)" }}>
        <div style={{ opacity: tagOp, transform: `translateY(${tagY}px)` }}>
          <div style={{ color: GOLD, fontSize: 26, fontFamily: oswald, letterSpacing: 6, marginBottom: 6 }}>◆ KATY AREA SECURITY</div>
          <div style={{ color: WHITE, fontSize: 76, fontFamily: bebas, letterSpacing: 3, lineHeight: 0.9 }}>RAPID RESPONSE{"\n"}ON WHEELS</div>
        </div>
      </div>

      {/* Bottom: phone highlight */}
      <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, padding: "30px 65px 75px", background: "linear-gradient(to top, rgba(0,0,0,0.9) 0%, transparent 100%)" }}>
        <div style={{ opacity: num, display: "flex", alignItems: "center", gap: 18 }}>
          <div style={{ width: 54, height: 54, borderRadius: "50%", backgroundColor: RED, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <span style={{ fontSize: 26 }}>📞</span>
          </div>
          <div style={{ color: WHITE, fontSize: 64, fontFamily: bebas, letterSpacing: 4 }}>346-277-2563</div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 9: Flyer showcase ───────────────────────────────────────────────────
const FlyerScene = () => {
  const frame = useCurrentFrame();
  const dur   = T.flyer[1] - T.flyer[0];
  const scale = interpolate(frame, [0, dur], [1.18, 1.02], { extrapolateRight: "clamp" });
  const fadeIn = interpolate(frame, [0, 14], [0, 1], { extrapolateRight: "clamp" });
  const sp1   = spring({ frame: frame - 16, fps: FPS, config: { damping: 11, stiffness: 180 } });
  const b1Y   = interpolate(sp1, [0, 1], [140, 0]);
  const sp2   = spring({ frame: frame - 30, fps: FPS, config: { damping: 12, stiffness: 155 } });
  const b2X   = interpolate(sp2, [0, 1], [-320, 0]);
  const b2Op  = interpolate(frame, [30, 48], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill>
      <Flash />
      <AbsoluteFill style={{ overflow: "hidden" }}>
        <Img src={staticFile("images/flyer.jpg")} style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${scale})`, opacity: fadeIn }} />
        <AbsoluteFill style={{ background: "linear-gradient(to top, rgba(0,0,0,0.88) 0%, rgba(0,0,0,0.2) 45%, transparent 70%)" }} />
      </AbsoluteFill>
      <ScanLine color={WHITE} speed={42} />
      <div style={{ position: "absolute", bottom: 220, left: 0, right: 0, display: "flex", justifyContent: "center", transform: `translateY(${b1Y}px)` }}>
        <Badge text="PROTECTING YOUR WORLD" />
      </div>
      <div style={{ position: "absolute", bottom: 100, left: 0, right: 0, display: "flex", justifyContent: "center", opacity: b2Op, transform: `translateX(${b2X}px)` }}>
        <div style={{ color: WHITE, fontSize: 30, fontFamily: oswald, fontWeight: 300, letterSpacing: 6 }}>LICENSED • INSURED • PROFESSIONAL</div>
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 11: Nextdoor Social Proof ──────────────────────────────────────────
const NextdoorScene = () => {
  const frame = useCurrentFrame();
  const phoneSp = spring({ frame, fps: FPS, config: { damping: 12, stiffness: 120 } });
  const phoneScale = interpolate(phoneSp, [0, 1], [0.7, 1]);
  const labelOp = interpolate(frame, [22, 40], [0, 1], { extrapolateRight: "clamp" });
  const labelY  = interpolate(frame, [22, 40], [50, 0], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 50%, #1E2A1A 0%, ${CHARCOAL} 70%)`, justifyContent: "center", alignItems: "center", flexDirection: "column" }}>
      <Flash />
      <Particles count={25} />
      <Corners color={GOLD} />

      {/* Top label */}
      <div style={{ position: "absolute", top: 65, left: 0, right: 0, textAlign: "center" }}>
        <div style={{ color: GOLD, fontSize: 26, fontFamily: oswald, fontWeight: 600, letterSpacing: 6 }}>◆ AS SEEN ON NEXTDOOR</div>
        <div style={{ color: WHITE, fontSize: 52, fontFamily: bebas, letterSpacing: 4, marginTop: 6 }}>TRUSTED BY THE COMMUNITY</div>
      </div>

      {/* Phone mockup with screenshot */}
      <div style={{ transform: `scale(${phoneScale})`, zIndex: 2, filter: "drop-shadow(0 20px 60px rgba(0,0,0,0.8))" }}>
        <div style={{ width: 440, borderRadius: 36, overflow: "hidden", border: "3px solid rgba(255,255,255,0.15)", boxShadow: "0 0 60px rgba(200,16,46,0.3)" }}>
          <Img src={staticFile("images/nextdoor.jpg")} style={{ width: "100%", display: "block" }} />
        </div>
      </div>

      {/* Star rating badge */}
      <div style={{ opacity: labelOp, transform: `translateY(${labelY}px)`, marginTop: 36, zIndex: 3 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          {[1,2,3,4,5].map(i => <span key={i} style={{ fontSize: 44, color: GOLD }}>★</span>)}
          <div style={{ color: WHITE, fontSize: 34, fontFamily: oswald, fontWeight: 300, letterSpacing: 2 }}>Community Trusted</div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 12: Outro ───────────────────────────────────────────────────────────
const OutroScene = () => {
  const frame  = useCurrentFrame();
  const pulse  = usePulse(0.04);
  const logoSp = spring({ frame,      fps: FPS, config: { damping: 9,  stiffness: 130 } });
  const badgSp = spring({ frame: frame - 26, fps: FPS, config: { damping: 10, stiffness: 180 } });
  const phonSp = spring({ frame: frame - 46, fps: FPS, config: { damping: 14, stiffness: 145 } });
  const webSp  = spring({ frame: frame - 62, fps: FPS, config: { damping: 14, stiffness: 145 } });
  const bg     = interpolate(frame, [0, 120], [0, 0.3], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 38%, rgba(200,16,46,${bg}) 0%, ${CHARCOAL} 65%)`, justifyContent: "center", alignItems: "center", flexDirection: "column" }}>
      <Flash />
      <Particles count={42} />
      <Corners size={80} />

      <div style={{ transform: `scale(${interpolate(logoSp, [0, 1], [0.3, 1])} ) scale(${pulse})`, opacity: interpolate(frame, [0, 18], [0, 1], { extrapolateRight: "clamp" }), filter: "drop-shadow(0 0 70px rgba(200,16,46,0.7)) drop-shadow(0 0 130px rgba(200,16,46,0.3))", marginBottom: 26, zIndex: 2 }}>
        <Img src={staticFile("images/logo.jpg")} style={{ width: 560, height: 560, objectFit: "contain" }} />
      </div>

      <div style={{ opacity: interpolate(frame, [26, 42], [0, 1], { extrapolateRight: "clamp" }), transform: `scale(${Math.max(0, interpolate(badgSp, [0, 1], [0, 1]))})`, marginBottom: 46, zIndex: 2 }}>
        <div style={{ backgroundColor: RED, paddingTop: 18, paddingBottom: 18, paddingLeft: 65, paddingRight: 65, borderRadius: 8, boxShadow: "0 8px 42px rgba(200,16,46,0.65)" }}>
          <div style={{ color: WHITE, fontSize: 48, fontFamily: bebas, letterSpacing: 10 }}>LICENSED • INSURED</div>
        </div>
      </div>

      <div style={{ opacity: interpolate(frame, [46, 62], [0, 1], { extrapolateRight: "clamp" }), transform: `translateY(${interpolate(Math.max(0, phonSp), [0, 1], [80, 0])}px)`, display: "flex", alignItems: "center", gap: 20, marginBottom: 22, zIndex: 2 }}>
        <div style={{ width: 58, height: 58, borderRadius: "50%", backgroundColor: RED, display: "flex", alignItems: "center", justifyContent: "center" }}><span style={{ fontSize: 28 }}>📞</span></div>
        <div style={{ color: WHITE, fontSize: 58, fontFamily: bebas, letterSpacing: 4 }}>(346) 277-2563</div>
      </div>

      <div style={{ opacity: interpolate(frame, [62, 78], [0, 1], { extrapolateRight: "clamp" }), transform: `translateY(${interpolate(Math.max(0, webSp), [0, 1], [80, 0])}px)`, display: "flex", alignItems: "center", gap: 20, zIndex: 2 }}>
        <div style={{ width: 58, height: 58, borderRadius: "50%", backgroundColor: CHARCOAL, border: `2px solid ${RED}`, display: "flex", alignItems: "center", justifyContent: "center" }}><span style={{ fontSize: 28 }}>🌐</span></div>
        <div style={{ color: "#9EB8D0", fontSize: 33, fontFamily: oswald, fontWeight: 300, letterSpacing: 1 }}>montespatrolsecurityllc.com</div>
      </div>
    </AbsoluteFill>
  );
};

// ── Root ──────────────────────────────────────────────────────────────────────
export const PromoVideo: React.FC = () => (
  <AbsoluteFill>
    <Sequence from={T.intro[0]}    durationInFrames={T.intro[1]    - T.intro[0]}>    <IntroScene /> </Sequence>
    <Sequence from={T.tag[0]}      durationInFrames={T.tag[1]      - T.tag[0]}>      <TaglineScene /></Sequence>
    <Sequence from={T.car1[0]}     durationInFrames={T.car1[1]     - T.car1[0]}>     <Car1Scene />  </Sequence>
    <Sequence from={T.s1[0]}       durationInFrames={T.s1[1]       - T.s1[0]}>       <ServiceScene iconChar="🕐" title="24/7 SECURITY COVERAGE"      desc={"Around-the-clock protection.\nWe never sleep so you can."}          dark      dir="left"   /></Sequence>
    <Sequence from={T.car2[0]}     durationInFrames={T.car2[1]     - T.car2[0]}>     <Car2Scene />  </Sequence>
    <Sequence from={T.s2[0]}       durationInFrames={T.s2[1]       - T.s2[0]}>       <ServiceScene iconChar="⚡" title="FAST RESPONSE TIME"             desc={"Seconds matter in an emergency.\nWe respond before threats escalate."} dark={false} dir="right"  /></Sequence>
    <Sequence from={T.car3[0]}     durationInFrames={T.car3[1]     - T.car3[0]}>     <Car3Scene />  </Sequence>
    <Sequence from={T.s3[0]}       durationInFrames={T.s3[1]       - T.s3[0]}>       <ServiceScene iconChar="🛡️" title="ELITE TRAINED GUARDS"           desc={"Certified, professional, and ready.\nYour safety is our mission."}     dark      dir="bottom" /></Sequence>
    <Sequence from={T.flyer[0]}    durationInFrames={T.flyer[1]    - T.flyer[0]}>    <FlyerScene /> </Sequence>
    <Sequence from={T.s4[0]}       durationInFrames={T.s4[1]       - T.s4[0]}>       <ServiceScene iconChar="🚔" title="MOBILE PATROL SERVICES"         desc={"Visible deterrence. Consistent routes.\nComplete peace of mind."}      dark={false} dir="top"    /></Sequence>
    <Sequence from={T.nextdoor[0]} durationInFrames={T.nextdoor[1] - T.nextdoor[0]}> <NextdoorScene /></Sequence>
    <Sequence from={T.outro[0]}    durationInFrames={T.outro[1]    - T.outro[0]}>    <OutroScene /> </Sequence>
  </AbsoluteFill>
);
