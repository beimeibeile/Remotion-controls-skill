/**
 * 运动路径组件 v1.0
 * 支持贝塞尔曲线运动、直线运动、弹性运动
 * 用于透明背景动画中的角色/道具移动
 */

import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";

export interface PathPoint {
  x: number;
  y: number;
}

export interface MotionPathProps {
  /** 起始点 */
  from: PathPoint;
  /** 结束点 */
  to: PathPoint;
  /** 控制点1（贝塞尔曲线） */
  control1?: PathPoint;
  /** 控制点2（贝塞尔曲线） */
  control2?: PathPoint;
  /** 起始帧 */
  startFrame?: number;
  /** 结束帧 */
  endFrame?: number;
  /** 运动类型 */
  motionType?: "linear" | "bezier" | "bounce" | "elastic";
  /** 子元素 */
  children: React.ReactNode;
  /** 宽度 */
  width?: number;
  /** 高度 */
  height?: number;
}

/**
 * 线性插值
 */
function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

/**
 * 三次贝塞尔曲线插值
 */
function cubicBezier(
  p0: number, p1: number, p2: number, p3: number, t: number
): number {
  const u = 1 - t;
  return u * u * u * p0 + 3 * u * u * t * p1 + 3 * u * t * t * p2 + t * t * t * p3;
}

/**
 * 弹性缓动函数
 */
function elasticOut(t: number): number {
  if (t === 0 || t === 1) return t;
  const p = 0.3;
  return Math.pow(2, -10 * t) * Math.sin((t - p / 4) * (2 * Math.PI) / p) + 1;
}

/**
 * 弹跳缓动函数
 */
function bounceOut(t: number): number {
  const n1 = 7.5625;
  const d1 = 2.75;
  if (t < 1 / d1) {
    return n1 * t * t;
  } else if (t < 2 / d1) {
    return n1 * (t -= 1.5 / d1) * t + 0.75;
  } else if (t < 2.5 / d1) {
    return n1 * (t -= 2.25 / d1) * t + 0.9375;
  } else {
    return n1 * (t -= 2.625 / d1) * t + 0.984375;
  }
}

/**
 * 运动路径组件
 * 根据当前帧计算位置，并渲染子元素
 */
export const MotionPath: React.FC<MotionPathProps> = ({
  from,
  to,
  control1,
  control2,
  startFrame = 0,
  endFrame = 30,
  motionType = "linear",
  children,
  width = 100,
  height = 100,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // 计算进度
  const duration = endFrame - startFrame;
  const rawProgress = Math.max(0, Math.min(1, (frame - startFrame) / duration));

  // 应用缓动函数
  let progress = rawProgress;
  switch (motionType) {
    case "elastic":
      progress = elasticOut(rawProgress);
      break;
    case "bounce":
      progress = bounceOut(rawProgress);
      break;
    case "bezier":
      // 贝塞尔曲线用位置插值，进度仍用线性
      progress = rawProgress;
      break;
    default:
      progress = rawProgress;
  }

  // 计算位置
  let x: number, y: number;
  if (motionType === "bezier" && control1 && control2) {
    x = cubicBezier(from.x, control1.x, control2.x, to.x, progress);
    y = cubicBezier(from.y, control1.y, control2.y, to.y, progress);
  } else {
    x = lerp(from.x, to.x, progress);
    y = lerp(from.y, to.y, progress);
  }

  // 超出范围不渲染
  if (frame < startFrame || frame > endFrame) {
    return null;
  }

  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        width,
        height,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      {children}
    </div>
  );
};

export default MotionPath;
