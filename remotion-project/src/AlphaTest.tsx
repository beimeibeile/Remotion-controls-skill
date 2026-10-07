// 最简Alpha通道测试动画
// 纯色方块从左到右移动，透明背景
// 用于验证剪映对ProRes 4444透明背景视频的支持
import React from 'react';
import { AbsoluteFill, useCurrentFrame, interpolate } from 'remotion';

export const AlphaTest: React.FC = () => {
  const frame = useCurrentFrame();

  // 方块从左到右移动（0帧在左，90帧在右）
  const x = interpolate(frame, [0, 90], [100, 780], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // 方块上下浮动
  const y = 800 + Math.sin(frame * 0.1) * 50;

  // 透明度渐变（前30帧淡入，最后30帧淡出）
  const opacity = interpolate(frame, [0, 30, 60, 90], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ backgroundColor: 'transparent' }}>
      {/* 红色方块 */}
      <div
        style={{
          position: 'absolute',
          left: x,
          top: y,
          width: 200,
          height: 200,
          backgroundColor: '#FF4444',
          borderRadius: 20,
          opacity: opacity,
          boxShadow: '0 0 30px rgba(255, 68, 68, 0.8)',
        }}
      />
      {/* 蓝色方块（反向移动） */}
      <div
        style={{
          position: 'absolute',
          left: interpolate(frame, [0, 90], [780, 100], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          }),
          top: y + 250,
          width: 150,
          height: 150,
          backgroundColor: '#4488FF',
          borderRadius: 75,
          opacity: opacity * 0.8,
        }}
      />
      {/* 中心文字 */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: 500,
          textAlign: 'center',
          fontSize: 48,
          fontWeight: 'bold',
          color: '#FFFFFF',
          opacity: opacity,
          textShadow: '0 2px 10px rgba(0,0,0,0.5)',
        }}
      >
        Alpha Test
      </div>
    </AbsoluteFill>
  );
};
