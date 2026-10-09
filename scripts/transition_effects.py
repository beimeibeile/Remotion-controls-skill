"""
Remotion转场特效库
- 淡入淡出
- 滑动转场
- 缩放转场
- 旋转转场
- 模糊转场
- 故障效果转场
- 转场组件代码生成
"""

import os
import sys
import logging
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class TransitionConfig:
    """转场配置"""
    transition_type: str = "fade"  # fade/slide_left/slide_right/slide_up/slide_down/scale/rotate/blur/glitch/wipe
    duration: int = 30
    direction: str = "left"  # left/right/up/down
    easing: str = "ease_in_out"
    color: str = "#000000"


# 转场预设
TRANSITION_PRESETS = {
    "fade": {
        "description": "淡入淡出",
        "duration": 30,
        "easing": "ease_in_out",
    },
    "slide_left": {
        "description": "向左滑动",
        "duration": 30,
        "easing": "ease_in_out",
        "direction": "left",
    },
    "slide_right": {
        "description": "向右滑动",
        "duration": 30,
        "easing": "ease_in_out",
        "direction": "right",
    },
    "slide_up": {
        "description": "向上滑动",
        "duration": 30,
        "easing": "ease_in_out",
        "direction": "up",
    },
    "slide_down": {
        "description": "向下滑动",
        "duration": 30,
        "easing": "ease_in_out",
        "direction": "down",
    },
    "scale_in": {
        "description": "缩放进入",
        "duration": 30,
        "easing": "ease_out_back",
        "from_scale": 0.5,
    },
    "scale_out": {
        "description": "缩放退出",
        "duration": 30,
        "easing": "ease_in_back",
        "to_scale": 1.5,
    },
    "rotate": {
        "description": "旋转转场",
        "duration": 45,
        "easing": "ease_in_out",
        "rotation": 180,
    },
    "blur": {
        "description": "模糊转场",
        "duration": 30,
        "easing": "ease_in_out",
        "max_blur": 20,
    },
    "glitch": {
        "description": "故障效果",
        "duration": 20,
        "easing": "linear",
        "intensity": 10,
    },
    "wipe_left": {
        "description": "向左擦除",
        "duration": 30,
        "easing": "ease_in_out",
        "direction": "left",
    },
    "wipe_right": {
        "description": "向右擦除",
        "duration": 30,
        "easing": "ease_in_out",
        "direction": "right",
    },
    "circle_reveal": {
        "description": "圆形揭示",
        "duration": 45,
        "easing": "ease_in_out",
    },
    "pixelate": {
        "description": "像素化转场",
        "duration": 20,
        "easing": "ease_in_out",
        "max_pixel": 50,
    },
}


class TransitionEffects:
    """Remotion转场特效库"""

    def __init__(self):
        self.presets = TRANSITION_PRESETS

    def generate_transition_component(
        self,
        config: TransitionConfig,
        output_path: str,
        component_name: str = "Transition",
    ) -> str:
        """生成转场组件代码

        Args:
            config: 转场配置
            output_path: 输出路径
            component_name: 组件名

        Returns:
            生成的文件路径
        """
        t_type = config.transition_type
        duration = config.duration

        # 根据转场类型生成动画逻辑
        if t_type == "fade":
            anim_logic = f"""
  const progress = interpolate(frame, [0, {duration}], [0, 1], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});
  const opacity = 1 - progress;
  const transform = 'none';
  const filter = 'none';
"""
        elif t_type.startswith("slide_"):
            direction = t_type.replace("slide_", "")
            if direction == "left":
                anim_logic = f"""
  const progress = interpolate(frame, [0, {duration}], [0, 1], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});
  const translateX = progress * -1920;
  const opacity = 1;
  const transform = `translateX(${{translateX}}px)`;
  const filter = 'none';
"""
            elif direction == "right":
                anim_logic = f"""
  const progress = interpolate(frame, [0, {duration}], [0, 1], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});
  const translateX = progress * 1920;
  const opacity = 1;
  const transform = `translateX(${{translateX}}px)`;
  const filter = 'none';
"""
            elif direction == "up":
                anim_logic = f"""
  const progress = interpolate(frame, [0, {duration}], [0, 1], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});
  const translateY = progress * -1080;
  const opacity = 1;
  const transform = `translateY(${{translateY}}px)`;
  const filter = 'none';
"""
            else:  # down
                anim_logic = f"""
  const progress = interpolate(frame, [0, {duration}], [0, 1], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});
  const translateY = progress * 1080;
  const opacity = 1;
  const transform = `translateY(${{translateY}}px)`;
  const filter = 'none';
"""
        elif t_type == "scale_in":
            anim_logic = f"""
  const progress = interpolate(frame, [0, {duration}], [0, 1], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});
  const scale = 0.5 + progress * 0.5;
  const opacity = progress;
  const transform = `scale(${{scale}})`;
  const filter = 'none';
"""
        elif t_type == "scale_out":
            anim_logic = f"""
  const progress = interpolate(frame, [0, {duration}], [0, 1], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});
  const scale = 1 + progress * 0.5;
  const opacity = 1 - progress;
  const transform = `scale(${{scale}})`;
  const filter = 'none';
"""
        elif t_type == "rotate":
            anim_logic = f"""
  const progress = interpolate(frame, [0, {duration}], [0, 1], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});
  const rotation = progress * 180;
  const scale = 1 - progress * 0.3;
  const opacity = 1 - progress;
  const transform = `rotate(${{rotation}}deg) scale(${{scale}})`;
  const filter = 'none';
"""
        elif t_type == "blur":
            anim_logic = f"""
  const progress = interpolate(frame, [0, {duration}], [0, 1], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});
  const blur = Math.sin(progress * Math.PI) * 20;
  const opacity = 1;
  const transform = 'none';
  const filter = `blur(${{blur}}px)`;
"""
        elif t_type == "glitch":
            anim_logic = f"""
  const progress = frame / {duration};
  const glitchX = (Math.random() - 0.5) * 20 * (1 - progress);
  const glitchY = (Math.random() - 0.5) * 10 * (1 - progress);
  const opacity = 1 - progress;
  const transform = `translate(${{glitchX}}px, ${{glitchY}}px)`;
  const filter = `hue-rotate(${{progress * 360}}deg)`;
"""
        elif t_type.startswith("wipe_"):
            direction = t_type.replace("wipe_", "")
            clip_path = "inset(0 100% 0 0)" if direction == "left" else "inset(0 0 0 100%)"
            anim_logic = f"""
  const progress = interpolate(frame, [0, {duration}], [0, 1], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});
  const clipPercent = progress * 100;
  const clipPath = '{clip_path}'.replace('100%', `${{100 - clipPercent}}%`);
  const opacity = 1;
  const transform = 'none';
  const filter = 'none';
"""
        elif t_type == "circle_reveal":
            anim_logic = f"""
  const progress = interpolate(frame, [0, {duration}], [0, 1], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});
  const radius = progress * 150;
  const clipPath = `circle(${{radius}}% at 50% 50%)`;
  const opacity = 1;
  const transform = 'none';
  const filter = 'none';
"""
        else:  # 默认fade
            anim_logic = f"""
  const progress = interpolate(frame, [0, {duration}], [0, 1], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});
  const opacity = 1 - progress;
  const transform = 'none';
  const filter = 'none';
"""

        component_code = f"""import React from 'react';
import {{ AbsoluteFill, interpolate, useCurrentFrame }} from 'remotion';

// 转场效果: {t_type} ({self.presets.get(t_type, {{}}).get('description', '自定义')})
// 转场时长: {duration}帧

export const {component_name}: React.FC<{{children: React.ReactNode}}> = ({{children}}) => {{
  const frame = useCurrentFrame();
{anim_logic}
  return (
    <AbsoluteFill style={{
      opacity,
      transform,
      filter,
      overflow: 'hidden',
    }}>
      {{children}}
    </AbsoluteFill>
  );
}};
"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(component_code)

        logger.info(f"转场组件已生成: {output_path}")
        return output_path

    def generate_transition_sequence(
        self,
        transitions: List[Dict[str, Any]],
        output_path: str,
        component_name: str = "TransitionSequence",
    ) -> str:
        """生成转场序列组件（多个转场组合）

        Args:
            transitions: 转场列表 [{type, start, duration}]
            output_path: 输出路径
            component_name: 组件名

        Returns:
            生成的文件路径
        """
        # 生成转场逻辑
        transition_logic = ""
        for i, t in enumerate(transitions):
            t_type = t.get("type", "fade")
            start = t.get("start", 0)
            duration = t.get("duration", 30)
            transition_logic += f"""
  // 转场 {i+1}: {t_type}
  const t{i}_progress = interpolate(frame, [{start}, {start + duration}], [0, 1], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});
"""

        component_code = f"""import React from 'react';
import {{ AbsoluteFill, interpolate, useCurrentFrame }} from 'remotion';

// 转场序列组件
// 共 {len(transitions)} 个转场

export const {component_name}: React.FC<{{children: React.ReactNode}}> = ({{children}}) => {{
  const frame = useCurrentFrame();
{transition_logic}
  return (
    <AbsoluteFill>
      {{children}}
    </AbsoluteFill>
  );
}};
"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(component_code)

        logger.info(f"转场序列组件已生成: {output_path}")
        return output_path

    def list_presets(self) -> List[str]:
        """列出所有转场预设"""
        return list(self.presets.keys())


def main():
    """测试转场特效库"""
    effects = TransitionEffects()

    print(f"可用转场效果 ({len(effects.list_presets())}种):")
    for name in effects.list_presets():
        print(f"  - {name}: {effects.presets[name]['description']}")

    # 生成淡入淡出转场
    config = TransitionConfig(transition_type="fade", duration=30)
    output = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\remotion\FadeTransition.tsx"
    path = effects.generate_transition_component(config, output, "FadeTransition")
    print(f"\n生成文件: {path}")

    # 生成滑动转场
    config2 = TransitionConfig(transition_type="slide_left", duration=30)
    output2 = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\remotion\SlideTransition.tsx"
    path2 = effects.generate_transition_component(config2, output2, "SlideTransition")
    print(f"生成文件: {path2}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
