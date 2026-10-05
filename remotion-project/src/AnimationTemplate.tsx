// 动画模板组件 - 从JSON配置渲染多图层关键帧动画（透明背景）
import React from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig, Img } from 'remotion';
import type { AnimationConfig, Layer } from './types';
import { interpolate } from './easing';

interface AnimationTemplateProps {
  config?: AnimationConfig;
}

// 单个动画图层
const AnimationLayer: React.FC<{
  layer: Layer;
  currentTime: number;
  canvasWidth: number;
  canvasHeight: number;
}> = ({ layer, currentTime, canvasWidth, canvasHeight }) => {
  const { keyframes, image } = layer;

  // 计算当前帧的属性
  const x = interpolate(currentTime, keyframes, 'x');
  const y = interpolate(currentTime, keyframes, 'y');
  const scale = interpolate(currentTime, keyframes, 'scale', 'ease-out') || 1;
  const opacity = interpolate(currentTime, keyframes, 'opacity', 'ease-out');
  const rotation = interpolate(currentTime, keyframes, 'rotation', 'ease-out');

  // 检查该图层在当前时间是否可见（有任何关键帧属性）
  const hasRelevantKf = keyframes.some(
    kf => kf.x !== undefined || kf.y !== undefined ||
          kf.scale !== undefined || kf.opacity !== undefined ||
          kf.rotation !== undefined
  );

  if (!hasRelevantKf) return null;

  // 如果透明度为0，不渲染
  if (opacity <= 0.001) return null;

  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        top: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
      }}
    >
      <div
        style={{
          position: 'absolute',
          left: `${x}px`,
          top: `${y}px`,
          transform: `translate(-50%, -50%) scale(${scale}) rotate(${rotation}deg)`,
          opacity: opacity,
          transformOrigin: 'center center',
        }}
      >
        <Img
          src={image}
          style={{
            display: 'block',
            maxWidth: 'none',
          }}
        />
      </div>
    </div>
  );
};

export const AnimationTemplate: React.FC<AnimationTemplateProps> = ({ config }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const currentTime = frame / fps;
  const layers = config?.layers || [];
  const canvasWidth = config?.width || 1080;
  const canvasHeight = config?.height || 1920;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: 'transparent',
      }}
    >
      {layers.map((layer, index) => (
        <AnimationLayer
          key={layer.id || `layer-${index}`}
          layer={layer}
          currentTime={currentTime}
          canvasWidth={canvasWidth}
          canvasHeight={canvasHeight}
        />
      ))}
    </AbsoluteFill>
  );
};
