import {
  AbsoluteFill,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
} from "remotion";

const oswald = "Oswald, sans-serif";
const bebas = "BebasNeue, Impact, sans-serif";

// Brand colors
const NAVY = "#1B2A4A";
const RED = "#C8102E";
const WHITE = "#FFFFFF";
const LIGHT_GRAY = "#F0F2F5";

const FPS = 30;

const INTRO_END = 3 * FPS;
const TAGLINE_END = 7 * FPS;
const S1_END = 12 * FPS;
const S2_END = 17 * FPS;
const S3_END = 22 * FPS;
const S4_END = 27 * FPS;
const OUTRO_END = 34 * FPS;

export const PROMO_DURATION = OUTRO_END;

// SVG Shield Logo matching brand
const ShieldSVG = ({ size = 280 }: { size?: number }) => {
  const h = size * 1.1;
  return (
    <svg width={size} height={h} viewBox="0 0 200 220">
      {/* Outer glow ring */}
      <ellipse cx="100" cy="110" rx="95" ry="105" fill="none" stroke={RED} strokeWidth="1.5" opacity="0.4" />
      {/* Shield body - right half navy */}
      <path d="M100 12 L178 42 L178 118 C178 166 100 208 100 208 Z" fill={NAVY} />
      {/* Shield body - left half red */}
      <path d="M100 12 L22 42 L22 118 C22 166 100 208 100 208 Z" fill={RED} />
      {/* Shield border */}
      <path d="M100 12 L178 42 L178 118 C178 166 100 208 100 208 C100 208 22 166 22 118 L22 42 Z" fill="none" stroke={WHITE} strokeWidth="3.5" />
      {/* Horizontal divider */}
      <line x1="22" y1="110" x2="178" y2="110" stroke={WHITE} strokeWidth="1.5" opacity="0.3" />
      {/* 5-point star */}
      <polygon
        points="100,52 107,74 131,74 113,88 120,110 100,96 80,110 87,88 69,74 93,74"
        fill={WHITE}
      />
      {/* Left sword */}
      <line x1="30" y1="20" x2="100" y2="90" stroke="#A0A8B8" strokeWidth="4" strokeLinecap="round" />
      <line x1="30" y1="20" x2="22" y2="28" stroke="#A0A8B8" strokeWidth="6" strokeLinecap="round" />
      {/* Right sword */}
      <line x1="170" y1="20" x2="100" y2="90" stroke="#A0A8B8" strokeWidth="4" strokeLinecap="round" />
      <line x1="170" y1="20" x2="178" y2="28" stroke="#A0A8B8" strokeWidth="6" strokeLinecap="round" />
      {/* Stars flanking */}
      <polygon points="40,50 43,59 52,59 45,64 48,73 40,68 32,73 35,64 28,59 37,59" fill={WHITE} opacity="0.7" />
      <polygon points="160,50 163,59 172,59 165,64 168,73 160,68 152,73 155,64 148,59 157,59" fill={WHITE} opacity="0.7" />
    </svg>
  );
};

// Pulsing red dot
const PulseDot = ({ delay = 0 }: { delay?: number }) => {
  const frame = useCurrentFrame();
  const scale = interpolate(
    (frame + delay) % 60,
    [0, 30, 60],
    [1, 1.4, 1],
    { extrapolateRight: "clamp" }
  );
  const opacity = interpolate(
    (frame + delay) % 60,
    [0, 30, 60],
    [0.8, 0.3, 0.8],
    { extrapolateRight: "clamp" }
  );
  return (
    <div style={{
      width: 18, height: 18, borderRadius: "50%",
      backgroundColor: RED,
      transform: `scale(${scale})`,
      opacity,
    }} />
  );
};

// ─── SCENE 1: Intro ──────────────────────────────────────────────────────────
const IntroScene = () => {
  const frame = useCurrentFrame();

  const shieldScale = spring({ frame, fps: FPS, config: { damping: 14, stiffness: 90 } });
  const shieldOpacity = interpolate(frame, [0, 12], [0, 1], { extrapolateRight: "clamp" });

  const titleY = interpolate(frame, [18, 38], [60, 0], { extrapolateRight: "clamp" });
  const titleOpacity = interpolate(frame, [18, 38], [0, 1], { extrapolateRight: "clamp" });

  const lineW = interpolate(frame, [35, 55], [0, 320], { extrapolateRight: "clamp" });
  const llcOpacity = interpolate(frame, [40, 60], [0, 1], { extrapolateRight: "clamp" });

  const bgGlow = interpolate(frame, [0, 90], [0, 0.15], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{
      background: `radial-gradient(ellipse at 50% 40%, rgba(200,16,46,${bgGlow}) 0%, ${NAVY} 65%)`,
      justifyContent: "center",
      alignItems: "center",
      flexDirection: "column",
      gap: 0,
    }}>
      {/* Decorative corner lines */}
      <div style={{ position: "absolute", top: 60, left: 60, width: 80, height: 3, backgroundColor: RED, opacity: 0.6 }} />
      <div style={{ position: "absolute", top: 60, left: 60, width: 3, height: 80, backgroundColor: RED, opacity: 0.6 }} />
      <div style={{ position: "absolute", top: 60, right: 60, width: 80, height: 3, backgroundColor: RED, opacity: 0.6 }} />
      <div style={{ position: "absolute", top: 60, right: 60, width: 3, height: 80, backgroundColor: RED, opacity: 0.6 }} />
      <div style={{ position: "absolute", bottom: 60, left: 60, width: 80, height: 3, backgroundColor: RED, opacity: 0.6 }} />
      <div style={{ position: "absolute", bottom: 60, left: 60, width: 3, height: 80, backgroundColor: RED, opacity: 0.6 }} />
      <div style={{ position: "absolute", bottom: 60, right: 60, width: 80, height: 3, backgroundColor: RED, opacity: 0.6 }} />
      <div style={{ position: "absolute", bottom: 60, right: 60, width: 3, height: 80, backgroundColor: RED, opacity: 0.6 }} />

      <div style={{
        transform: `scale(${shieldScale})`,
        opacity: shieldOpacity,
        filter: "drop-shadow(0 0 40px rgba(200,16,46,0.5))",
      }}>
        <ShieldSVG size={320} />
      </div>

      <div style={{
        marginTop: 36,
        opacity: titleOpacity,
        transform: `translateY(${titleY}px)`,
        textAlign: "center",
      }}>
        <div style={{ display: "flex", justifyContent: "center", alignItems: "baseline", gap: 14 }}>
          <span style={{ color: WHITE, fontSize: 78, fontFamily: bebas, letterSpacing: 6 }}>MONTES</span>
          <span style={{ color: RED, fontSize: 78, fontFamily: bebas, letterSpacing: 6 }}>PATROL</span>
        </div>
      </div>

      <div style={{ opacity: llcOpacity, textAlign: "center", marginTop: 6 }}>
        <div style={{ width: lineW, height: 2, backgroundColor: RED, margin: "0 auto 10px" }} />
        <div style={{ color: "#9EB0CC", fontSize: 26, fontFamily: oswald, fontWeight: 400, letterSpacing: 14 }}>
          SECURITY LLC
        </div>
        <div style={{ width: lineW, height: 2, backgroundColor: RED, margin: "10px auto 0" }} />
      </div>
    </AbsoluteFill>
  );
};

// ─── SCENE 2: Tagline ─────────────────────────────────────────────────────────
const TaglineScene = () => {
  const frame = useCurrentFrame();

  const line1X = interpolate(frame, [0, 22], [-200, 0], { extrapolateRight: "clamp" });
  const line2X = interpolate(frame, [10, 32], [200, 0], { extrapolateRight: "clamp" });
  const subOpacity = interpolate(frame, [28, 50], [0, 1], { extrapolateRight: "clamp" });
  const subY = interpolate(frame, [28, 50], [30, 0], { extrapolateRight: "clamp" });
  const accentW = interpolate(frame, [35, 60], [0, 1], { extrapolateRight: "clamp" });
  const badgeOpacity = interpolate(frame, [50, 70], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{
      backgroundColor: WHITE,
      justifyContent: "center",
      alignItems: "flex-start",
      flexDirection: "column",
    }}>
      {/* Red top accent bar */}
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 12, backgroundColor: RED }} />
      {/* Navy bottom accent bar */}
      <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: 12, backgroundColor: NAVY }} />

      <div style={{ paddingLeft: 70, paddingRight: 50 }}>
        <div style={{ transform: `translateX(${line1X}px)` }}>
          <div style={{
            color: NAVY,
            fontSize: 118,
            fontFamily: bebas,
            letterSpacing: 3,
            lineHeight: 0.92,
          }}>YOUR SAFETY</div>
        </div>
        <div style={{ transform: `translateX(${line2X}px)` }}>
          <div style={{
            color: RED,
            fontSize: 118,
            fontFamily: bebas,
            letterSpacing: 3,
            lineHeight: 0.92,
          }}>OUR PRIORITY</div>
        </div>

        {/* Divider */}
        <div style={{
          opacity: subOpacity,
          transform: `translateY(${subY}px)`,
          marginTop: 40,
        }}>
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: 16,
            marginBottom: 36,
          }}>
            <div style={{ flex: accentW, height: 3, backgroundColor: NAVY, transformOrigin: "left" }} />
            <div style={{ flex: accentW, height: 3, backgroundColor: RED, transformOrigin: "right" }} />
          </div>
          <div style={{
            color: NAVY,
            fontSize: 34,
            fontFamily: oswald,
            fontWeight: 500,
            letterSpacing: 3,
            lineHeight: 1.3,
          }}>
            PROFESSIONAL SECURITY{"\n"}YOU CAN TRUST
          </div>
        </div>
      </div>

      {/* Bottom badge */}
      <div style={{
        position: "absolute",
        bottom: 80,
        left: 70,
        opacity: badgeOpacity,
        display: "flex",
        alignItems: "center",
        gap: 16,
      }}>
        <ShieldSVG size={80} />
        <div style={{ color: NAVY, fontSize: 22, fontFamily: oswald, fontWeight: 400, letterSpacing: 2, opacity: 0.7 }}>
          MONTES PATROL SECURITY LLC
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ─── SCENE 3-6: Service Cards ─────────────────────────────────────────────────
interface ServiceProps {
  iconChar: string;
  title: string;
  description: string;
  dark: boolean;
}

const ServiceScene = ({ iconChar, title, description, dark }: ServiceProps) => {
  const frame = useCurrentFrame();

  const circleScale = spring({ frame, fps: FPS, config: { damping: 16, stiffness: 120 } });
  const textY = interpolate(frame, [12, 32], [80, 0], { extrapolateRight: "clamp" });
  const textOpacity = interpolate(frame, [12, 32], [0, 1], { extrapolateRight: "clamp" });
  const lineW = interpolate(frame, [25, 48], [0, 220], { extrapolateRight: "clamp" });
  const descOpacity = interpolate(frame, [35, 55], [0, 1], { extrapolateRight: "clamp" });

  const bg = dark ? NAVY : LIGHT_GRAY;
  const titleColor = dark ? WHITE : NAVY;
  const descColor = dark ? "#8AAAC8" : "#5A6A80";

  return (
    <AbsoluteFill style={{
      backgroundColor: bg,
      justifyContent: "center",
      alignItems: "center",
      flexDirection: "column",
      gap: 0,
    }}>
      {/* Top red bar */}
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 8, backgroundColor: RED }} />

      {/* Icon circle */}
      <div style={{
        width: 200,
        height: 200,
        borderRadius: "50%",
        backgroundColor: RED,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        transform: `scale(${circleScale})`,
        border: `6px solid ${dark ? "#2D4470" : WHITE}`,
        boxShadow: "0 8px 40px rgba(200,16,46,0.35)",
        marginBottom: 50,
      }}>
        <span style={{ fontSize: 96, lineHeight: 1 }}>{iconChar}</span>
      </div>

      {/* Text */}
      <div style={{
        transform: `translateY(${textY}px)`,
        opacity: textOpacity,
        textAlign: "center",
        paddingLeft: 60,
        paddingRight: 60,
      }}>
        <div style={{
          color: titleColor,
          fontSize: 68,
          fontFamily: bebas,
          letterSpacing: 3,
          lineHeight: 1,
        }}>{title}</div>

        <div style={{
          width: lineW,
          height: 3,
          backgroundColor: RED,
          margin: "22px auto",
        }} />

        <div style={{
          opacity: descOpacity,
          color: descColor,
          fontSize: 36,
          fontFamily: oswald,
          fontWeight: 300,
          lineHeight: 1.45,
          letterSpacing: 1,
        }}>{description}</div>
      </div>

      {/* Bottom left dots */}
      <div style={{
        position: "absolute",
        bottom: 55,
        left: 60,
        display: "flex",
        gap: 12,
        alignItems: "center",
      }}>
        <PulseDot delay={0} />
        <PulseDot delay={20} />
        <PulseDot delay={40} />
      </div>

      {/* Bottom right brand */}
      <div style={{
        position: "absolute",
        bottom: 48,
        right: 55,
        opacity: descOpacity * 0.6,
      }}>
        <ShieldSVG size={55} />
      </div>
    </AbsoluteFill>
  );
};

// ─── SCENE 7: Outro / Contact ─────────────────────────────────────────────────
const OutroScene = () => {
  const frame = useCurrentFrame();

  const shieldScale = spring({ frame, fps: FPS, config: { damping: 14, stiffness: 80 } });
  const nameOpacity = interpolate(frame, [15, 35], [0, 1], { extrapolateRight: "clamp" });
  const nameY = interpolate(frame, [15, 35], [40, 0], { extrapolateRight: "clamp" });

  const badgeOpacity = interpolate(frame, [35, 55], [0, 1], { extrapolateRight: "clamp" });
  const badgeScale = spring({ frame: frame - 35, fps: FPS, config: { damping: 16, stiffness: 100 } });

  const phoneOpacity = interpolate(frame, [52, 68], [0, 1], { extrapolateRight: "clamp" });
  const phoneY = interpolate(frame, [52, 68], [30, 0], { extrapolateRight: "clamp" });
  const webOpacity = interpolate(frame, [64, 80], [0, 1], { extrapolateRight: "clamp" });
  const webY = interpolate(frame, [64, 80], [30, 0], { extrapolateRight: "clamp" });

  const bgGlow = interpolate(frame, [0, 100], [0, 0.2], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{
      background: `radial-gradient(ellipse at 50% 35%, rgba(200,16,46,${bgGlow}) 0%, ${NAVY} 60%)`,
      justifyContent: "center",
      alignItems: "center",
      flexDirection: "column",
    }}>
      {/* Corner accents */}
      {[
        { top: 60, left: 60 },
        { top: 60, right: 60 },
        { bottom: 60, left: 60 },
        { bottom: 60, right: 60 },
      ].map((pos, i) => (
        <div key={i} style={{ position: "absolute", ...pos }}>
          <div style={{ position: "relative", width: 70, height: 70 }}>
            <div style={{ position: "absolute", top: 0, left: 0, width: "100%", height: 3, backgroundColor: RED, opacity: 0.7 }} />
            <div style={{ position: "absolute", top: 0, left: 0, width: 3, height: "100%", backgroundColor: RED, opacity: 0.7 }} />
          </div>
        </div>
      ))}

      {/* Shield */}
      <div style={{
        transform: `scale(${shieldScale})`,
        filter: "drop-shadow(0 0 50px rgba(200,16,46,0.5))",
        marginBottom: 28,
      }}>
        <ShieldSVG size={240} />
      </div>

      {/* Company name */}
      <div style={{
        opacity: nameOpacity,
        transform: `translateY(${nameY}px)`,
        textAlign: "center",
        marginBottom: 40,
      }}>
        <div style={{ display: "flex", justifyContent: "center", gap: 12 }}>
          <span style={{ color: WHITE, fontSize: 66, fontFamily: bebas, letterSpacing: 5 }}>MONTES</span>
          <span style={{ color: RED, fontSize: 66, fontFamily: bebas, letterSpacing: 5 }}>PATROL</span>
        </div>
        <div style={{ color: "#7A9ABB", fontSize: 22, fontFamily: oswald, fontWeight: 300, letterSpacing: 12 }}>
          SECURITY LLC
        </div>
      </div>

      {/* Licensed & Insured badge */}
      <div style={{
        opacity: badgeOpacity,
        transform: `scale(${Math.max(0, badgeScale)})`,
        backgroundColor: RED,
        paddingTop: 18,
        paddingBottom: 18,
        paddingLeft: 55,
        paddingRight: 55,
        borderRadius: 8,
        marginBottom: 48,
        boxShadow: "0 6px 30px rgba(200,16,46,0.5)",
      }}>
        <div style={{ color: WHITE, fontSize: 44, fontFamily: bebas, letterSpacing: 8 }}>
          LICENSED • INSURED
        </div>
      </div>

      {/* Contact info */}
      <div style={{
        opacity: phoneOpacity,
        transform: `translateY(${phoneY}px)`,
        display: "flex",
        alignItems: "center",
        gap: 18,
        marginBottom: 20,
      }}>
        <div style={{
          width: 52, height: 52, borderRadius: "50%",
          backgroundColor: RED,
          display: "flex", alignItems: "center", justifyContent: "center",
        }}>
          <span style={{ fontSize: 26 }}>📞</span>
        </div>
        <div style={{ color: WHITE, fontSize: 52, fontFamily: bebas, letterSpacing: 4 }}>
          (346) 277-2563
        </div>
      </div>

      <div style={{
        opacity: webOpacity,
        transform: `translateY(${webY}px)`,
        display: "flex",
        alignItems: "center",
        gap: 18,
      }}>
        <div style={{
          width: 52, height: 52, borderRadius: "50%",
          backgroundColor: NAVY,
          border: `2px solid ${RED}`,
          display: "flex", alignItems: "center", justifyContent: "center",
        }}>
          <span style={{ fontSize: 26 }}>🌐</span>
        </div>
        <div style={{ color: "#9EB8D0", fontSize: 30, fontFamily: oswald, fontWeight: 300, letterSpacing: 1 }}>
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

      <Sequence from={TAGLINE_END} durationInFrames={S1_END - TAGLINE_END}>
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
