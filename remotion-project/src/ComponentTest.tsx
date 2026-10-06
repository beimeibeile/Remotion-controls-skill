/**
 * 基础组件库测试动画
 * 验证 CharacterSprite、MotionPath、Effects 等组件
 * 5秒测试动画，透明背景
 */

import React from "react";
import { AbsoluteFill } from "remotion";
import { CharacterSprite } from "./components/CharacterSprite";
import { MotionPath } from "./components/MotionPath";
import { FlashEffect, ShakeEffect, FadeEffect, PopEffect } from "./components/Effects";

export const ComponentTest: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "transparent" }}>
      {/* 角色精灵：从左到右移动，同时切换姿态 */}
      <CharacterSprite
        poses={[
          {
            name: "idle",
            image: "/doubao_head_normal.png",
            frameRange: [0, 45],
            position: [
              { frame: 0, x: 100, y: 800 },
              { frame: 45, x: 400, y: 800 },
            ],
            scale: [{ frame: 0, scale: 1 }, { frame: 45, scale: 1.2 }],
          },
          {
            name: "angry",
            image: "/doubao_head_angry.png",
            frameRange: [45, 90],
            position: [
              { frame: 45, x: 400, y: 800 },
              { frame: 90, x: 700, y: 600 },
            ],
            rotation: [{ frame: 45, rotation: 0 }, { frame: 90, rotation: 15 }],
          },
          {
            name: "injured",
            image: "/doubao_head_injured.png",
            frameRange: [90, 150],
            position: [
              { frame: 90, x: 700, y: 600 },
              { frame: 120, x: 500, y: 1200 },
              { frame: 150, x: 200, y: 800 },
            ],
            scale: [{ frame: 90, scale: 1.2 }, { frame: 150, scale: 0.8 }],
          },
        ]}
        width={200}
        height={200}
      />

      {/* 运动路径：弹弓从右往左飞 */}
      <MotionPath
        from={{ x: 900, y: 300 }}
        to={{ x: 200, y: 900 }}
        control1={{ x: 600, y: 100 }}
        control2={{ x: 400, y: 1100 }}
        startFrame={30}
        endFrame={80}
        motionType="bezier"
        width={80}
        height={80}
      >
        <img src="/slingshot.png" style={{ width: "100%", height: "100%" }} />
      </MotionPath>

      {/* 闪白特效：在60帧时闪白 */}
      <FlashEffect startFrame={60} duration={10} maxOpacity={0.8} />

      {/* 震动特效：60-75帧震动 */}
      <ShakeEffect startFrame={60} duration={15} amplitude={15} frequency={3}>
        <AbsoluteFill />
      </ShakeEffect>

      {/* 弹出特效：100帧时弹出受伤标记 */}
      <PopEffect startFrame={100} duration={20} maxScale={1.5}>
        <div
          style={{
            position: "absolute",
            left: 500,
            top: 400,
            width: 100,
            height: 100,
            backgroundColor: "red",
            borderRadius: "50%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "white",
            fontSize: 40,
            fontWeight: "bold",
          }}
        >
          !
        </div>
      </PopEffect>

      {/* 淡入淡出：底部文字 */}
      <FadeEffect startFrame={120} fadeInDuration={15} fadeOutDuration={15} duration={30}>
        <div
          style={{
            position: "absolute",
            bottom: 200,
            width: "100%",
            textAlign: "center",
            fontSize: 48,
            color: "white",
            textShadow: "2px 2px 4px rgba(0,0,0,0.8)",
          }}
        >
          组件库测试通过
        </div>
      </FadeEffect>
    </AbsoluteFill>
  );
};

export default ComponentTest;
