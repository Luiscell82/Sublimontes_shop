import {
  AbsoluteFill,
  Audio,
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

const NAVY    = "#1B2A4A";
const RED     = "#C8102E";
const WHITE   = "#FFFFFF";
const CHARCOAL = "#13131A";
const LIGHT_GRAY = "#F0F2F5";

const FPS = 30;
const BPM = 120;
const BEAT = FPS * 60 / BPM; // 15 frames per beat

// ── Timeline ──────────────────────────────────────────────────────────────────
const INTRO_START  = 0;
const INTRO_END    = 4  * FPS;   //   0–4 s
const TAG_END      = 8  * FPS;   //   4–8 s
const FLYER_END    = 12 * FPS;   //  8–12 s
const S1_END       = 17 * FPS;   // 12–17 s
const S2_END       = 22 * FPS;   // 17–22 s
const S3_END       = 27 * FPS;   // 22–27 s
const S4_END       = 32 * FPS;   // 27–32 s
const OUTRO_END    = 39 * FPS;   // 32–39 s

export const PROMO_DURATION = OUTRO_END;

// ── Helpers ───────────────────────────────────────────────────────────────────

/** beat-sync pulse: scale oscillates on every beat */
const useBeatPulse = (strength = 0.04) => {
  const frame = useCurrentFrame();
  const beatPhase = (frame % BEAT) / BEAT;
  return 1 + strength * Math.exp(-6 * beatPhase) * Math.sin(Math.PI * beatPhase * 3);
};

/** White flash overlay – peaks at frame 0, gone by frame 8 */
const FlashOverlay = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 8], [1, 0], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: WHITE, opacity, pointerEvents: "none" }} />
  );
};

/** Thin horizontal scan-line sweeping top→bottom */
const ScanLine = ({ color = RED }: { color?: string }) => {
  const frame = useCurrentFrame();
  const { height } = useVideoConfig();
  const y = interpolate(frame, [0, 40], [-4, height + 4], { extrapolateRight: "clamp" });
  return (
    <div style={{
      position: "absolute", left: 0, right: 0,
      top: y, height: 4,
      background: `linear-gradient(90deg, transparent, ${color}, transparent)`,
      opacity: 0.9,
      pointerEvents: "none",
    }} />
  );
};

/** Floating particle field for dark backgrounds */
const Particles = ({ count = 30 }: { count?: number }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const particles = Array.from({ length: count }, (_, i) => {
    const seed1 = (i * 137.508 + 13) % 1;
    const seed2 = (i * 251.312 + 57) % 1;
    const seed3 = (i * 89.731 + 29) % 1;
    const x = seed1 * width;
    const baseY = seed2 * height;
    const speed = 0.3 + seed3 * 0.7;
    const y = ((baseY - frame * speed) % height + height) % height;
    const size = 2 + seed3 * 4;
    const opacity = 0.15 + seed1 * 0.25;
    return { x, y, size, opacity, i };
  });
  return (
    <>
      {particles.map(({ x, y, size, opacity, i }) => (
        <div key={i} style={{
          position: "absolute",
          left: x, top: y,
          width: size, height: size,
          borderRadius: "50%",
          backgroundColor: i % 4 === 0 ? RED : WHITE,
          opacity,
          pointerEvents: "none",
        }} />
      ))}
    </>
  );
};

/** Corner bracket decoration */
const Corners = ({ color = RED, size = 75, opacity = 0.8 }: { color?: string; size?: number; opacity?: number }) => (
  <>
    {[
      { top: 50, left: 50 }, { top: 50, right: 50 },
      { bottom: 50, left: 50 }, { bottom: 50, right: 50 },
    ].map((pos, i) => (
      <div key={i} style={{ position: "absolute", ...pos, width: size, height: size, opacity }}>
        <div style={{ position: "absolute", top: 0, left: 0, width: "100%", height: 3, backgroundColor: color }} />
        <div style={{ position: "absolute", top: 0, left: 0, width: 3, height: "100%", backgroundColor: color }} />
      </div>
    ))}
  </>
);

/** Glitch effect: briefly offset text horizontally */
const GlitchText = ({ text, style }: { text: string; style: React.CSSProperties }) => {
  const frame = useCurrentFrame();
  const glitch = (frame % 47 < 3 || frame % 73 < 2) ? (frame % 2 === 0 ? 6 : -6) : 0;
  const redShift = glitch !== 0 ? 4 : 0;
  return (
    <div style={{ position: "relative" }}>
      {glitch !== 0 && (
        <div style={{ ...style, position: "absolute", color: RED, opacity: 0.6, transform: `translateX(${redShift}px)` }}>
          {text}
        </div>
      )}
      <div style={{ ...style, transform: `translateX(${glitch}px)` }}>{text}</div>
    </div>
  );
};

/** Staggered character reveal */
const CharReveal = ({
  text, style, startFrame, charDelay = 2,
}: {
  text: string; style: React.CSSProperties; startFrame: number; charDelay?: number;
}) => {
  const frame = useCurrentFrame();
  return (
    <div style={{ display: "flex", flexWrap: "wrap", ...style }}>
      {text.split("").map((ch, i) => {
        const charFrame = frame - startFrame - i * charDelay;
        const opacity = interpolate(charFrame, [0, 6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        const y = interpolate(charFrame, [0, 8], [20, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        return (
          <span key={i} style={{ opacity, transform: `translateY(${y}px)`, display: "inline-block", whiteSpace: "pre" }}>
            {ch}
          </span>
        );
      })}
    </div>
  );
};

// ── Scene 1: Intro ────────────────────────────────────────────────────────────
const IntroScene = () => {
  const frame = useCurrentFrame();
  const pulse = useBeatPulse(0.05);

  const logoY = spring({ frame, fps: FPS, config: { damping: 9, stiffness: 160 } });
  const logoScale = interpolate(logoY, [0, 1], [0.5, 1]);
  const logoOpacity = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: "clamp" });

  const ringScale = spring({ frame, fps: FPS, config: { damping: 20, stiffness: 80 } });
  const ringOpacity = interpolate(frame, [5, 40], [0.6, 0], { extrapolateRight: "clamp" });

  const textOpacity = interpolate(frame, [25, 42], [0, 1], { extrapolateRight: "clamp" });
  const redLineW   = interpolate(frame, [38, 55], [0, 1], { extrapolateRight: "clamp" });

  const fadeOut = interpolate(frame, [INTRO_END - 10, INTRO_END], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{
      background: `radial-gradient(ellipse at 50% 45%, #2A0A0E 0%, ${CHARCOAL} 70%)`,
      justifyContent: "center", alignItems: "center", flexDirection: "column",
      opacity: fadeOut,
    }}>
      <Particles count={35} />
      <Corners />

      {/* Shockwave ring */}
      <div style={{
        position: "absolute",
        width: 900 * ringScale, height: 900 * ringScale,
        borderRadius: "50%",
        border: `4px solid ${RED}`,
        opacity: ringOpacity,
      }} />

      {/* Logo with beat pulse */}
      <div style={{
        transform: `scale(${logoScale * pulse})`,
        opacity: logoOpacity,
        filter: "drop-shadow(0 0 70px rgba(200,16,46,0.7)) drop-shadow(0 0 130px rgba(200,16,46,0.3))",
        zIndex: 2,
      }}>
        <Img src={staticFile("images/logo.jpg")} style={{ width: 840, height: 840, objectFit: "contain" }} />
      </div>

      {/* Company name with char reveal */}
      <div style={{ opacity: textOpacity, textAlign: "center", marginTop: -20, zIndex: 3 }}>
        <CharReveal
          text="MONTES PATROL"
          startFrame={25}
          charDelay={3}
          style={{ fontSize: 0, justifyContent: "center" }}
        />
        <div style={{ display: "flex", justifyContent: "center", gap: 16 }}>
          <CharReveal text="MONTES " startFrame={25} charDelay={3}
            style={{ color: WHITE, fontSize: 74, fontFamily: bebas, letterSpacing: 5 }} />
          <CharReveal text="PATROL" startFrame={25 + 7 * 3} charDelay={3}
            style={{ color: RED, fontSize: 74, fontFamily: bebas, letterSpacing: 5 }} />
        </div>

        <div style={{ width: `${redLineW * 340}px`, height: 3, backgroundColor: RED, margin: "8px auto" }} />

        <div style={{
          opacity: interpolate(frame, [55, 70], [0, 1], { extrapolateRight: "clamp" }),
          color: "#8AAAC8", fontSize: 26, fontFamily: oswald, letterSpacing: 14, marginTop: 4,
        }}>
          SECURITY LLC
        </div>
      </div>

      <ScanLine />
    </AbsoluteFill>
  );
};

// ── Scene 2: Tagline ──────────────────────────────────────────────────────────
const TaglineScene = () => {
  const frame = useCurrentFrame();
  const pulse = useBeatPulse(0.025);

  const line1 = spring({ frame, fps: FPS, config: { damping: 10, stiffness: 200 } });
  const line1X = interpolate(line1, [0, 1], [-400, 0]);
  const line2 = spring({ frame: frame - 8, fps: FPS, config: { damping: 10, stiffness: 200 } });
  const line2X = interpolate(line2, [0, 1], [400, 0]);

  const subOpacity = interpolate(frame, [32, 52], [0, 1], { extrapolateRight: "clamp" });
  const subY       = interpolate(frame, [32, 52], [50, 0], { extrapolateRight: "clamp" });
  const lineW      = interpolate(frame, [38, 60], [0, 280], { extrapolateRight: "clamp" });
  const logoScale  = spring({ frame: frame - 50, fps: FPS, config: { damping: 12, stiffness: 160 } });

  return (
    <AbsoluteFill style={{ backgroundColor: WHITE, justifyContent: "center", alignItems: "flex-start", flexDirection: "column" }}>
      <FlashOverlay />
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 14, backgroundColor: RED }} />
      <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: 14, backgroundColor: NAVY }} />

      {/* Animated vertical red stripe */}
      <div style={{
        position: "absolute", top: 14, bottom: 14, left: 0,
        width: interpolate(frame, [0, 20], [1080, 0], { extrapolateRight: "clamp" }),
        backgroundColor: RED, opacity: 0.08,
      }} />

      <div style={{ paddingLeft: 65, paddingRight: 50 }}>
        <div style={{ transform: `translateX(${line1X}px) scale(${pulse})`, transformOrigin: "left center" }}>
          <GlitchText text="YOUR SAFETY" style={{ color: NAVY, fontSize: 126, fontFamily: bebas, letterSpacing: 2, lineHeight: 0.88 }} />
        </div>
        <div style={{ transform: `translateX(${line2X}px) scale(${pulse})`, transformOrigin: "left center" }}>
          <GlitchText text="OUR PRIORITY" style={{ color: RED, fontSize: 126, fontFamily: bebas, letterSpacing: 2, lineHeight: 0.88 }} />
        </div>

        <div style={{ opacity: subOpacity, transform: `translateY(${subY}px)`, marginTop: 46 }}>
          <div style={{ display: "flex", gap: 14, marginBottom: 26 }}>
            <div style={{ width: lineW, height: 4, backgroundColor: NAVY }} />
            <div style={{ width: lineW, height: 4, backgroundColor: RED }} />
          </div>
          <div style={{ color: NAVY, fontSize: 34, fontFamily: oswald, fontWeight: 500, letterSpacing: 4, lineHeight: 1.3 }}>
            PROFESSIONAL SECURITY{"\n"}YOU CAN TRUST
          </div>
        </div>
      </div>

      {/* Logo spin-in bottom right */}
      <div style={{
        position: "absolute", bottom: 55, right: 50,
        transform: `scale(${Math.max(0, logoScale)}) rotate(${interpolate(Math.max(0, logoScale), [0, 1], [-45, 0])}deg)`,
        width: 185, height: 185,
      }}>
        <Img src={staticFile("images/logo.jpg")} style={{ width: "100%", height: "100%", objectFit: "contain" }} />
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 3: Flyer Showcase ───────────────────────────────────────────────────
const FlyerScene = () => {
  const frame = useCurrentFrame();
  const duration = FLYER_END - TAG_END;
  const pulse = useBeatPulse(0.015);

  const scale = interpolate(frame, [0, duration], [1.18, 1.02], { extrapolateRight: "clamp" });
  const fadeIn = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" });

  const badge1Y = spring({ frame: frame - 18, fps: FPS, config: { damping: 12, stiffness: 180 } });
  const badge1T = interpolate(badge1Y, [0, 1], [120, 0]);
  const badge2X = spring({ frame: frame - 32, fps: FPS, config: { damping: 12, stiffness: 160 } });
  const badge2T = interpolate(badge2X, [0, 1], [-300, 0]);
  const badge2Op = interpolate(frame, [32, 50], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: CHARCOAL }}>
      <FlashOverlay />
      <Img
        src={staticFile("images/flyer.jpg")}
        style={{
          width: "100%", height: "100%", objectFit: "cover",
          transform: `scale(${scale * pulse})`, opacity: fadeIn,
        }}
      />
      <AbsoluteFill style={{ background: "linear-gradient(to top, rgba(0,0,0,0.88) 0%, rgba(0,0,0,0.2) 45%, transparent 72%)" }} />
      <ScanLine color={WHITE} />

      {/* Badge 1 - slams from below */}
      <div style={{
        position: "absolute", bottom: 210, left: 0, right: 0,
        display: "flex", justifyContent: "center",
        transform: `translateY(${badge1T}px)`,
      }}>
        <div style={{
          backgroundColor: RED, paddingTop: 18, paddingBottom: 18, paddingLeft: 58, paddingRight: 58,
          borderRadius: 6, boxShadow: "0 6px 40px rgba(200,16,46,0.8)",
        }}>
          <div style={{ color: WHITE, fontSize: 48, fontFamily: bebas, letterSpacing: 9 }}>
            PROTECTING YOUR WORLD
          </div>
        </div>
      </div>

      {/* Badge 2 - slides from left */}
      <div style={{
        position: "absolute", bottom: 105, left: 0, right: 0, display: "flex", justifyContent: "center",
        transform: `translateX(${badge2T}px)`, opacity: badge2Op,
      }}>
        <div style={{ color: WHITE, fontSize: 32, fontFamily: oswald, fontWeight: 300, letterSpacing: 6 }}>
          LICENSED • INSURED • PROFESSIONAL
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ── Scenes 4-7: Service Cards ─────────────────────────────────────────────────
interface ServiceProps {
  iconChar: string; title: string; description: string;
  dark: boolean; entranceDir?: "left" | "right" | "top" | "bottom";
}

const PulseDot = ({ delay = 0 }: { delay?: number }) => {
  const frame = useCurrentFrame();
  const sc = interpolate((frame + delay) % BEAT, [0, BEAT / 2, BEAT], [1, 1.6, 1]);
  const op = interpolate((frame + delay) % BEAT, [0, BEAT / 2, BEAT], [1, 0.25, 1]);
  return <div style={{ width: 16, height: 16, borderRadius: "50%", backgroundColor: RED, transform: `scale(${sc})`, opacity: op }} />;
};

const ServiceScene = ({ iconChar, title, description, dark, entranceDir = "left" }: ServiceProps) => {
  const frame = useCurrentFrame();
  const pulse = useBeatPulse(0.03);

  const iconSp = spring({ frame, fps: FPS, config: { damping: 9, stiffness: 200 } });
  const iconScale = interpolate(iconSp, [0, 1], [0, 1]);

  const textSp = spring({ frame: frame - 12, fps: FPS, config: { damping: 11, stiffness: 160 } });
  const offset = interpolate(textSp, [0, 1], [160, 0]);
  const textTranslate = entranceDir === "left"  ? `translateX(-${offset}px)` :
                        entranceDir === "right" ? `translateX(${offset}px)`  :
                        entranceDir === "top"   ? `translateY(-${offset}px)` :
                                                  `translateY(${offset}px)`;

  const descOp = interpolate(frame, [36, 55], [0, 1], { extrapolateRight: "clamp" });
  const lineW  = interpolate(frame, [28, 48], [0, 250], { extrapolateRight: "clamp" });
  const logoOp = interpolate(frame, [50, 70], [0, 0.6], { extrapolateRight: "clamp" });

  const bg          = dark ? NAVY : LIGHT_GRAY;
  const titleColor  = dark ? WHITE : NAVY;
  const descColor   = dark ? "#8AAAC8" : "#5A6A80";

  return (
    <AbsoluteFill style={{ backgroundColor: bg, justifyContent: "center", alignItems: "center", flexDirection: "column" }}>
      <FlashOverlay />
      {dark && <Particles count={20} />}
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 9, backgroundColor: RED }} />

      {/* Icon circle with beat pulse */}
      <div style={{
        width: 200, height: 200, borderRadius: "50%", backgroundColor: RED,
        display: "flex", alignItems: "center", justifyContent: "center",
        transform: `scale(${iconScale * pulse})`,
        border: `6px solid ${dark ? "#2D4470" : WHITE}`,
        boxShadow: "0 10px 50px rgba(200,16,46,0.45)",
        marginBottom: 50,
      }}>
        <span style={{ fontSize: 96, lineHeight: 1 }}>{iconChar}</span>
      </div>

      <div style={{ transform: textTranslate, textAlign: "center", paddingLeft: 60, paddingRight: 60 }}>
        <div style={{ color: titleColor, fontSize: 68, fontFamily: bebas, letterSpacing: 3, lineHeight: 1 }}>{title}</div>
        <div style={{ width: lineW, height: 4, backgroundColor: RED, margin: "20px auto" }} />
        <div style={{ opacity: descOp, color: descColor, fontSize: 36, fontFamily: oswald, fontWeight: 300, lineHeight: 1.5, letterSpacing: 1 }}>
          {description}
        </div>
      </div>

      {/* Beat dots */}
      <div style={{ position: "absolute", bottom: 55, left: 60, display: "flex", gap: 14 }}>
        <PulseDot delay={0} /><PulseDot delay={5} /><PulseDot delay={10} />
      </div>

      {/* Logo watermark */}
      <div style={{ position: "absolute", bottom: 38, right: 48, opacity: logoOp, width: 82, height: 82 }}>
        <Img src={staticFile("images/logo.jpg")} style={{ width: "100%", height: "100%", objectFit: "contain" }} />
      </div>
    </AbsoluteFill>
  );
};

// ── Scene 8: Outro ────────────────────────────────────────────────────────────
const OutroScene = () => {
  const frame = useCurrentFrame();
  const pulse = useBeatPulse(0.04);

  const logoSp  = spring({ frame, fps: FPS, config: { damping: 9, stiffness: 130 } });
  const logoScale = interpolate(logoSp, [0, 1], [0.3, 1]);
  const logoOp    = interpolate(frame, [0, 18], [0, 1], { extrapolateRight: "clamp" });

  const badgeSp  = spring({ frame: frame - 28, fps: FPS, config: { damping: 10, stiffness: 180 } });
  const badgeScale = interpolate(Math.max(0, badgeSp), [0, 1], [0, 1]);
  const badgeOp    = interpolate(frame, [28, 45], [0, 1], { extrapolateRight: "clamp" });

  const phoneY = spring({ frame: frame - 48, fps: FPS, config: { damping: 14, stiffness: 140 } });
  const phoneT = interpolate(Math.max(0, phoneY), [0, 1], [80, 0]);
  const phoneOp = interpolate(frame, [48, 64], [0, 1], { extrapolateRight: "clamp" });
  const webY  = spring({ frame: frame - 64, fps: FPS, config: { damping: 14, stiffness: 140 } });
  const webT  = interpolate(Math.max(0, webY), [0, 1], [80, 0]);
  const webOp = interpolate(frame, [64, 80], [0, 1], { extrapolateRight: "clamp" });

  const bgGlow = interpolate(frame, [0, 120], [0, 0.28], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{
      background: `radial-gradient(ellipse at 50% 38%, rgba(200,16,46,${bgGlow}) 0%, ${CHARCOAL} 65%)`,
      justifyContent: "center", alignItems: "center", flexDirection: "column",
    }}>
      <FlashOverlay />
      <Particles count={40} />
      <Corners size={80} />

      {/* Logo */}
      <div style={{
        transform: `scale(${logoScale * pulse})`, opacity: logoOp,
        filter: "drop-shadow(0 0 60px rgba(200,16,46,0.65)) drop-shadow(0 0 120px rgba(200,16,46,0.3))",
        marginBottom: 28, zIndex: 2,
      }}>
        <Img src={staticFile("images/logo.jpg")} style={{ width: 580, height: 580, objectFit: "contain" }} />
      </div>

      {/* LICENSED INSURED badge */}
      <div style={{ opacity: badgeOp, transform: `scale(${badgeScale})`, marginBottom: 48, zIndex: 2 }}>
        <div style={{
          backgroundColor: RED, paddingTop: 20, paddingBottom: 20, paddingLeft: 65, paddingRight: 65,
          borderRadius: 8, boxShadow: "0 8px 40px rgba(200,16,46,0.6)",
        }}>
          <div style={{ color: WHITE, fontSize: 48, fontFamily: bebas, letterSpacing: 10 }}>LICENSED • INSURED</div>
        </div>
      </div>

      {/* Phone */}
      <div style={{ opacity: phoneOp, transform: `translateY(${phoneT}px)`, display: "flex", alignItems: "center", gap: 20, marginBottom: 22, zIndex: 2 }}>
        <div style={{ width: 58, height: 58, borderRadius: "50%", backgroundColor: RED, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <span style={{ fontSize: 28 }}>📞</span>
        </div>
        <div style={{ color: WHITE, fontSize: 58, fontFamily: bebas, letterSpacing: 4 }}>(346) 277-2563</div>
      </div>

      {/* Website */}
      <div style={{ opacity: webOp, transform: `translateY(${webT}px)`, display: "flex", alignItems: "center", gap: 20, zIndex: 2 }}>
        <div style={{ width: 58, height: 58, borderRadius: "50%", backgroundColor: CHARCOAL, border: `2px solid ${RED}`, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <span style={{ fontSize: 28 }}>🌐</span>
        </div>
        <div style={{ color: "#9EB8D0", fontSize: 33, fontFamily: oswald, fontWeight: 300, letterSpacing: 1 }}>
          montespatrolsecurityllc.com
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ── Root Composition ──────────────────────────────────────────────────────────
export const PromoVideo: React.FC = () => {
  return (
    <AbsoluteFill>
      {/* Background music */}
      <Audio
        src={staticFile("audio/bg-music.wav")}
        startFrom={0}
        volume={0.72}
      />

      <Sequence from={INTRO_START}  durationInFrames={INTRO_END - INTRO_START}>
        <IntroScene />
      </Sequence>
      <Sequence from={INTRO_END}    durationInFrames={TAG_END - INTRO_END}>
        <TaglineScene />
      </Sequence>
      <Sequence from={TAG_END}      durationInFrames={FLYER_END - TAG_END}>
        <FlyerScene />
      </Sequence>
      <Sequence from={FLYER_END}    durationInFrames={S1_END - FLYER_END}>
        <ServiceScene iconChar="🕐" title="24/7 SECURITY COVERAGE"
          description={"Around-the-clock protection.\nWe never sleep so you can."} dark entranceDir="left" />
      </Sequence>
      <Sequence from={S1_END}       durationInFrames={S2_END - S1_END}>
        <ServiceScene iconChar="⚡" title="FAST RESPONSE TIME"
          description={"Seconds matter in an emergency.\nWe respond before threats escalate."} dark={false} entranceDir="right" />
      </Sequence>
      <Sequence from={S2_END}       durationInFrames={S3_END - S2_END}>
        <ServiceScene iconChar="🛡️" title="ELITE TRAINED GUARDS"
          description={"Certified, professional, and ready.\nYour safety is our mission."} dark entranceDir="bottom" />
      </Sequence>
      <Sequence from={S3_END}       durationInFrames={S4_END - S3_END}>
        <ServiceScene iconChar="🚔" title="MOBILE PATROL SERVICES"
          description={"Visible deterrence. Consistent routes.\nComplete peace of mind."} dark={false} entranceDir="top" />
      </Sequence>
      <Sequence from={S4_END}       durationInFrames={OUTRO_END - S4_END}>
        <OutroScene />
      </Sequence>
    </AbsoluteFill>
  );
};
