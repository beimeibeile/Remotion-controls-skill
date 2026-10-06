/**
 * 转场+冲击特效综合测试
 * 验证 TransitionEffects + ImpactEffects 全部组件
 * 8秒测试动画，透明背景
 */

import React from "react";
import { AbsoluteFill } from "remotion";
import {
  FadeTransition,
  SlideTransition,
  ZoomTransition,
  WipeTransition,
  PunchImpact,
  ImpactFlash,
  ParticleBurst,
  Shockwave,
  SpeedLines,
  TextPop,
} from "./components";

export const EffectTest: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "transparent" }}>
      {/* 0-1秒: 淡入 */}
      <FadeTransition direction="in" duration={15} startFrame={0} color="#1a1a2e" />

      {/* 1秒: 标题弹出 */}
      <div style={{ position: "absolute", top: 300, width: "100%" }}>
        <TextPop text="特效测试" fontSize={72} color="#ff6b6b" startFrame={10} duration={20} popType="bounce" />
      </div>

      {/* 1.5-2秒: 拳击冲击 */}
      <PunchImpact startFrame={45} x={540} y={800} scale={1.2} />
      <ImpactFlash startFrame={45} duration={8} />

      {/* 2-2.5秒: 粒子爆发 */}
      <ParticleBurst startFrame={60} x={540} y={800} count={16} particleType="star" color="#ffcc00" maxDistance={250} />

      {/* 2.5-3.5秒: 冲击波 */}
      <Shockwave startFrame={75} x={540} y={800} maxRadius={400} color="#00ffff" ringCount={3} />

      {/* 3-3.5秒: 速度线 */}
      <SpeedLines startFrame={90} duration={12} x={540} y={800} count={12} color="#ffffff" />

      {/* 3.5-4.5秒: 滑动转场 */}
      <SlideTransition direction="left" duration={20} startFrame={105} color="#16213e" />

      {/* 4.5-5秒: 缩放转场 */}
      <ZoomTransition direction="in" duration={15} startFrame={135} color="#0f3460" />

      {/* 5-5.5秒: 擦除转场 */}
      <WipeTransition direction="diagonal" duration={15} startFrame={150} color="#e94560" />

      {/* 5.5-6秒: 第二次冲击 */}
      <PunchImpact startFrame={165} x={300} y={600} scale={0.8} />
      <ParticleBurst startFrame={165} x={300} y={600} count={8} particleType="spark" color="#00ffff" maxDistance={150} />

      {/* 6-6.5秒: 第三次冲击 */}
      <PunchImpact startFrame={180} x={780} y={1100} scale={0.8} />
      <ParticleBurst startFrame={180} x={780} y={1100} count={8} particleType="debris" color="#ff6b6b" maxDistance={150} />

      {/* 6.5-7.5秒: 淡出 */}
      <FadeTransition direction="out" duration={20} startFrame={195} color="#000000" />
    </AbsoluteFill>
  );
};

export default EffectTest;
