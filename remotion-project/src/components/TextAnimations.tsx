/**
 * 文字动画组件库 v1.0
 * 专业级字幕/标题动画，支持透明背景输出
 *
 * 组件清单：
 * - TextReveal: 逐字显现（打字机/淡入/滑动）
 * - TextPop: 弹出文字（弹性缩放/旋转）
 * - TextWave: 波浪文字（逐字上下浮动）
 * - TextGlitch: 故障风文字（RGB分离/抖动）
 * - TextGradient: 渐变文字（颜色流动/扫光）
 * - KineticText: 动态排版（多文字组合动画）
 */

import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { Easing } from "remotion";

// ============= 工具函数 =============

function easeOutBack(t: number): number {
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
}

function easeOutElastic(t: number): number {
  const c4 = (2 * Math.PI) / 3;
  return t === 0 ? 0 : t === 1 ? 1 : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1;
}

// ============= TextReveal: 逐字显现 =============

export interface TextRevealProps {
  text: string;
  fontSize?: number;
  color?: string;
  fontFamily?: string;
  fontWeight?: string | number;
  startFrame?: number;
  duration?: number;
  revealType?: "typewriter" | "fade" | "slideUp" | "slideLeft";
  charDelay?: number;
  textAlign?: "left" | "center" | "right";
  style?: React.CSSProperties;
}

export const TextReveal: React.FC<TextRevealProps> = ({
  text,
  fontSize = 48,
  color = "#ffffff",
  fontFamily = "sans-serif",
  fontWeight = "bold",
  startFrame = 0,
  duration = 30,
  revealType = "fade",
  charDelay = 3,
  textAlign = "center",
  style = {},
}) => {
  const frame = useCurrentFrame();
  const chars = text.split("");

  return (
    <div
      style={{
        display: "flex",
        justifyContent: textAlign === "center" ? "center" : textAlign === "right" ? "flex-end" : "flex-start",
        alignItems: "center",
        width: "100%",
        ...style,
      }}
    >
      {chars.map((char, i) => {
        const charStart = startFrame + i * charDelay;
        const charFrame = frame - charStart;
        const progress = Math.min(Math.max(charFrame / duration, 0), 1);

        let opacity = 1;
        let transform = "none";
        let filter = "none";

        switch (revealType) {
          case "typewriter":
            opacity = progress > 0 ? 1 : 0;
            break;
          case "fade":
            opacity = progress;
            break;
          case "slideUp":
            opacity = progress;
            transform = `translateY(${interpolate(progress, [0, 1], [30, 0])}px)`;
            break;
          case "slideLeft":
            opacity = progress;
            transform = `translateX(${interpolate(progress, [0, 1], [-30, 0])}px)`;
            break;
        }

        return (
          <span
            key={i}
            style={{
              fontSize,
              color,
              fontFamily,
              fontWeight,
              opacity,
              transform,
              filter,
              display: "inline-block",
              whiteSpace: "pre",
            }}
          >
            {char}
          </span>
        );
      })}
    </div>
  );
};

// ============= TextPop: 弹出文字 =============

export interface TextPopProps {
  text: string;
  fontSize?: number;
  color?: string;
  fontFamily?: string;
  startFrame?: number;
  duration?: number;
  popType?: "scale" | "rotate" | "bounce";
  style?: React.CSSProperties;
}

export const TextPop: React.FC<TextPopProps> = ({
  text,
  fontSize = 64,
  color = "#ffffff",
  fontFamily = "sans-serif",
  startFrame = 0,
  duration = 20,
  popType = "scale",
  style = {},
}) => {
  const frame = useCurrentFrame();
  const progress = Math.min(Math.max((frame - startFrame) / duration, 0), 1);

  let transform = "none";
  let opacity = 1;

  switch (popType) {
    case "scale":
      transform = `scale(${interpolate(progress, [0, 0.6, 1], [0, 1.3, 1], {
        extrapolateRight: "clamp",
      })})`;
      opacity = progress > 0 ? 1 : 0;
      break;
    case "rotate":
      transform = `rotate(${interpolate(progress, [0, 1], [-180, 0])}deg) scale(${easeOutBack(progress)})`;
      opacity = progress > 0 ? 1 : 0;
      break;
    case "bounce":
      transform = `translateY(${interpolate(progress, [0, 0.3, 0.5, 0.7, 1], [0, -40, 0, -20, 0], {
        extrapolateRight: "clamp",
      })}px) scale(${easeOutElastic(progress)})`;
      opacity = progress > 0 ? 1 : 0;
      break;
  }

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        width: "100%",
        ...style,
      }}
    >
      <span
        style={{
          fontSize,
          color,
          fontFamily,
          fontWeight: "bold",
          transform,
          opacity,
          display: "inline-block",
          textShadow: "0 4px 20px rgba(0,0,0,0.5)",
        }}
      >
        {text}
      </span>
    </div>
  );
};

// ============= TextWave: 波浪文字 =============

export interface TextWaveProps {
  text: string;
  fontSize?: number;
  color?: string;
  fontFamily?: string;
  amplitude?: number;
  frequency?: number;
  speed?: number;
  style?: React.CSSProperties;
}

export const TextWave: React.FC<TextWaveProps> = ({
  text,
  fontSize = 48,
  color = "#ffffff",
  fontFamily = "sans-serif",
  amplitude = 15,
  frequency = 0.3,
  speed = 1,
  style = {},
}) => {
  const frame = useCurrentFrame();
  const chars = text.split("");

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        width: "100%",
        ...style,
      }}
    >
      {chars.map((char, i) => {
        const y = Math.sin((frame * speed + i * frequency * 10) * 0.1) * amplitude;
        return (
          <span
            key={i}
            style={{
              fontSize,
              color,
              fontFamily,
              fontWeight: "bold",
              transform: `translateY(${y}px)`,
              display: "inline-block",
              whiteSpace: "pre",
            }}
          >
            {char}
          </span>
        );
      })}
    </div>
  );
};

// ============= TextGlitch: 故障风文字 =============

export interface TextGlitchProps {
  text: string;
  fontSize?: number;
  color?: string;
  fontFamily?: string;
  intensity?: number;
  style?: React.CSSProperties;
}

export const TextGlitch: React.FC<TextGlitchProps> = ({
  text,
  fontSize = 64,
  color = "#ffffff",
  fontFamily = "sans-serif",
  intensity = 5,
  style = {},
}) => {
  const frame = useCurrentFrame();
  const glitchActive = Math.sin(frame * 0.3) > 0.7;
  const offsetX = glitchActive ? (Math.random() - 0.5) * intensity * 2 : 0;
  const offsetY = glitchActive ? (Math.random() - 0.5) * intensity : 0;

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        width: "100%",
        position: "relative",
        ...style,
      }}
    >
      {/* RGB分离层 */}
      <span
        style={{
          fontSize,
          color: "#ff0000",
          fontFamily,
          fontWeight: "bold",
          position: "absolute",
          transform: `translate(${-offsetX}px, ${offsetY}px)`,
          opacity: glitchActive ? 0.7 : 0,
          mixBlendMode: "screen",
        }}
      >
        {text}
      </span>
      <span
        style={{
          fontSize,
          color: "#00ffff",
          fontFamily,
          fontWeight: "bold",
          position: "absolute",
          transform: `translate(${offsetX}px, ${-offsetY}px)`,
          opacity: glitchActive ? 0.7 : 0,
          mixBlendMode: "screen",
        }}
      >
        {text}
      </span>
      {/* 主文字 */}
      <span
        style={{
          fontSize,
          color,
          fontFamily,
          fontWeight: "bold",
          transform: `translate(${offsetX * 0.5}px, ${offsetY * 0.5}px)`,
        }}
      >
        {text}
      </span>
    </div>
  );
};

// ============= TextGradient: 渐变/扫光文字 =============

export interface TextGradientProps {
  text: string;
  fontSize?: number;
  colors?: string[];
  fontFamily?: string;
  speed?: number;
  style?: React.CSSProperties;
}

export const TextGradient: React.FC<TextGradientProps> = ({
  text,
  fontSize = 56,
  colors = ["#ff6b6b", "#feca57", "#48dbfb", "#ff6b6b"],
  fontFamily = "sans-serif",
  speed = 1,
  style = {},
}) => {
  const frame = useCurrentFrame();
  const gradientPos = (frame * speed * 2) % 200;

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        width: "100%",
        ...style,
      }}
    >
      <span
        style={{
          fontSize,
          fontFamily,
          fontWeight: "bold",
          background: `linear-gradient(${gradientPos}deg, ${colors.join(", ")})`,
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          backgroundClip: "text",
          backgroundSize: "200% 200%",
        }}
      >
        {text}
      </span>
    </div>
  );
};

// ============= KineticText: 动态排版 =============

export interface KineticTextLine {
  text: string;
  fontSize?: number;
  color?: string;
  delay?: number;
  animation?: "pop" | "slide" | "fade" | "wave";
}

export interface KineticTextProps {
  lines: KineticTextLine[];
  fontFamily?: string;
  lineHeight?: number;
  style?: React.CSSProperties;
}

export const KineticText: React.FC<KineticTextProps> = ({
  lines,
  fontFamily = "sans-serif",
  lineHeight = 1.4,
  style = {},
}) => {
  const frame = useCurrentFrame();

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        width: "100%",
        gap: 10,
        ...style,
      }}
    >
      {lines.map((line, i) => {
        const delay = line.delay || i * 10;
        const progress = Math.min(Math.max((frame - delay) / 20, 0), 1);
        const anim = line.animation || "pop";

        let transform = "none";
        let opacity = 1;

        switch (anim) {
          case "pop":
            transform = `scale(${easeOutBack(progress)})`;
            opacity = progress > 0 ? 1 : 0;
            break;
          case "slide":
            transform = `translateX(${interpolate(progress, [0, 1], [-100, 0])}px)`;
            opacity = progress;
            break;
          case "fade":
            opacity = progress;
            break;
          case "wave":
            transform = `translateY(${Math.sin((frame + i * 5) * 0.1) * 10 * progress}px)`;
            opacity = progress;
            break;
        }

        return (
          <span
            key={i}
            style={{
              fontSize: line.fontSize || 48,
              color: line.color || "#ffffff",
              fontFamily,
              fontWeight: "bold",
              transform,
              opacity,
              lineHeight,
              textShadow: "0 2px 10px rgba(0,0,0,0.5)",
            }}
          >
            {line.text}
          </span>
        );
      })}
    </div>
  );
};
