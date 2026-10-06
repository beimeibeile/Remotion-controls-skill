/**
 * 转场特效组件库 v1.0
 * 视频剪辑常用转场，支持透明背景输出
 *
 * 组件清单：
 * - FadeTransition: 淡入淡出转场
 * - SlideTransition: 滑动转场（上下左右）
 * - ZoomTransition: 缩放转场（推近/拉远）
 * - WipeTransition: 擦除转场（上下左右/对角线）
 * - BlurTransition: 模糊转场
 * - GlitchTransition: 故障风转场
 */

import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

// 手动缓动函数（避免Remotion Easing高阶函数API问题）
const easeInOut = (t: number) => (t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2);

// ============= FadeTransition: 淡入淡出 =============

export interface FadeTransitionProps {
  direction?: "in" | "out" | "inOut";
  duration?: number;
  startFrame?: number;
  color?: string;
  style?: React.CSSProperties;
}

export const FadeTransition: React.FC<FadeTransitionProps> = ({
  direction = "inOut",
  duration = 15,
  startFrame = 0,
  color = "#000000",
  style = {},
}) => {
  const frame = useCurrentFrame();
  const t = frame - startFrame;

  let opacity = 0;
  if (direction === "in") {
    opacity = interpolate(t, [0, duration], [1, 0], { extrapolateRight: "clamp" });
  } else if (direction === "out") {
    opacity = interpolate(t, [0, duration], [0, 1], { extrapolateRight: "clamp" });
  } else {
    // inOut: 先淡入再淡出
    const half = duration / 2;
    if (t < half) {
      opacity = interpolate(t, [0, half], [0, 1], { extrapolateRight: "clamp" });
    } else {
      opacity = interpolate(t, [half, duration], [1, 0], { extrapolateRight: "clamp" });
    }
  }

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

// ============= SlideTransition: 滑动转场 =============

export interface SlideTransitionProps {
  direction?: "left" | "right" | "up" | "down";
  duration?: number;
  startFrame?: number;
  color?: string;
  style?: React.CSSProperties;
}

export const SlideTransition: React.FC<SlideTransitionProps> = ({
  direction = "left",
  duration = 15,
  startFrame = 0,
  color = "#000000",
  style = {},
}) => {
  const frame = useCurrentFrame();
  const t = Math.min(Math.max((frame - startFrame) / duration, 0), 1);
  const eased = easeInOut(t);

  let transform = "none";
  switch (direction) {
    case "left":
      transform = `translateX(${interpolate(eased, [0, 1], [0, -100])}%)`;
      break;
    case "right":
      transform = `translateX(${interpolate(eased, [0, 1], [0, 100])}%)`;
      break;
    case "up":
      transform = `translateY(${interpolate(eased, [0, 1], [0, -100])}%)`;
      break;
    case "down":
      transform = `translateY(${interpolate(eased, [0, 1], [0, 100])}%)`;
      break;
  }

  return (
    <AbsoluteFill
      style={{
        backgroundColor: color,
        transform,
        ...style,
      }}
    />
  );
};

// ============= ZoomTransition: 缩放转场 =============

export interface ZoomTransitionProps {
  direction?: "in" | "out";
  duration?: number;
  startFrame?: number;
  color?: string;
  style?: React.CSSProperties;
}

export const ZoomTransition: React.FC<ZoomTransitionProps> = ({
  direction = "in",
  duration = 15,
  startFrame = 0,
  color = "#000000",
  style = {},
}) => {
  const frame = useCurrentFrame();
  const t = Math.min(Math.max((frame - startFrame) / duration, 0), 1);
  const eased = easeInOut(t);

  const scale = direction === "in"
    ? interpolate(eased, [0, 1], [0, 1.5])
    : interpolate(eased, [0, 1], [1.5, 0]);
  const opacity = direction === "in"
    ? interpolate(eased, [0, 0.8, 1], [0, 1, 1])
    : interpolate(eased, [0, 0.2, 1], [1, 1, 0]);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: color,
        transform: `scale(${scale})`,
        opacity,
        ...style,
      }}
    />
  );
};

// ============= WipeTransition: 擦除转场 =============

export interface WipeTransitionProps {
  direction?: "left" | "right" | "up" | "down" | "diagonal";
  duration?: number;
  startFrame?: number;
  color?: string;
  style?: React.CSSProperties;
}

export const WipeTransition: React.FC<WipeTransitionProps> = ({
  direction = "left",
  duration = 15,
  startFrame = 0,
  color = "#ffffff",
  style = {},
}) => {
  const frame = useCurrentFrame();
  const t = Math.min(Math.max((frame - startFrame) / duration, 0), 1);
  const eased = easeInOut(t);

  let clipPath = "none";
  switch (direction) {
    case "left":
      clipPath = `inset(0 ${interpolate(eased, [0, 1], [0, 100])}% 0 0)`;
      break;
    case "right":
      clipPath = `inset(0 0 0 ${interpolate(eased, [0, 1], [0, 100])}%)`;
      break;
    case "up":
      clipPath = `inset(0 0 ${interpolate(eased, [0, 1], [0, 100])}% 0)`;
      break;
    case "down":
      clipPath = `inset(${interpolate(eased, [0, 1], [0, 100])}% 0 0 0)`;
      break;
    case "diagonal":
      clipPath = `polygon(0 0, ${interpolate(eased, [0, 1], [100, 0])}% 0, 0 ${interpolate(eased, [0, 1], [100, 0])}%)`;
      break;
  }

  return (
    <AbsoluteFill
      style={{
        backgroundColor: color,
        clipPath,
        ...style,
      }}
    />
  );
};

// ============= BlurTransition: 模糊转场 =============

export interface BlurTransitionProps {
  duration?: number;
  startFrame?: number;
  maxBlur?: number;
  color?: string;
  style?: React.CSSProperties;
}

export const BlurTransition: React.FC<BlurTransitionProps> = ({
  duration = 20,
  startFrame = 0,
  maxBlur = 30,
  color = "#000000",
  style = {},
}) => {
  const frame = useCurrentFrame();
  const t = Math.min(Math.max((frame - startFrame) / duration, 0), 1);

  // 先模糊到最大，再恢复
  const blur = t < 0.5
    ? interpolate(t, [0, 0.5], [0, maxBlur])
    : interpolate(t, [0.5, 1], [maxBlur, 0]);
  const opacity = t < 0.5
    ? interpolate(t, [0, 0.5], [0, 0.8])
    : interpolate(t, [0.5, 1], [0.8, 0]);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: color,
        opacity,
        filter: `blur(${blur}px)`,
        ...style,
      }}
    />
  );
};

// ============= GlitchTransition: 故障风转场 =============

export interface GlitchTransitionProps {
  duration?: number;
  startFrame?: number;
  intensity?: number;
  style?: React.CSSProperties;
}

export const GlitchTransition: React.FC<GlitchTransitionProps> = ({
  duration = 15,
  startFrame = 0,
  intensity = 10,
  style = {},
}) => {
  const frame = useCurrentFrame();
  const t = Math.min(Math.max((frame - startFrame) / duration, 0), 1);

  const active = Math.sin(frame * 0.5) > 0.3;
  const offsetX = active ? (Math.random() - 0.5) * intensity * 2 : 0;
  const offsetY = active ? (Math.random() - 0.5) * intensity : 0;
  const opacity = interpolate(t, [0, 0.3, 0.7, 1], [0, 0.9, 0.9, 0], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ opacity, ...style }}>
      {/* RGB分离层 */}
      <AbsoluteFill
        style={{
          backgroundColor: "#ff0000",
          transform: `translate(${-offsetX}px, ${offsetY}px)`,
          opacity: 0.5,
          mixBlendMode: "screen",
        }}
      />
      <AbsoluteFill
        style={{
          backgroundColor: "#00ffff",
          transform: `translate(${offsetX}px, ${-offsetY}px)`,
          opacity: 0.5,
          mixBlendMode: "screen",
        }}
      />
      {/* 扫描线 */}
      <div
        style={{
          position: "absolute",
          top: `${(frame * 3) % 100}%`,
          left: 0,
          right: 0,
          height: "3px",
          backgroundColor: "rgba(255,255,255,0.3)",
        }}
      />
    </AbsoluteFill>
  );
};
