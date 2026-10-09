"""
Remotion 2D角色动画系统
- 角色部件管理
- 骨骼动画
- 表情系统
- 动作预设
- 角色组件代码生成
"""

import os
import sys
import logging
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CharacterPart:
    """角色部件"""
    name: str
    image_path: str = ""
    position: Tuple[float, float] = (0, 0)
    rotation: float = 0.0
    scale: Tuple[float, float] = (1, 1)
    opacity: float = 1.0
    z_index: int = 0


@dataclass
class CharacterConfig:
    """角色配置"""
    name: str = "Character"
    width: int = 300
    height: int = 400
    parts: List[CharacterPart] = field(default_factory=list)
    anchor_point: Tuple[float, float] = (0.5, 0.5)


# 动作预设
ACTION_PRESETS = {
    "idle": {
        "description": "待机呼吸动画",
        "duration": 60,
        "animations": [
            {"part": "body", "property": "scale", "keyframes": [(0, 1.0), (30, 1.02), (60, 1.0)]},
            {"part": "head", "property": "rotation", "keyframes": [(0, 0), (30, 2), (60, 0)]},
        ],
    },
    "walk": {
        "description": "行走动画",
        "duration": 30,
        "animations": [
            {"part": "body", "property": "positionY", "keyframes": [(0, 0), (15, -10), (30, 0)]},
            {"part": "left_arm", "property": "rotation", "keyframes": [(0, -20), (15, 20), (30, -20)]},
            {"part": "right_arm", "property": "rotation", "keyframes": [(0, 20), (15, -20), (30, 20)]},
            {"part": "left_leg", "property": "rotation", "keyframes": [(0, 15), (15, -15), (30, 15)]},
            {"part": "right_leg", "property": "rotation", "keyframes": [(0, -15), (15, 15), (30, -15)]},
        ],
    },
    "jump": {
        "description": "跳跃动画",
        "duration": 40,
        "animations": [
            {"part": "body", "property": "positionY", "keyframes": [(0, 0), (20, -80), (40, 0)]},
            {"part": "body", "property": "scaleY", "keyframes": [(0, 1.0), (10, 0.8), (20, 1.1), (40, 1.0)]},
            {"part": "left_arm", "property": "rotation", "keyframes": [(0, 0), (20, -45), (40, 0)]},
            {"part": "right_arm", "property": "rotation", "keyframes": [(0, 0), (20, 45), (40, 0)]},
        ],
    },
    "wave": {
        "description": "挥手动画",
        "duration": 60,
        "animations": [
            {"part": "right_arm", "property": "rotation", "keyframes": [(0, -30), (15, -60), (30, -30), (45, -60), (60, -30)]},
            {"part": "head", "property": "rotation", "keyframes": [(0, 0), (30, 5), (60, 0)]},
        ],
    },
    "nod": {
        "description": "点头动画",
        "duration": 30,
        "animations": [
            {"part": "head", "property": "rotation", "keyframes": [(0, 0), (10, 15), (20, -5), (30, 0)]},
        ],
    },
    "shake": {
        "description": "摇头动画",
        "duration": 40,
        "animations": [
            {"part": "head", "property": "rotation", "keyframes": [(0, 0), (10, -15), (20, 15), (30, -10), (40, 0)]},
        ],
    },
    "sad": {
        "description": "悲伤低头",
        "duration": 45,
        "animations": [
            {"part": "head", "property": "rotation", "keyframes": [(0, 0), (45, 25)]},
            {"part": "body", "property": "scaleY", "keyframes": [(0, 1.0), (45, 0.95)]},
            {"part": "left_arm", "property": "rotation", "keyframes": [(0, 0), (45, 10)]},
            {"part": "right_arm", "property": "rotation", "keyframes": [(0, 0), (45, -10)]},
        ],
    },
    "happy": {
        "description": "开心跳动",
        "duration": 30,
        "animations": [
            {"part": "body", "property": "positionY", "keyframes": [(0, 0), (15, -20), (30, 0)]},
            {"part": "body", "property": "scaleY", "keyframes": [(0, 1.0), (10, 1.1), (20, 0.95), (30, 1.0)]},
            {"part": "left_arm", "property": "rotation", "keyframes": [(0, 0), (15, -30), (30, 0)]},
            {"part": "right_arm", "property": "rotation", "keyframes": [(0, 0), (15, 30), (30, 0)]},
        ],
    },
}

# 表情预设
EXPRESSION_PRESETS = {
    "happy": {"eyes": "happy", "mouth": "smile", "brows": "normal"},
    "sad": {"eyes": "sad", "mouth": "frown", "brows": "sad"},
    "angry": {"eyes": "angry", "mouth": "grimace", "brows": "angry"},
    "surprised": {"eyes": "wide", "mouth": "open", "brows": "raised"},
    "neutral": {"eyes": "normal", "mouth": "closed", "brows": "normal"},
    "wink": {"eyes": "wink", "mouth": "smirk", "brows": "normal"},
}


class CharacterAnimator:
    """Remotion 2D角色动画器"""

    def __init__(self):
        self.actions = ACTION_PRESETS
        self.expressions = EXPRESSION_PRESETS

    def generate_character_component(
        self,
        config: CharacterConfig,
        output_path: str,
        action: str = "idle",
        expression: str = "neutral",
    ) -> str:
        """生成Remotion角色组件代码

        Args:
            config: 角色配置
            output_path: 输出路径
            action: 动作预设
            expression: 表情预设

        Returns:
            生成的文件路径
        """
        action_data = self.actions.get(action, self.actions["idle"])
        expr_data = self.expressions.get(expression, self.expressions["neutral"])

        # 生成部件导入
        parts_import = ""
        for part in config.parts:
            if part.image_path:
                var_name = part.name.replace(" ", "_")
                parts_import += f"import {var_name} from '{part.image_path}';\n"

        # 生成动画插值代码
        animation_code = ""
        for anim in action_data["animations"]:
            part_name = anim["part"]
            prop = anim["property"]
            keyframes = anim["keyframes"]

            if len(keyframes) == 2:
                (f1, v1), (f2, v2) = keyframes
                animation_code += f"""
  const {part_name}_{prop} = interpolate(frame, [{f1}, {f2}], [{v1}, {v2}], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});
"""
            else:
                frames = [k[0] for k in keyframes]
                values = [k[1] for k in keyframes]
                animation_code += f"""
  const {part_name}_{prop} = interpolate(frame, [{', '.join(map(str, frames))}], [{', '.join(map(str, values))}], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});
"""

        # 生成部件渲染代码
        parts_render = ""
        for part in sorted(config.parts, key=lambda p: p.z_index):
            var_name = part.name.replace(" ", "_")
            pos_x, pos_y = part.position

            parts_render += f"""
        <div style={{
          position: 'absolute',
          left: '{pos_x}px',
          top: '{pos_y}px',
          transform: `rotate(${{{part.name}_rotation || 0}}deg) scale(${{{part.name}_scale || 1}})`,
          opacity: {part.opacity},
          zIndex: {part.z_index},
        }}>
          <img src={{{var_name}}} style={{width: '100%', height: '100%'}} />
        </div>
"""

        component_code = f"""import React from 'react';
import {{ AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig }} from 'remotion';
{parts_import}

// 角色: {config.name}
// 动作: {action} ({action_data['description']})
// 表情: {expression} ({expr_data})

export const {config.name.replace(' ', '')}: React.FC = () => {{
  const frame = useCurrentFrame();
  const {{ fps }} = useVideoConfig();

{animation_code}
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
      <div style={{
        position: 'relative',
        width: '{config.width}px',
        height: '{config.height}px',
      }}>
{parts_render}
      </div>
    </AbsoluteFill>
  );
}};
"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(component_code)

        logger.info(f"角色组件已生成: {output_path}")
        return output_path

    def generate_simple_character(
        self,
        output_path: str,
        character_name: str = "SimpleCharacter",
        action: str = "idle",
    ) -> str:
        """生成简化版角色组件（使用CSS形状，无需图片素材）

        Args:
            output_path: 输出路径
            character_name: 角色名
            action: 动作预设

        Returns:
            生成的文件路径
        """
        action_data = self.actions.get(action, self.actions["idle"])

        # 生成动画代码
        animation_code = ""
        for anim in action_data["animations"]:
            part_name = anim["part"]
            prop = anim["property"]
            keyframes = anim["keyframes"]
            frames = [k[0] for k in keyframes]
            values = [k[1] for k in keyframes]
            animation_code += f"""
  const {part_name}_{prop} = interpolate(frame, [{', '.join(map(str, frames))}], [{', '.join(map(str, values))}], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});
"""

        component_code = f"""import React from 'react';
import {{ AbsoluteFill, interpolate, useCurrentFrame }} from 'remotion';

// 简化角色: {character_name}
// 动作: {action} ({action_data['description']})
// 使用CSS形状，无需图片素材

export const {character_name}: React.FC = () => {{
  const frame = useCurrentFrame();
{animation_code}
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
      <div style={{ position: 'relative', width: 200, height: 300 }}>
        <div style={{
          position: 'absolute',
          left: 50, top: 0,
          width: 100, height: 100,
          borderRadius: '50%',
          backgroundColor: '#FFD5B8',
          transform: `rotate(${{head_rotation || 0}}deg)`,
        }}>
          <div style={{ position: 'absolute', left: 25, top: 35, width: 15, height: 15, borderRadius: '50%', backgroundColor: '#333' }} />
          <div style={{ position: 'absolute', right: 25, top: 35, width: 15, height: 15, borderRadius: '50%', backgroundColor: '#333' }} />
          <div style={{ position: 'absolute', left: 35, bottom: 20, width: 30, height: 10, borderBottom: '3px solid #333', borderRadius: '0 0 15px 15px' }} />
        </div>
        <div style={{
          position: 'absolute',
          left: 60, top: 95,
          width: 80, height: 120,
          borderRadius: '20px 20px 10px 10px',
          backgroundColor: '#4A90D9',
          transform: `scaleY(${{body_scaleY || 1}}) translateY(${{body_positionY || 0}}px)`,
        }} />
        <div style={{
          position: 'absolute',
          left: 35, top: 100,
          width: 25, height: 80,
          borderRadius: 12,
          backgroundColor: '#FFD5B8',
          transformOrigin: 'top center',
          transform: `rotate(${{left_arm_rotation || 0}}deg)`,
        }} />
        <div style={{
          position: 'absolute',
          right: 35, top: 100,
          width: 25, height: 80,
          borderRadius: 12,
          backgroundColor: '#FFD5B8',
          transformOrigin: 'top center',
          transform: `rotate(${{right_arm_rotation || 0}}deg)`,
        }} />
        <div style={{
          position: 'absolute',
          left: 65, top: 210,
          width: 25, height: 70,
          borderRadius: 12,
          backgroundColor: '#2C3E50',
          transformOrigin: 'top center',
          transform: `rotate(${{left_leg_rotation || 0}}deg)`,
        }} />
        <div style={{
          position: 'absolute',
          right: 65, top: 210,
          width: 25, height: 70,
          borderRadius: 12,
          backgroundColor: '#2C3E50',
          transformOrigin: 'top center',
          transform: `rotate(${{right_leg_rotation || 0}}deg)`,
        }} />
      </div>
    </AbsoluteFill>
  );
}};
"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(component_code)

        logger.info(f"简化角色组件已生成: {output_path}")
        return output_path

    def list_actions(self) -> List[str]:
        """列出所有动作预设"""
        return list(self.actions.keys())

    def list_expressions(self) -> List[str]:
        """列出所有表情预设"""
        return list(self.expressions.keys())


def main():
    """测试角色动画器"""
    animator = CharacterAnimator()

    print(f"可用动作 ({len(animator.list_actions())}种):")
    for name in animator.list_actions():
        print(f"  - {name}: {animator.actions[name]['description']}")

    print(f"\n可用表情 ({len(animator.list_expressions())}种):")
    for name in animator.list_expressions():
        print(f"  - {name}")

    # 生成简化角色
    output = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\remotion\SimpleCharacter.tsx"
    path = animator.generate_simple_character(output, action="walk")
    print(f"\n生成文件: {path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
