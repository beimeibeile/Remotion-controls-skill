/**
 * 文字动画组件测试
 * 验证 TextReveal/TextPop/TextWave/TextGlitch/TextGradient/KineticText
 * 6秒测试动画，透明背景
 */

import React from "react";
import { AbsoluteFill } from "remotion";
import {
  TextReveal,
  TextPop,
  TextWave,
  TextGlitch,
  TextGradient,
  KineticText,
} from "./components/TextAnimations";

export const TextAnimationTest: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "transparent" }}>
      {/* 0-1秒: 逐字显现 */}
      <div style={{ position: "absolute", top: 200, width: "100%" }}>
        <TextReveal
          text="逐字显现"
          fontSize={56}
          color="#ffffff"
          startFrame={0}
          duration={15}
          revealType="typewriter"
          charDelay={4}
        />
      </div>

      {/* 1-2秒: 弹出文字 */}
      <div style={{ position: "absolute", top: 400, width: "100%" }}>
        <TextPop
          text="弹出!"
          fontSize={72}
          color="#ff6b6b"
          startFrame={30}
          duration={20}
          popType="bounce"
        />
      </div>

      {/* 2-3秒: 波浪文字 */}
      <div style={{ position: "absolute", top: 600, width: "100%" }}>
        <TextWave
          text="波浪起伏"
          fontSize={56}
          color="#48dbfb"
          amplitude={20}
          frequency={0.4}
        />
      </div>

      {/* 3-4秒: 故障风 */}
      <div style={{ position: "absolute", top: 800, width: "100%" }}>
        <TextGlitch
          text="GLITCH"
          fontSize={64}
          color="#ffffff"
          intensity={8}
        />
      </div>

      {/* 4-5秒: 渐变扫光 */}
      <div style={{ position: "absolute", top: 1000, width: "100%" }}>
        <TextGradient
          text="渐变流光"
          fontSize={56}
          colors={["#ff6b6b", "#feca57", "#48dbfb", "#ff6b6b"]}
          speed={2}
        />
      </div>

      {/* 5-6秒: 动态排版 */}
      <div style={{ position: "absolute", top: 1200, width: "100%" }}>
        <KineticText
          lines={[
            { text: "动态排版", fontSize: 48, color: "#feca57", delay: 150, animation: "pop" },
            { text: "Kinetic Typography", fontSize: 32, color: "#ffffff", delay: 160, animation: "slide" },
          ]}
        />
      </div>
    </AbsoluteFill>
  );
};

export default TextAnimationTest;
