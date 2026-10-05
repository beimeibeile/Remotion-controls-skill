// Remotion Root 组件 - 注册 Composition
import React from 'react';
import { Composition } from 'remotion';
import { AnimationTemplate } from './AnimationTemplate';
import type { AnimationConfig } from './types';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="AnimationTemplate"
        component={AnimationTemplate}
        durationInFrames={600}  // 默认20秒 @ 30fps
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{
          config: {
            composition: 'AnimationTemplate',
            fps: 30,
            width: 1080,
            height: 1920,
            duration: 20,
            layers: [],
          } as AnimationConfig,
        }}
      />
    </>
  );
};
