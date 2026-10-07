import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";

/**
 * 豆包被打 - 精细版动画 v2
 * 4层结构中的第4层（透明背景动画层）
 *
 * 剧情时间线（20秒，30fps = 600帧）：
 * 0-180帧  (0-6s):   静态，头像框里豆包正常
 * 180-270帧 (6-9s):  被打，震动，出现伤痕
 * 270-360帧 (9-12s):  掉下去（加速下落，旋转）
 * 360-450帧 (12-15s): 作品区打斗，卡片被打碎
 * 450-540帧 (15-18s): 从底部爬上来
 * 540-600帧 (18-20s): 满身伤痕爬回头像框，委屈状
 *
 * 画布：1080x1920（竖屏）
 */

// 头像框中心坐标（基于1080x1920画布）
const AVATAR_CENTER = { x: 200, y: 380 };
const AVATAR_RADIUS = 140;

// 作品卡片位置（3列）
const CARD_POSITIONS = [
  { x: 180, y: 1350 },
  { x: 540, y: 1350 },
  { x: 900, y: 1350 },
];
const CARD_SIZE = { w: 300, h: 400 };

// ==================== 豆包机器人SVG角色 ====================

const DoubaoRobot: React.FC<{
  x: number;
  y: number;
  scale: number;
  rotation: number;
  expression: "normal" | "happy" | "hurt" | "sad" | "angry";
  bruised: boolean;
  opacity?: number;
}> = ({ x, y, scale, rotation, expression, bruised, opacity = 1 }) => {
  const size = 160 * scale;

  return (
    <div
      style={{
        position: "absolute",
        left: x - size / 2,
        top: y - size / 2,
        width: size,
        height: size,
        transform: `rotate(${rotation}deg)`,
        opacity,
      }}
    >
      <svg viewBox="0 0 160 160" width={size} height={size}>
        {/* 头部 */}
        <defs>
          <linearGradient id="headGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#E8E8E8" />
            <stop offset="100%" stopColor="#B0B0B0" />
          </linearGradient>
          <linearGradient id="faceGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#FFFFFF" />
            <stop offset="100%" stopColor="#F0F0F0" />
          </linearGradient>
        </defs>

        {/* 头部外壳 */}
        <ellipse cx="80" cy="75" rx="65" ry="60" fill="url(#headGrad)" stroke="#888" strokeWidth="2" />

        {/* 面部区域 */}
        <ellipse cx="80" cy="80" rx="50" ry="45" fill="url(#faceGrad)" />

        {/* 天线 */}
        <line x1="80" y1="15" x2="80" y2="5" stroke="#666" strokeWidth="3" />
        <circle cx="80" cy="3" r="5" fill="#FF6B6B" />

        {/* 眼睛 */}
        {expression === "hurt" ? (
          <>
            {/* 受伤眼：X形 */}
            <line x1="55" y1="65" x2="67" y2="77" stroke="#333" strokeWidth="3" />
            <line x1="67" y1="65" x2="55" y2="77" stroke="#333" strokeWidth="3" />
            <line x1="93" y1="65" x2="105" y2="77" stroke="#333" strokeWidth="3" />
            <line x1="105" y1="65" x2="93" y2="77" stroke="#333" strokeWidth="3" />
          </>
        ) : expression === "sad" ? (
          <>
            {/* 委屈眼：下垂+泪光 */}
            <ellipse cx="61" cy="72" rx="8" ry="10" fill="#333" />
            <ellipse cx="99" cy="72" rx="8" ry="10" fill="#333" />
            <circle cx="64" cy="68" r="3" fill="#FFF" />
            <circle cx="102" cy="68" r="3" fill="#FFF" />
            {/* 泪痕 */}
            <ellipse cx="55" cy="85" rx="3" ry="6" fill="#87CEEB" opacity="0.8" />
            <ellipse cx="105" cy="85" rx="3" ry="6" fill="#87CEEB" opacity="0.8" />
          </>
        ) : expression === "angry" ? (
          <>
            {/* 愤怒眼：皱眉 */}
            <line x1="50" y1="58" x2="70" y2="65" stroke="#333" strokeWidth="3" />
            <line x1="110" y1="58" x2="90" y2="65" stroke="#333" strokeWidth="3" />
            <ellipse cx="61" cy="75" rx="7" ry="8" fill="#333" />
            <ellipse cx="99" cy="75" rx="7" ry="8" fill="#333" />
          </>
        ) : (
          <>
            {/* 正常/开心眼 */}
            <ellipse cx="61" cy="72" rx="8" ry="10" fill="#333" />
            <ellipse cx="99" cy="72" rx="8" ry="10" fill="#333" />
            <circle cx="64" cy="68" r="3" fill="#FFF" />
            <circle cx="102" cy="68" r="3" fill="#FFF" />
          </>
        )}

        {/* 嘴巴 */}
        {expression === "happy" ? (
          <path d="M 65 95 Q 80 110 95 95" stroke="#333" strokeWidth="3" fill="none" />
        ) : expression === "sad" ? (
          <path d="M 65 100 Q 80 88 95 100" stroke="#333" strokeWidth="3" fill="none" />
        ) : expression === "hurt" ? (
          <ellipse cx="80" cy="98" rx="8" ry="6" fill="#333" />
        ) : (
          <rect x="70" y="93" width="20" height="5" rx="2" fill="#333" />
        )}

        {/* 脸颊红晕（开心时） */}
        {expression === "happy" && (
          <>
            <ellipse cx="50" cy="88" rx="8" ry="5" fill="#FFB6C1" opacity="0.6" />
            <ellipse cx="110" cy="88" rx="8" ry="5" fill="#FFB6C1" opacity="0.6" />
          </>
        )}

        {/* 伤痕 */}
        {bruised && (
          <>
            {/* 左眼眶淤青 */}
            <ellipse cx="55" cy="68" rx="15" ry="12" fill="#8B0000" opacity="0.4" />
            {/* 右脸颊划伤 */}
            <path d="M 100 80 L 115 90" stroke="#FF0000" strokeWidth="2" fill="none" />
            {/* 额头包 */}
            <ellipse cx="80" cy="30" rx="12" ry="8" fill="#FF6B6B" opacity="0.7" />
            {/* 创可贴 */}
            <rect x="40" y="50" width="20" height="8" rx="2" fill="#F5DEB3" transform="rotate(-20 50 54)" />
            <line x1="50" y1="50" x2="50" y2="58" stroke="#DDD" strokeWidth="1" transform="rotate(-20 50 54)" />
          </>
        )}

        {/* 身体（小部分露出） */}
        <rect x="55" y="130" width="50" height="25" rx="8" fill="url(#headGrad)" stroke="#888" strokeWidth="1" />
      </svg>
    </div>
  );
};

// ==================== 作品卡片 ====================

const WorkCard: React.FC<{
  x: number;
  y: number;
  w: number;
  h: number;
  broken: boolean;
  breakProgress: number;
  index: number;
  shake: number;
}> = ({ x, y, w, h, broken, breakProgress, index, shake }) => {
  if (!broken) {
    return (
      <div
        style={{
          position: "absolute",
          left: x - w / 2 + shake,
          top: y - h / 2,
          width: w,
          height: h,
          background: `linear-gradient(135deg, ${
            index === 0 ? "#4A90D9" : index === 1 ? "#E8A838" : "#D94A4A"
          } 0%, ${
            index === 0 ? "#2A5A8A" : index === 1 ? "#B87818" : "#A82A2A"
          } 100%)`,
          borderRadius: 12,
          boxShadow: "0 6px 20px rgba(0,0,0,0.3)",
          overflow: "hidden",
        }}
      >
        {/* 卡片内容模拟 */}
        <div style={{ position: "absolute", top: "20%", left: "10%", right: "10%", height: "50%", background: "rgba(255,255,255,0.2)", borderRadius: 8 }} />
        <div style={{ position: "absolute", bottom: "10%", left: "10%", width: "40%", height: "8%", background: "rgba(255,255,255,0.5)", borderRadius: 4 }} />
        <div style={{ position: "absolute", bottom: "10%", right: "10%", width: "20%", height: "8%", background: "rgba(255,100,100,0.8)", borderRadius: 4 }} />
      </div>
    );
  }

  // 打碎效果：分裂成6块飞散
  const pieces = [
    { dx: -120, dy: -100, rot: -45, delay: 0 },
    { dx: 100, dy: -80, rot: 35, delay: 0.05 },
    { dx: -90, dy: 90, rot: 30, delay: 0.1 },
    { dx: 110, dy: 100, rot: -40, delay: 0.15 },
    { dx: 0, dy: -120, rot: 20, delay: 0.08 },
    { dx: 0, dy: 120, rot: -25, delay: 0.12 },
  ];

  return (
    <>
      {pieces.map((p, i) => {
        const t = Math.max(0, Math.min(1, (breakProgress - p.delay) / (1 - p.delay)));
        if (t <= 0) return null;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x - w / 2 + p.dx * t,
              top: y - h / 2 + p.dy * t,
              width: w / 2.5,
              height: h / 3,
              background: `linear-gradient(135deg, ${
                index === 0 ? "#4A90D9" : index === 1 ? "#E8A838" : "#D94A4A"
              } 0%, ${
                index === 0 ? "#2A5A8A" : index === 1 ? "#B87818" : "#A82A2A"
              } 100%)`,
              transform: `rotate(${p.rot * t}deg)`,
              opacity: 1 - t * 0.3,
              borderRadius: 6,
              boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
            }}
          />
        );
      })}
    </>
  );
};

// ==================== 打击特效 ====================

const HitEffect: React.FC<{
  x: number;
  y: number;
  intensity: number;
  text?: string;
}> = ({ x, y, intensity, text = "砰!" }) => {
  if (intensity <= 0) return null;

  return (
    <div
      style={{
        position: "absolute",
        left: x - 80,
        top: y - 80,
        width: 160,
        height: 160,
        opacity: intensity,
      }}
    >
      {/* 冲击波圆环 */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          width: 40 + intensity * 80,
          height: 40 + intensity * 80,
          border: `4px solid #FFD700`,
          borderRadius: "50%",
          transform: "translate(-50%, -50%)",
          boxShadow: "0 0 20px #FFD700",
        }}
      />
      {/* 星星 */}
      {[0, 60, 120, 180, 240, 300].map((angle) => (
        <div
          key={angle}
          style={{
            position: "absolute",
            left: "50%",
            top: "50%",
            fontSize: 20 + intensity * 10,
            transform: `translate(-50%, -50%) rotate(${angle}deg) translateY(-${30 + intensity * 40}px)`,
            color: "#FFD700",
            textShadow: "0 0 8px #FFA500",
          }}
        >
          ★
        </div>
      ))}
      {/* 文字 */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          transform: "translate(-50%, -50%)",
          fontSize: 32 + intensity * 16,
          fontWeight: "bold",
          color: "#FF4444",
          textShadow: "2px 2px 4px rgba(0,0,0,0.5), 0 0 10px #FF6B6B",
          whiteSpace: "nowrap",
        }}
      >
        {text}
      </div>
    </div>
  );
};

// ==================== 主动画组件 ====================

export const DoubaoHitAnimation: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // 时间节点（帧）
  const F_IDLE_END = 180;    // 6秒：静态
  const F_HIT_END = 270;     // 9秒：被打
  const F_FALL_END = 360;    // 12秒：掉下去
  const F_FIGHT_END = 450;   // 15秒：作品区打斗
  const F_CLIMB_END = 540;   // 18秒：爬上来
  const F_END = 600;         // 20秒：结束

  // 豆包状态
  let doubaoX = AVATAR_CENTER.x;
  let doubaoY = AVATAR_CENTER.y;
  let doubaoScale = 1.0;
  let doubaoRotation = 0;
  let doubaoOpacity = 1;
  let expression: "normal" | "happy" | "hurt" | "sad" | "angry" = "normal";
  let bruised = false;

  // 作品卡片状态
  let cardsBroken = false;
  let breakProgress = 0;
  let cardShake = 0;

  // 打击特效
  let hitIntensity = 0;
  let hitX = AVATAR_CENTER.x;
  let hitY = AVATAR_CENTER.y;
  let hitText = "砰!";

  if (frame <= F_IDLE_END) {
    // 0-6秒：静态，轻微呼吸
    const t = frame / F_IDLE_END;
    doubaoY = AVATAR_CENTER.y + Math.sin(t * Math.PI * 4) * 3;
    doubaoScale = 1.0 + Math.sin(t * Math.PI * 4) * 0.02;
    expression = "normal";
  } else if (frame <= F_HIT_END) {
    // 6-9秒：被打
    const t = (frame - F_IDLE_END) / (F_HIT_END - F_IDLE_END);

    // 多次打击
    const hitCount = Math.floor(t * 5);
    const hitPhase = (t * 5) % 1;

    // 震动
    const shake = Math.sin(frame * 2.5) * (15 - t * 10);
    doubaoX = AVATAR_CENTER.x + shake;
    doubaoY = AVATAR_CENTER.y + Math.cos(frame * 2) * 8;
    doubaoRotation = Math.sin(frame * 3) * (10 - t * 5);
    doubaoScale = 1.0 + Math.abs(Math.sin(frame * 2.5)) * 0.1;

    // 表情变化
    if (hitCount < 2) {
      expression = "hurt";
    } else {
      expression = "angry";
    }
    bruised = t > 0.3;

    // 打击特效（每次打击开始时）
    if (hitPhase < 0.2) {
      hitIntensity = 1 - hitPhase / 0.2;
      hitX = AVATAR_CENTER.x + (Math.random() - 0.5) * 40;
      hitY = AVATAR_CENTER.y + (Math.random() - 0.5) * 40;
      hitText = hitCount % 2 === 0 ? "砰!" : "啪!";
    }
  } else if (frame <= F_FALL_END) {
    // 9-12秒：掉下去（加速下落）
    const t = (frame - F_HIT_END) / (F_FALL_END - F_HIT_END);
    bruised = true;
    expression = "hurt";

    // 抛物线下落
    doubaoY = AVATAR_CENTER.y + t * t * 1600; // 加速下落
    doubaoX = AVATAR_CENTER.x + Math.sin(t * Math.PI) * 80;
    doubaoRotation = t * 360; // 旋转下落
    doubaoScale = 1.0 - t * 0.3;
    doubaoOpacity = 1 - t * 0.3;

    // 最后一帧完全消失
    if (t > 0.9) {
      doubaoOpacity = 1 - (t - 0.9) / 0.1;
    }
  } else if (frame <= F_FIGHT_END) {
    // 12-15秒：作品区打斗，卡片被打碎
    const t = (frame - F_FALL_END) / (F_FIGHT_END - F_FALL_END);

    // 豆包在作品区出现（从中间卡片后面）
    const appear = spring({ frame: t * fps, fps, config: { damping: 10 } });
    doubaoX = CARD_POSITIONS[1].x;
    doubaoY = CARD_POSITIONS[1].y - appear * 100;
    doubaoScale = 0.8 + appear * 0.4;
    doubaoRotation = Math.sin(frame * 4) * 20;
    expression = "angry";
    bruised = true;
    doubaoOpacity = appear;

    // 卡片震动
    cardShake = Math.sin(frame * 6) * (10 * (1 - t * 0.5));

    // 卡片打碎（在打斗中段开始）
    if (t > 0.2) {
      cardsBroken = true;
      breakProgress = Math.min(1, (t - 0.2) / 0.5);
    }

    // 打击特效
    if (t > 0.1 && t < 0.8) {
      const hitPhase = (t * 8) % 1;
      if (hitPhase < 0.15) {
        hitIntensity = 1 - hitPhase / 0.15;
        hitX = CARD_POSITIONS[1].x + (Math.random() - 0.5) * 100;
        hitY = CARD_POSITIONS[1].y + (Math.random() - 0.5) * 100;
        hitText = ["砰!", "啪!", "咚!", "哐!"][Math.floor(t * 8) % 4];
      }
    }
  } else if (frame <= F_CLIMB_END) {
    // 15-18秒：从底部爬上来
    const t = (frame - F_FIGHT_END) / (F_CLIMB_END - F_FIGHT_END);
    bruised = true;

    // 从底部爬向头像框
    const climb = spring({
      frame: t * fps * 0.7,
      fps,
      config: { damping: 14 },
    });

    // 路径：底部 → 作品区 → 头像框
    const startY = 1920 + 100;
    const endY = AVATAR_CENTER.y + 100;
    doubaoY = startY - climb * (startY - endY);
    doubaoX = AVATAR_CENTER.x + Math.sin(climb * Math.PI) * 100;
    doubaoRotation = Math.sin(climb * Math.PI * 4) * 15;
    doubaoScale = 0.7 + climb * 0.3;
    doubaoOpacity = Math.min(1, climb * 2);

    // 表情：先痛苦后委屈
    expression = climb > 0.6 ? "sad" : "hurt";

    cardsBroken = true;
    breakProgress = 1;
  } else {
    // 18-20秒：满身伤痕爬回头像框，委屈状
    const t = (frame - F_CLIMB_END) / (F_END - F_CLIMB_END);
    bruised = true;
    expression = "sad";

    // 稳定在头像框位置，轻微颤抖
    const settle = spring({
      frame: t * fps,
      fps,
      config: { damping: 8 },
    });

    doubaoY = AVATAR_CENTER.y + 20 - settle * 20 + Math.sin(frame * 0.5) * 2;
    doubaoX = AVATAR_CENTER.x + Math.sin(frame * 0.3) * 3;
    doubaoScale = 1.0 - settle * 0.05;
    doubaoRotation = Math.sin(frame * 0.5) * 2;

    cardsBroken = true;
    breakProgress = 1;
  }

  return (
    <AbsoluteFill style={{ backgroundColor: "transparent" }}>
      {/* 作品卡片（在豆包后面） */}
      {CARD_POSITIONS.map((pos, i) => (
        <WorkCard
          key={i}
          x={pos.x}
          y={pos.y}
          w={CARD_SIZE.w}
          h={CARD_SIZE.h}
          broken={cardsBroken}
          breakProgress={breakProgress}
          index={i}
          shake={i === 1 ? cardShake : cardShake * 0.5}
        />
      ))}

      {/* 打击特效 */}
      <HitEffect x={hitX} y={hitY} intensity={hitIntensity} text={hitText} />

      {/* 豆包角色 */}
      <DoubaoRobot
        x={doubaoX}
        y={doubaoY}
        scale={doubaoScale}
        rotation={doubaoRotation}
        expression={expression}
        bruised={bruised}
        opacity={doubaoOpacity}
      />
    </AbsoluteFill>
  );
};

export default DoubaoHitAnimation;
