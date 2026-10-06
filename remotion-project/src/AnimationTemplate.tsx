// 动画模板组件 - 从JSON配置渲染多图层关键帧动画（透明背景）
import React from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig, Img } from 'remotion';
import type { AnimationConfig, Layer } from './types';
import { interpolate } from './easing';
import { animationConfig } from './animation-config';

// 直接import所有图片，确保Remotion打包时包含
import doubao_head_normal from '../public/doubao_head_normal.png';
import doubao_head_angry from '../public/doubao_head_angry.png';
import doubao_head_injured from '../public/doubao_head_injured.png';
import doubao_flying from '../public/doubao_flying.png';
import doubao_climbing from '../public/doubao_climbing.png';
import doubao_injured from '../public/doubao_injured.png';
// 从原视频提取的正确豆包姿态
import doubao_normal from '../public/doubao_normal.png';
import doubao_peek from '../public/doubao_peek.png';
import doubao_falling from '../public/doubao_falling.png';
import doubao_slingshot from '../public/doubao_slingshot.png';
import slingshot from '../public/slingshot.png';
import flying_rock from '../public/flying_rock.png';
import portal from '../public/portal.png';
import admin from '../public/admin.png';
import hook from '../public/hook.png';
import flash_white from '../public/flash_white.png';
import ban_stamp from '../public/ban_stamp.png';

// 图片名称到import的映射
const imageMap: Record<string, string> = {
  'doubao_head_normal.png': doubao_head_normal,
  'doubao_head_angry.png': doubao_head_angry,
  'doubao_head_injured.png': doubao_head_injured,
  'doubao_flying.png': doubao_flying,
  'doubao_climbing.png': doubao_climbing,
  'doubao_injured.png': doubao_injured,
  'doubao_normal.png': doubao_normal,
  'doubao_peek.png': doubao_peek,
  'doubao_falling.png': doubao_falling,
  'doubao_slingshot.png': doubao_slingshot,
  'slingshot.png': slingshot,
  'flying_rock.png': flying_rock,
  'portal.png': portal,
  'admin.png': admin,
  'hook.png': hook,
  'flash_white.png': flash_white,
  'ban_stamp.png': ban_stamp,
};

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

  // 获取图片src
  const imgSrc = imageMap[image] || image;

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
          src={imgSrc}
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
  // 优先使用props传入的config，否则使用animation-config.ts文件中的配置
  const activeConfig = config || (animationConfig as unknown as AnimationConfig);
  const layers = activeConfig?.layers || [];
  const canvasWidth = activeConfig?.width || 1080;
  const canvasHeight = activeConfig?.height || 1920;

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
