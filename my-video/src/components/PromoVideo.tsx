import {
  AbsoluteFill,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
} from "remotion";

const oswald = "Oswald, sans-serif";
const bebas = "BebasNeue, Impact, sans-serif";

// Brand colors
const NAVY = "#1B2A4A";
const RED = "#C8102E";
const WHITE = "#FFFFFF";
const CHARCOAL = "#1A1A1F";
const LIGHT_GRAY = "#F0F2F5";

const FPS = 30;

const INTRO_END    = 4  * FPS;   //  0-4s   logo reveal
const TAGLINE_END  = 8  * FPS;   //  4-8s   tagline
const FLYER_END    = 12 * FPS;   //  8-12s  flyer showcase
const S1_END       = 17 * FPS;   // 12-17s  24/7
const S2_END       = 22 * FPS;   // 17-22s  fast response
const S3_END       = 27 * FPS;   // 22-27s  elite guards
const S4_END       = 32 * FPS;   // 27-32s  mobile patrol
const OUTRO_END    = 39 * FPS;   // 32-39s  outro + contact

export const PROMO_DURATION = OUTRO_END;

// ─── SCENE 1: Logo Intro ──────────────────────────────────────────────────────
const IntroScene = () => {
  const frame = useCurrentFrame();

  const logoScale = spring({ frame, fps: FPS, config: { damping: 18, stiffness: 70 } });
  const logoOpacity = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });

  // Glowing ring pulse
  const glowOpacity = interpolate((frame * 2) % 60, [0, 30, 60], [0.3, 0.8, 0.3]);

  // Fade out at end
  const sceneOpacity = interpolate(frame, [INTRO_END - 15, INTRO_END], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: CHARCOAL, justifyContent: "center", alignItems: "center", opacity: sceneOpacity }}>
      {/* Pulsing glow behind logo */}
      <div style={{
        position: "absolute",
        width: 700,
        height: 700,
        borderRadius: "50%",
        background: `radial-gradient(circle, rgba(200,16,46,${glowOpacity}) 0%, transparent 70%)`,
      }} />

      {/* Corner frame lines */}
      {[
        { top: 50, left: 50 }, { top: 50, right: 50 },
        { bottom: 50, left: 50 }, { bottom: 50, right: 50 },
      ].map((pos, i) => (
        <div key={i} style={{ position: "absolute", ...pos, width: 80, height: 80 }}>
          <div style={{ position: "absolute", top: 0, left: 0, width: "100%", height: 3, backgroundColor: RED, opacity: 0.8 }} />
          <div style={{ position: "absolute", top: 0, left: 0, width: 3, height: "100%", backgroundColor: RED, opacity: 0.8 }} />
        </div>
      ))}

      {/* Actual logo image */}
      <div style={{
        transform: `scale(${logoScale})`,
        opacity: logoOpacity,
        filter: "drop-shadow(0 0 60px rgba(200,16,46,0.6)) drop-shadow(0 0 120px rgba(200,16,46,0.3))",
      }}>
        <Img
          src={staticFile("images/logo.jpg")}
          style={{ width: 820, height: 820, objectFit: "contain" }}
        />
      </div>
    </AbsoluteFill>
  );
};

// ─── SCENE 2: Tagline ─────────────────────────────────────────────────────────
const TaglineScene = () => {
  const frame = useCurrentFrame();

  const line1X = interpolate(frame, [0, 22], [-300, 0], { extrapolateRight: "clamp" });
  const line2X = interpolate(frame, [10, 32], [300, 0], { extrapolateRight: "clamp" });
  const subOpacity = interpolate(frame, [30, 50], [0, 1], { extrapolateRight: "clamp" });
  const subY = interpolate(frame, [30, 50], [40, 0], { extrapolateRight: "clamp" });
  const logoOpacity = interpolate(frame, [45, 65], [0, 1], { extrapolateRight: "clamp" });
  const lineW = interpolate(frame, [35, 58], [0, 260], { extrapolateRight: "clamp" });

  const sceneOpacity = interpolate(frame, [TAGLINE_END - FLYER_END - 15, TAGLINE_END - FLYER_END], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{
      backgroundColor: WHITE,
      justifyContent: "center",
      alignItems: "flex-start",
      flexDirection: "column",
      opacity: sceneOpacity,
    }}>
      {/* Red top bar */}
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 14, backgroundColor: RED }} />
      {/* Navy bottom bar */}
      <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: 14, backgroundColor: NAVY }} />

      <div style={{ paddingLeft: 65, paddingRight: 50 }}>
        <div style={{ transform: `translateX(${line1X}px)`, overflow: "hidden" }}>
          <div style={{ color: NAVY, fontSize: 124, fontFamily: bebas, letterSpacing: 2, lineHeight: 0.9 }}>
            YOUR SAFETY
          </div>
        </div>
        <div style={{ transform: `translateX(${line2X}px)`, overflow: "hidden" }}>
          <div style={{ color: RED, fontSize: 124, fontFamily: bebas, letterSpacing: 2, lineHeight: 0.9 }}>
            OUR PRIORITY
          </div>
        </div>

        <div style={{ opacity: subOpacity, transform: `translateY(${subY}px)`, marginTop: 44 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 30 }}>
            <div style={{ width: lineW, height: 3, backgroundColor: NAVY }} />
            <div style={{ width: lineW, height: 3, backgroundColor: RED }} />
          </div>
          <div style={{ color: NAVY, fontSize: 33, fontFamily: oswald, fontWeight: 500, letterSpacing: 4, lineHeight: 1.3 }}>
            PROFESSIONAL SECURITY{"\n"}YOU CAN TRUST
          </div>
        </div>
      </div>

      {/* Logo small bottom right */}
      <div style={{
        position: "absolute",
        bottom: 60,
        right: 55,
        opacity: logoOpacity,
        width: 180,
        height: 180,
      }}>
        <Img src={staticFile("images/logo.jpg")} style={{ width: "100%", height: "100%", objectFit: "contain" }} />
      </div>
    </AbsoluteFill>
  );
};

// ─── SCENE 3: Flyer Showcase ──────────────────────────────────────────────────
const FlyerScene = () => {
  const frame = useCurrentFrame();
  const duration = FLYER_END - TAGLINE_END;

  // Ken Burns: slow zoom in on flyer
  const scale = interpolate(frame, [0, duration], [1, 1.12], { extrapolateRight: "clamp" });
  const overlayOpacity = interpolate(frame, [0, 20], [0.6, 0], { extrapolateRight: "clamp" });

  // Animated text overlays
  const badge1Opacity = interpolate(frame, [20, 38], [0, 1], { extrapolateRight: "clamp" });
  const badge1Y = interpolate(frame, [20, 38], [50, 0], { extrapolateRight: "clamp" });
  const badge2Opacity = interpolate(frame, [38, 56], [0, 1], { extrapolateRight: "clamp" });
  const badge2Y = interpolate(frame, [38, 56], [50, 0], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ overflow: "hidden", backgroundColor: CHARCOAL }}>
      {/* Flyer image with Ken Burns zoom */}
      <Img
        src={staticFile("images/flyer.jpg")}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${scale})`,
          transformOrigin: "center center",
        }}
      />

      {/* Dark fade-in overlay at start */}
      <AbsoluteFill style={{ backgroundColor: `rgba(0,0,0,${overlayOpacity})` }} />

      {/* Bottom gradient for badges */}
      <AbsoluteFill style={{
        background: "linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.3) 40%, transparent 70%)",
      }} />

      {/* Badge 1 */}
      <div style={{
        position: "absolute",
        bottom: 220,
        left: 0, right: 0,
        opacity: badge1Opacity,
        transform: `translateY(${badge1Y}px)`,
        display: "flex",
        justifyContent: "center",
      }}>
        <div style={{
          backgroundColor: RED,
          paddingTop: 16, paddingBottom: 16,
          paddingLeft: 55, paddingRight: 55,
          borderRadius: 6,
          boxShadow: "0 4px 30px rgba(200,16,46,0.7)",
        }}>
          <div style={{ color: WHITE, fontSize: 46, fontFamily: bebas, letterSpacing: 8 }}>
            PROTECTING YOUR WORLD
          </div>
        </div>
      </div>

      {/* Badge 2 */}
      <div style={{
        position: "absolute",
        bottom: 110,
        left: 0, right: 0,
        opacity: badge2Opacity,
        transform: `translateY(${badge2Y}px)`,
        display: "flex",
        justifyContent: "center",
      }}>
        <div style={{ color: WHITE, fontSize: 30, fontFamily: oswald, fontWeight: 300, letterSpacing: 5, opacity: 0.9 }}>
          LICENSED • INSURED • PROFESSIONAL
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ─── SCENES 4-7: Service Cards ────────────────────────────────────────────────
interface ServiceProps {
  iconChar: string;
  title: string;
  description: string;
  dark: boolean;
}

const PulseDot = ({ delay = 0 }: { delay?: number }) => {
  const frame = useCurrentFrame();
  const scale = interpolate((frame + delay) % 60, [0, 30, 60], [1, 1.45, 1]);
  const opacity = interpolate((frame + delay) % 60, [0, 30, 60], [0.8, 0.25, 0.8]);
  return (
    <div style={{
      width: 16, height: 16, borderRadius: "50%",
      backgroundColor: RED,
      transform: `scale(${scale})`,
      opacity,
    }} />
  );
};

const ServiceScene = ({ iconChar, title, description, dark }: ServiceProps) => {
  const frame = useCurrentFrame();

  const circleScale = spring({ frame, fps: FPS, config: { damping: 16, stiffness: 120 } });
  const textY = interpolate(frame, [14, 34], [80, 0], { extrapolateRight: "clamp" });
  const textOpacity = interpolate(frame, [14, 34], [0, 1], { extrapolateRight: "clamp" });
  const lineW = interpolate(frame, [28, 50], [0, 240], { extrapolateRight: "clamp" });
  const descOpacity = interpolate(frame, [38, 58], [0, 1], { extrapolateRight: "clamp" });
  const logoOpacity = interpolate(frame, [50, 70], [0, 0.55], { extrapolateRight: "clamp" });

  const bg = dark ? NAVY : LIGHT_GRAY;
  const titleColor = dark ? WHITE : NAVY;
  const descColor = dark ? "#8AAAC8" : "#5A6A80";

  return (
    <AbsoluteFill style={{ backgroundColor: bg, justifyContent: "center", alignItems: "center", flexDirection: "column" }}>
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 8, backgroundColor: RED }} />

      {/* Icon circle */}
      <div style={{
        width: 200, height: 200, borderRadius: "50%",
        backgroundColor: RED,
        display: "flex", alignItems: "center", justifyContent: "center",
        transform: `scale(${circleScale})`,
        border: `6px solid ${dark ? "#2D4470" : WHITE}`,
        boxShadow: "0 8px 40px rgba(200,16,46,0.4)",
        marginBottom: 50,
      }}>
        <span style={{ fontSize: 96, lineHeight: 1 }}>{iconChar}</span>
      </div>

      {/* Text block */}
      <div style={{ transform: `translateY(${textY}px)`, opacity: textOpacity, textAlign: "center", paddingLeft: 60, paddingRight: 60 }}>
        <div style={{ color: titleColor, fontSize: 66, fontFamily: bebas, letterSpacing: 3, lineHeight: 1 }}>{title}</div>
        <div style={{ width: lineW, height: 3, backgroundColor: RED, margin: "20px auto" }} />
        <div style={{ opacity: descOpacity, color: descColor, fontSize: 36, fontFamily: oswald, fontWeight: 300, lineHeight: 1.5, letterSpacing: 1 }}>
          {description}
        </div>
      </div>

      {/* Pulse dots */}
      <div style={{ position: "absolute", bottom: 55, left: 60, display: "flex", gap: 14, alignItems: "center" }}>
        <PulseDot delay={0} /><PulseDot delay={20} /><PulseDot delay={40} />
      </div>

      {/* Logo watermark bottom right */}
      <div style={{ position: "absolute", bottom: 40, right: 50, opacity: logoOpacity, width: 80, height: 80 }}>
        <Img src={staticFile("images/logo.jpg")} style={{ width: "100%", height: "100%", objectFit: "contain" }} />
      </div>
    </AbsoluteFill>
  );
};

// ─── SCENE 8: Outro ───────────────────────────────────────────────────────────
const OutroScene = () => {
  const frame = useCurrentFrame();

  const logoScale = spring({ frame, fps: FPS, config: { damping: 14, stiffness: 80 } });
  const logoOpacity = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp" });

  const badgeOpacity = interpolate(frame, [28, 48], [0, 1], { extrapolateRight: "clamp" });
  const badgeScale = spring({ frame: frame - 28, fps: FPS, config: { damping: 16, stiffness: 100 } });

  const phoneOpacity = interpolate(frame, [50, 68], [0, 1], { extrapolateRight: "clamp" });
  const phoneY = interpolate(frame, [50, 68], [40, 0], { extrapolateRight: "clamp" });
  const webOpacity = interpolate(frame, [65, 82], [0, 1], { extrapolateRight: "clamp" });
  const webY = interpolate(frame, [65, 82], [40, 0], { extrapolateRight: "clamp" });

  const bgGlow = interpolate(frame, [0, 120], [0, 0.22], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{
      background: `radial-gradient(ellipse at 50% 35%, rgba(200,16,46,${bgGlow}) 0%, ${CHARCOAL} 65%)`,
      justifyContent: "center",
      alignItems: "center",
      flexDirection: "column",
    }}>
      {/* Corner accents */}
      {[{ top: 55, left: 55 }, { top: 55, right: 55 }, { bottom: 55, left: 55 }, { bottom: 55, right: 55 }].map((pos, i) => (
        <div key={i} style={{ position: "absolute", ...pos, width: 75, height: 75 }}>
          <div style={{ position: "absolute", top: 0, left: 0, width: "100%", height: 3, backgroundColor: RED, opacity: 0.75 }} />
          <div style={{ position: "absolute", top: 0, left: 0, width: 3, height: "100%", backgroundColor: RED, opacity: 0.75 }} />
        </div>
      ))}

      {/* Logo */}
      <div style={{
        transform: `scale(${logoScale})`,
        opacity: logoOpacity,
        filter: "drop-shadow(0 0 55px rgba(200,16,46,0.55)) drop-shadow(0 0 110px rgba(200,16,46,0.25))",
        marginBottom: 30,
      }}>
        <Img
          src={staticFile("images/logo.jpg")}
          style={{ width: 600, height: 600, objectFit: "contain" }}
        />
      </div>

      {/* Licensed & Insured badge */}
      <div style={{
        opacity: badgeOpacity,
        transform: `scale(${Math.max(0, badgeScale)})`,
        backgroundColor: RED,
        paddingTop: 18, paddingBottom: 18,
        paddingLeft: 60, paddingRight: 60,
        borderRadius: 8,
        marginBottom: 50,
        boxShadow: "0 6px 35px rgba(200,16,46,0.55)",
      }}>
        <div style={{ color: WHITE, fontSize: 46, fontFamily: bebas, letterSpacing: 9 }}>
          LICENSED • INSURED
        </div>
      </div>

      {/* Phone */}
      <div style={{ opacity: phoneOpacity, transform: `translateY(${phoneY}px)`, display: "flex", alignItems: "center", gap: 20, marginBottom: 22 }}>
        <div style={{ width: 56, height: 56, borderRadius: "50%", backgroundColor: RED, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <span style={{ fontSize: 28 }}>📞</span>
        </div>
        <div style={{ color: WHITE, fontSize: 56, fontFamily: bebas, letterSpacing: 4 }}>(346) 277-2563</div>
      </div>

      {/* Website */}
      <div style={{ opacity: webOpacity, transform: `translateY(${webY}px)`, display: "flex", alignItems: "center", gap: 20 }}>
        <div style={{ width: 56, height: 56, borderRadius: "50%", backgroundColor: CHARCOAL, border: `2px solid ${RED}`, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <span style={{ fontSize: 28 }}>🌐</span>
        </div>
        <div style={{ color: "#9EB8D0", fontSize: 32, fontFamily: oswald, fontWeight: 300, letterSpacing: 1 }}>
          montespatrolsecurityllc.com
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ─── Root Composition ─────────────────────────────────────────────────────────
export const PromoVideo: React.FC = () => {
  return (
    <AbsoluteFill>
      <Sequence durationInFrames={INTRO_END}>
        <IntroScene />
      </Sequence>

      <Sequence from={INTRO_END} durationInFrames={TAGLINE_END - INTRO_END}>
        <TaglineScene />
      </Sequence>

      <Sequence from={TAGLINE_END} durationInFrames={FLYER_END - TAGLINE_END}>
        <FlyerScene />
      </Sequence>

      <Sequence from={FLYER_END} durationInFrames={S1_END - FLYER_END}>
        <ServiceScene
          iconChar="🕐"
          title="24/7 SECURITY COVERAGE"
          description={"Around-the-clock protection.\nWe never sleep so you can."}
          dark
        />
      </Sequence>

      <Sequence from={S1_END} durationInFrames={S2_END - S1_END}>
        <ServiceScene
          iconChar="⚡"
          title="FAST RESPONSE TIME"
          description={"Seconds matter in an emergency.\nWe respond before threats escalate."}
          dark={false}
        />
      </Sequence>

      <Sequence from={S2_END} durationInFrames={S3_END - S2_END}>
        <ServiceScene
          iconChar="🛡️"
          title="ELITE TRAINED GUARDS"
          description={"Certified, professional, and ready.\nYour safety is our mission."}
          dark
        />
      </Sequence>

      <Sequence from={S3_END} durationInFrames={S4_END - S3_END}>
        <ServiceScene
          iconChar="🚔"
          title="MOBILE PATROL SERVICES"
          description={"Visible deterrence. Consistent routes.\nComplete peace of mind."}
          dark={false}
        />
      </Sequence>

      <Sequence from={S4_END} durationInFrames={OUTRO_END - S4_END}>
        <OutroScene />
      </Sequence>
    </AbsoluteFill>
  );
};
