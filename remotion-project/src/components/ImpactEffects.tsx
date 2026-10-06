/**
 * 冲击特效组件库 v1.0
 * 打斗/冲击/粒子特效，支持透明背景输出
 *
 * 组件清单：
 * - PunchImpact: 拳击冲击效果（冲击波+星星+震动）
 * - ImpactFlash: 冲击闪光（白闪+放射光线）
 * - ParticleBurst: 粒子爆发（星星/碎片/火花）
 * - Shockwave: 冲击波（扩散圆环）
 * - ScreenShake: 画面震动（包裹子元素）
 * - SpeedLines: 速度线（冲击瞬间）
 */

import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

// 手动缓动函数
const easeOut = (t: number) => 1 - Math.pow(1 - t, 3);
const easeIn = (t: number) => t * t * t;

// ============= PunchImpact: 拳击冲击 =============

export interface PunchImpactProps {
  startFrame?: number;
  x?: number;
  y?: number;
  scale?: number;
  style?: React.CSSProperties;
}

export const PunchImpact: React.FC<PunchImpactProps> = ({
  startFrame = 0,
  x = 540,
  y = 960,
  scale = 1,
  style = {},
}) => {
  const frame = useCurrentFrame();
  const t = Math.min(Math.max((frame - startFrame) / 20, 0), 1);

  if (t <= 0) return null;

  const ringScale = interpolate(t, [0, 1], [0.1, 2.5], {
    easing: easeOut,
    extrapolateRight: "clamp",
  });
  const ringOpacity = interpolate(t, [0, 0.3, 1], [0, 1, 0], {
    extrapolateRight: "clamp",
  });
  const flashOpacity = interpolate(t, [0, 0.1, 0.4], [0, 1, 0], {
    extrapolateRight: "clamp",
  });
  const starScale = interpolate(t, [0, 0.2, 0.6, 1], [0, 1.5, 1, 0.5], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ pointerEvents: "none", ...style }}>
      {/* 冲击波圆环 */}
      <div
        style={{
          position: "absolute",
          left: x,
          top: y,
          width: 200 * scale,
          height: 200 * scale,
          marginLeft: -100 * scale,
          marginTop: -100 * scale,
          borderRadius: "50%",
          border: `${8 * scale}px solid #ffcc00`,
          transform: `scale(${ringScale})`,
          opacity: ringOpacity,
          boxShadow: `0 0 ${30 * scale}px #ffcc00`,
        }}
      />
      {/* 白闪 */}
      <div
        style={{
          position: "absolute",
          left: x,
          top: y,
          width: 150 * scale,
          height: 150 * scale,
          marginLeft: -75 * scale,
          marginTop: -75 * scale,
          borderRadius: "50%",
          backgroundColor: "#ffffff",
          opacity: flashOpacity,
          boxShadow: `0 0 ${50 * scale}px #ffffff`,
        }}
      />
      {/* 星星 */}
      {[0, 60, 120, 180, 240, 300].map((angle, i) => {
        const dist = interpolate(t, [0, 1], [0, 120 * scale], {
          easing: easeOut,
        });
        const sx = x + Math.cos((angle * Math.PI) / 180) * dist;
        const sy = y + Math.sin((angle * Math.PI) / 180) * dist;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: sx,
              top: sy,
              fontSize: `${30 * scale * starScale}px`,
              opacity: ringOpacity,
              transform: `translate(-50%, -50%) rotate(${angle + t * 180}deg)`,
            }}
          >
            ⭐
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// ============= ImpactFlash: 冲击闪光 =============

export interface ImpactFlashProps {
  startFrame?: number;
  duration?: number;
  color?: string;
  style?: React.CSSProperties;
}

export const ImpactFlash: React.FC<ImpactFlashProps> = ({
  startFrame = 0,
  duration = 8,
  color = "#ffffff",
  style = {},
}) => {
  const frame = useCurrentFrame();
  const t = Math.min(Math.max((frame - startFrame) / duration, 0), 1);

  const opacity = interpolate(t, [0, 0.1, 0.5, 1], [0, 1, 0.6, 0], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: color,
        opacity,
        ...style,
      }}
    />
  );
};

// ============= ParticleBurst: 粒子爆发 =============

export interface ParticleBurstProps {
  startFrame?: number;
  x?: number;
  y?: number;
  count?: number;
  particleType?: "star" | "spark" | "debris" | "circle";
  color?: string;
  maxDistance?: number;
  duration?: number;
  style?: React.CSSProperties;
}

export const ParticleBurst: React.FC<ParticleBurstProps> = ({
  startFrame = 0,
  x = 540,
  y = 960,
  count = 12,
  particleType = "star",
  color = "#ffcc00",
  maxDistance = 200,
  duration = 30,
  style = {},
}) => {
  const frame = useCurrentFrame();
  const t = Math.min(Math.max((frame - startFrame) / duration, 0), 1);

  if (t <= 0) return null;

  const particles = Array.from({ length: count }, (_, i) => {
    const angle = (i / count) * 360 + (i % 2) * 15;
    const speed = 0.5 + (i % 3) * 0.2;
    const dist = interpolate(t, [0, 1], [0, maxDistance * speed], {
      easing: easeOut,
    });
    const px = x + Math.cos((angle * Math.PI) / 180) * dist;
    const py = y + Math.sin((angle * Math.PI) / 180) * dist - t * t * 50; // 重力
    const opacity = interpolate(t, [0, 0.3, 1], [0, 1, 0], {
      extrapolateRight: "clamp",
    });
    const size = interpolate(t, [0, 0.2, 1], [0, 1, 0.3], {
      extrapolateRight: "clamp",
    });
    const rotation = t * 360 * (i % 2 === 0 ? 1 : -1);

    let content = "⭐";
    let fontSize = 24;
    if (particleType === "spark") {
      content = "✦";
      fontSize = 20;
    } else if (particleType === "debris") {
      content = "◆";
      fontSize = 18;
    } else if (particleType === "circle") {
      content = "";
    }

    return { px, py, opacity, size, rotation, content, fontSize, i };
  });

  return (
    <AbsoluteFill style={{ pointerEvents: "none", ...style }}>
      {particles.map((p) => (
        <div
          key={p.i}
          style={{
            position: "absolute",
            left: p.px,
            top: p.py,
            fontSize: p.fontSize * p.size,
            color,
            opacity: p.opacity,
            transform: `translate(-50%, -50%) rotate(${p.rotation}deg)`,
            backgroundColor: particleType === "circle" ? color : "transparent",
            borderRadius: particleType === "circle" ? "50%" : 0,
            width: particleType === "circle" ? 12 * p.size : "auto",
            height: particleType === "circle" ? 12 * p.size : "auto",
          }}
        >
          {p.content}
        </div>
      ))}
    </AbsoluteFill>
  );
};

// ============= Shockwave: 冲击波 =============

export interface ShockwaveProps {
  startFrame?: number;
  x?: number;
  y?: number;
  maxRadius?: number;
  color?: string;
  duration?: number;
  ringCount?: number;
  style?: React.CSSProperties;
}

export const Shockwave: React.FC<ShockwaveProps> = ({
  startFrame = 0,
  x = 540,
  y = 960,
  maxRadius = 300,
  color = "#00ffff",
  duration = 25,
  ringCount = 3,
  style = {},
}) => {
  const frame = useCurrentFrame();
  const t = Math.min(Math.max((frame - startFrame) / duration, 0), 1);

  if (t <= 0) return null;

  return (
    <AbsoluteFill style={{ pointerEvents: "none", ...style }}>
      {Array.from({ length: ringCount }, (_, i) => {
        const delay = i * 0.15;
        const ringT = Math.max(0, t - delay);
        const radius = interpolate(ringT, [0, 1], [10, maxRadius], {
          easing: easeOut,
          extrapolateRight: "clamp",
        });
        const opacity = interpolate(ringT, [0, 0.2, 1], [0, 0.8, 0], {
          extrapolateRight: "clamp",
        });
        const borderWidth = interpolate(ringT, [0, 1], [8, 1], {
          extrapolateRight: "clamp",
        });

        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x,
              top: y,
              width: radius * 2,
              height: radius * 2,
              marginLeft: -radius,
              marginTop: -radius,
              borderRadius: "50%",
              border: `${borderWidth}px solid ${color}`,
              opacity,
              boxShadow: `0 0 ${20}px ${color}`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

// ============= SpeedLines: 速度线 =============

export interface SpeedLinesProps {
  startFrame?: number;
  duration?: number;
  x?: number;
  y?: number;
  count?: number;
  color?: string;
  style?: React.CSSProperties;
}

export const SpeedLines: React.FC<SpeedLinesProps> = ({
  startFrame = 0,
  duration = 10,
  x = 540,
  y = 960,
  count = 8,
  color = "#ffffff",
  style = {},
}) => {
  const frame = useCurrentFrame();
  const t = Math.min(Math.max((frame - startFrame) / duration, 0), 1);

  if (t <= 0 || t >= 1) return null;

  const opacity = interpolate(t, [0, 0.2, 0.8, 1], [0, 1, 1, 0], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ pointerEvents: "none", opacity, ...style }}>
      {Array.from({ length: count }, (_, i) => {
        const angle = (i / count) * 360;
        const length = interpolate(t, [0, 1], [20, 200], {
          easing: easeOut,
        });
        const thickness = interpolate(t, [0, 1], [6, 1]);

        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x,
              top: y,
              width: length,
              height: thickness,
              backgroundColor: color,
              transformOrigin: "left center",
              transform: `rotate(${angle}deg)`,
              opacity: 0.8,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};
