/**
 * 特效组件库 v1.0
 * 闪白、震动、爆炸、闪光等常用特效
 * 所有特效均支持透明背景
 */

import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

// ============= 闪白特效 =============
export interface FlashEffectProps {
  /** 起始帧 */
  startFrame?: number;
  /** 持续帧数 */
  duration?: number;
  /** 最大不透明度 (0-1) */
  maxOpacity?: number;
  /** 颜色 */
  color?: string;
}

export const FlashEffect: React.FC<FlashEffectProps> = ({
  startFrame = 0,
  duration = 10,
  maxOpacity = 1,
  color = "white",
}) => {
  const frame = useCurrentFrame();

  if (frame < startFrame || frame > startFrame + duration) {
    return null;
  }

  const progress = (frame - startFrame) / duration;
  // 快速淡入，缓慢淡出
  const opacity = progress < 0.3
    ? interpolate(progress, [0, 0.3], [0, maxOpacity])
    : interpolate(progress, [0.3, 1], [maxOpacity, 0]);

  return (
    <AbsoluteFill style={{ backgroundColor: color, opacity }} />
  );
};

// ============= 震动特效 =============
export interface ShakeEffectProps {
  /** 起始帧 */
  startFrame?: number;
  /** 持续帧数 */
  duration?: number;
  /** 震动幅度（像素） */
  amplitude?: number;
  /** 震动频率 */
  frequency?: number;
  /** 子元素 */
  children: React.ReactNode;
}

export const ShakeEffect: React.FC<ShakeEffectProps> = ({
  startFrame = 0,
  duration = 15,
  amplitude = 10,
  frequency = 2,
  children,
}) => {
  const frame = useCurrentFrame();

  if (frame < startFrame || frame > startFrame + duration) {
    return <>{children}</>;
  }

  const progress = (frame - startFrame) / duration;
  // 振幅随时间衰减
  const decay = 1 - progress;
  const offsetX = Math.sin(frame * frequency) * amplitude * decay;
  const offsetY = Math.cos(frame * frequency * 1.3) * amplitude * decay * 0.7;
  const rotation = Math.sin(frame * frequency * 0.7) * 2 * decay;

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        transform: `translate(${offsetX}px, ${offsetY}px) rotate(${rotation}deg)`,
      }}
    >
      {children}
    </div>
  );
};

// ============= 淡入淡出组件 =============
export interface FadeEffectProps {
  /** 起始帧 */
  startFrame?: number;
  /** 淡入时长 */
  fadeInDuration?: number;
  /** 淡出时长 */
  fadeOutDuration?: number;
  /** 总时长 */
  duration?: number;
  /** 子元素 */
  children: React.ReactNode;
}

export const FadeEffect: React.FC<FadeEffectProps> = ({
  startFrame = 0,
  fadeInDuration = 10,
  fadeOutDuration = 10,
  duration = 60,
  children,
}) => {
  const frame = useCurrentFrame();

  if (frame < startFrame || frame > startFrame + duration) {
    return null;
  }

  const elapsed = frame - startFrame;
  let opacity = 1;

  if (elapsed < fadeInDuration) {
    opacity = interpolate(elapsed, [0, fadeInDuration], [0, 1]);
  } else if (elapsed > duration - fadeOutDuration) {
    opacity = interpolate(elapsed, [duration - fadeOutDuration, duration], [1, 0]);
  }

  return (
    <div style={{ width: "100%", height: "100%", opacity }}>
      {children}
    </div>
  );
};

// ============= 缩放弹出组件 =============
export interface PopEffectProps {
  /** 起始帧 */
  startFrame?: number;
  /** 动画时长 */
  duration?: number;
  /** 最大缩放 */
  maxScale?: number;
  /** 子元素 */
  children: React.ReactNode;
}

export const PopEffect: React.FC<PopEffectProps> = ({
  startFrame = 0,
  duration = 20,
  maxScale = 1.2,
  children,
}) => {
  const frame = useCurrentFrame();

  if (frame < startFrame) {
    return null;
  }

  const elapsed = frame - startFrame;
  if (elapsed > duration) {
    return <>{children}</>;
  }

  // 弹性弹出：先放大到maxScale，再回弹到1
  const progress = elapsed / duration;
  let scale: number;
  if (progress < 0.5) {
    scale = interpolate(progress, [0, 0.5], [0, maxScale]);
  } else {
    scale = interpolate(progress, [0.5, 1], [maxScale, 1], {
      extrapolateRight: "clamp",
    });
  }

  const opacity = interpolate(progress, [0, 0.2], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        transform: `scale(${scale})`,
        opacity,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      {children}
    </div>
  );
};

// ============= 滑动组件 =============
export interface SlideEffectProps {
  /** 起始帧 */
  startFrame?: number;
  /** 动画时长 */
  duration?: number;
  /** 滑动方向 */
  direction?: "left" | "right" | "top" | "bottom";
  /** 滑动距离（像素） */
  distance?: number;
  /** 子元素 */
  children: React.ReactNode;
}

export const SlideEffect: React.FC<SlideEffectProps> = ({
  startFrame = 0,
  duration = 20,
  direction = "left",
  distance = 500,
  children,
}) => {
  const frame = useCurrentFrame();

  if (frame < startFrame) {
    return null;
  }

  const elapsed = frame - startFrame;
  const progress = Math.min(1, elapsed / duration);
  // 缓出
  const eased = 1 - Math.pow(1 - progress, 3);

  let offsetX = 0, offsetY = 0;
  switch (direction) {
    case "left":
      offsetX = distance * (1 - eased);
      break;
    case "right":
      offsetX = -distance * (1 - eased);
      break;
    case "top":
      offsetY = distance * (1 - eased);
      break;
    case "bottom":
      offsetY = -distance * (1 - eased);
      break;
  }

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        transform: `translate(${offsetX}px, ${offsetY}px)`,
      }}
    >
      {children}
    </div>
  );
};

export default {
  FlashEffect,
  ShakeEffect,
  FadeEffect,
  PopEffect,
  SlideEffect,
};
