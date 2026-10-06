/**
 * 角色精灵组件 v1.0
 * 支持多姿态切换、位置动画、缩放动画、旋转动画
 * 用于透明背景动画中的角色层
 */

import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";

export interface PoseConfig {
  /** 姿态名称 */
  name: string;
  /** 姿态图片路径（相对于public目录） */
  image: string;
  /** 姿态持续时间范围 [起始帧, 结束帧] */
  frameRange: [number, number];
  /** 位置关键帧 [{frame, x, y}] */
  position?: Array<{ frame: number; x: number; y: number }>;
  /** 缩放关键帧 [{frame, scale}] */
  scale?: Array<{ frame: number; scale: number }>;
  /** 旋转关键帧 [{frame, rotation}] */
  rotation?: Array<{ frame: number; rotation: number }>;
  /** 透明度关键帧 [{frame, opacity}] */
  opacity?: Array<{ frame: number; opacity: number }>;
  /** 缓动函数 */
  easing?: (t: number) => number;
}

export interface CharacterSpriteProps {
  /** 姿态配置列表 */
  poses: PoseConfig[];
  /** 默认宽度（像素） */
  width?: number;
  /** 默认高度（像素） */
  height?: number;
  /** 是否显示调试边框 */
  debug?: boolean;
}

/**
 * 线性插值关键帧值
 */
function interpolateKeyframes(
  frame: number,
  keyframes: Array<{ frame: number; value: number }>,
  defaultValue: number,
  easing?: (t: number) => number
): number {
  if (!keyframes || keyframes.length === 0) return defaultValue;
  if (keyframes.length === 1) return keyframes[0].value;

  // 排序
  const sorted = [...keyframes].sort((a, b) => a.frame - b.frame);

  // 找到当前帧所在的区间
  for (let i = 0; i < sorted.length - 1; i++) {
    const curr = sorted[i];
    const next = sorted[i + 1];
    if (frame >= curr.frame && frame <= next.frame) {
      const progress = (frame - curr.frame) / (next.frame - curr.frame);
      const easedProgress = easing ? easing(progress) : progress;
      return curr.value + (next.value - curr.value) * easedProgress;
    }
  }

  // 超出范围
  if (frame < sorted[0].frame) return sorted[0].value;
  return sorted[sorted.length - 1].value;
}

/**
 * 角色精灵组件
 * 根据当前帧自动切换姿态，并应用位置/缩放/旋转/透明度动画
 */
export const CharacterSprite: React.FC<CharacterSpriteProps> = ({
  poses,
  width = 250,
  height = 250,
  debug = false,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // 找到当前帧对应的姿态
  const currentPose = poses.find(
    (p) => frame >= p.frameRange[0] && frame <= p.frameRange[1]
  );

  if (!currentPose) {
    return null;
  }

  // 计算位置
  const x = interpolateKeyframes(
    frame,
    (currentPose.position || []).map((k) => ({ frame: k.frame, value: k.x })),
    0,
    currentPose.easing
  );
  const y = interpolateKeyframes(
    frame,
    (currentPose.position || []).map((k) => ({ frame: k.frame, value: k.y })),
    0,
    currentPose.easing
  );

  // 计算缩放
  const scale = interpolateKeyframes(
    frame,
    (currentPose.scale || []).map((k) => ({ frame: k.frame, value: k.scale })),
    1,
    currentPose.easing
  );

  // 计算旋转
  const rotation = interpolateKeyframes(
    frame,
    (currentPose.rotation || []).map((k) => ({ frame: k.frame, value: k.rotation })),
    0,
    currentPose.easing
  );

  // 计算透明度
  const opacity = interpolateKeyframes(
    frame,
    (currentPose.opacity || []).map((k) => ({ frame: k.frame, value: k.opacity })),
    1,
    currentPose.easing
  );

  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
      <div
        style={{
          position: "absolute",
          left: x,
          top: y,
          width: width * scale,
          height: height * scale,
          transform: `rotate(${rotation}deg)`,
          opacity,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          border: debug ? "2px solid red" : "none",
        }}
      >
        <img
          src={currentPose.image}
          alt={currentPose.name}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "contain",
          }}
        />
      </div>
    </AbsoluteFill>
  );
};

export default CharacterSprite;
