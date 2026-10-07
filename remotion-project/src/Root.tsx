// Remotion Root 组件 - 注册 Composition
import React from 'react';
import { Composition } from 'remotion';
import { AlphaTest } from './AlphaTest';
import { AnimationTemplate } from './AnimationTemplate';
import { ComponentTest } from './ComponentTest';
import { TextAnimationTest } from './TextAnimationTest';
import { EffectTest } from './EffectTest';
import { DoubaoHitAnimation } from './DoubaoHitAnimation';
import { animationConfig } from './animation-config';
import type { AnimationConfig } from './types';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="AlphaTest"
        component={AlphaTest}
        durationInFrames={90}  // 3秒 @ 30fps
        fps={30}
        width={1080}
        height={1920}
      />
      <Composition
        id="AnimationTemplate"
        component={AnimationTemplate}
        durationInFrames={600}  // 默认20秒 @ 30fps
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          config: animationConfig as unknown as AnimationConfig,
        }}
      />
      <Composition
        id="ComponentTest"
        component={ComponentTest}
        durationInFrames={150}  // 5秒 @ 30fps
        fps={30}
        width={1080}
        height={1920}
      />
      <Composition
        id="TextAnimationTest"
        component={TextAnimationTest}
        durationInFrames={180}  // 6秒 @ 30fps
        fps={30}
        width={1080}
        height={1920}
      />
      <Composition
        id="EffectTest"
        component={EffectTest}
        durationInFrames={240}  // 8秒 @ 30fps
        fps={30}
        width={1080}
        height={1920}
      />
      <Composition
        id="DoubaoHit"
        component={DoubaoHitAnimation}
        durationInFrames={600}  // 20秒 @ 30fps
        fps={30}
        width={1080}
        height={1920}
      />
    </>
  );
};
