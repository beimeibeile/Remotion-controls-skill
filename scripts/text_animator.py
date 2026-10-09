"""
Remotion文字动画系统
- 文字入场/出场动画
- 文字特效（打字机/霓虹/发光/渐变）
- 字幕动画
- 标题动画
- 文字组件代码生成
"""

import os
import sys
import logging
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class TextAnimationConfig:
    """文字动画配置"""
    text: str = "Hello World"
    font_size: int = 48
    font_family: str = "Arial"
    font_weight: str = "bold"
    color: str = "#FFFFFF"
    background_color: str = "transparent"
    position: Tuple[float, float] = (0.5, 0.5)  # 相对位置 0-1
    animation_type: str = "fade_in"  # fade_in/slide_up/typewriter/scale/neon/glow/gradient
    duration: int = 60
    start_frame: int = 0
    letter_spacing: float = 0.0
    line_height: float = 1.2
    text_align: str = "center"
    shadow: bool = False
    stroke_color: str = None
    stroke_width: float = 0.0


# 文字动画预设
TEXT_ANIMATION_PRESETS = {
    "fade_in": {
        "description": "淡入",
        "duration": 30,
        "easing": "ease_out",
    },
    "slide_up": {
        "description": "从下方滑入",
        "duration": 30,
        "easing": "ease_out",
        "distance": 50,
    },
    "slide_left": {
        "description": "从右方滑入",
        "duration": 30,
        "easing": "ease_out",
        "distance": 100,
    },
    "scale_in": {
        "description": "缩放进入",
        "duration": 30,
        "easing": "ease_out_back",
        "from_scale": 0.5,
    },
    "typewriter": {
        "description": "打字机效果",
        "duration": 60,
        "easing": "linear",
        "cursor": True,
    },
    "neon": {
        "description": "霓虹发光",
        "duration": 60,
        "easing": "ease_in_out",
        "glow_color": "#00FFFF",
        "pulse": True,
    },
    "glow": {
        "description": "发光脉冲",
        "duration": 60,
        "easing": "ease_in_out",
        "glow_color": "#FFD700",
    },
    "gradient": {
        "description": "渐变文字",
        "duration": 60,
        "easing": "linear",
        "colors": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FF6B6B"],
        "animate": True,
    },
    "bounce_in": {
        "description": "弹跳进入",
        "duration": 45,
        "easing": "ease_out_back",
        "bounces": 3,
    },
    "shake": {
        "description": "抖动效果",
        "duration": 30,
        "easing": "linear",
        "intensity": 5,
    },
    "blur_in": {
        "description": "模糊进入",
        "duration": 30,
        "easing": "ease_out",
        "from_blur": 10,
    },
    "rotate_in": {
        "description": "旋转进入",
        "duration": 45,
        "easing": "ease_out_back",
        "from_rotation": -180,
    },
}


class TextAnimator:
    """Remotion文字动画器"""

    def __init__(self):
        self.presets = TEXT_ANIMATION_PRESETS

    def generate_text_component(
        self,
        config: TextAnimationConfig,
        output_path: str,
        component_name: str = "AnimatedText",
    ) -> str:
        """生成Remotion文字动画组件

        Args:
            config: 文字动画配置
            output_path: 输出路径
            component_name: 组件名

        Returns:
            生成的文件路径
        """
        preset = self.presets.get(config.animation_type, self.presets["fade_in"])

        # 根据动画类型生成不同的动画逻辑
        if config.animation_type == "fade_in":
            anim_logic = f"""
  const opacity = interpolate(frame, [{config.start_frame}, {config.start_frame + preset['duration']}], [0, 1], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});
  const transform = 'none';
"""
        elif config.animation_type == "slide_up":
            anim_logic = f"""
  const opacity = interpolate(frame, [{config.start_frame}, {config.start_frame + preset['duration']}], [0, 1], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});
  const translateY = interpolate(frame, [{config.start_frame}, {config.start_frame + preset['duration']}], [{preset['distance']}, 0], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});
  const transform = `translateY(${{translateY}}px)`;
"""
        elif config.animation_type == "typewriter":
            text_len = len(config.text)
            anim_logic = f"""
  const charIndex = Math.floor(interpolate(frame, [{config.start_frame}, {config.start_frame + preset['duration']}], [0, {text_len}], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }}));
  const displayText = "{config.text}".substring(0, charIndex);
  const showCursor = {str(preset.get('cursor', False)).lower()};
  const opacity = 1;
  const transform = 'none';
"""
        elif config.animation_type == "neon":
            glow_color = preset.get("glow_color", "#00FFFF")
            anim_logic = f"""
  const opacity = interpolate(frame, [{config.start_frame}, {config.start_frame + 20}], [0, 1], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});
  const glowIntensity = interpolate(frame, [{config.start_frame + 20}, {config.start_frame + 40}, {config.start_frame + 60}], [10, 30, 10], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});
  const textShadow = `0 0 ${{glowIntensity}}px {glow_color}, 0 0 ${{glowIntensity * 2}}px {glow_color}, 0 0 ${{glowIntensity * 3}}px {glow_color}`;
  const transform = 'none';
"""
        elif config.animation_type == "scale_in":
            from_scale = preset.get("from_scale", 0.5)
            anim_logic = f"""
  const opacity = interpolate(frame, [{config.start_frame}, {config.start_frame + preset['duration']}], [0, 1], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});
  const scale = interpolate(frame, [{config.start_frame}, {config.start_frame + preset['duration']}], [{from_scale}, 1], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});
  const transform = `scale(${{scale}})`;
"""
        else:  # 默认fade_in
            anim_logic = f"""
  const opacity = interpolate(frame, [{config.start_frame}, {config.start_frame + preset['duration']}], [0, 1], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});
  const transform = 'none';
"""

        # 文字内容变量
        if config.animation_type == "typewriter":
            text_content = "{displayText}{showCursor && <span style={{animation: 'blink 1s infinite'}}>|</span>}"
        else:
            text_content = config.text

        # 阴影样式
        shadow_style = ""
        if config.shadow and config.animation_type != "neon":
            shadow_style = "textShadow: '2px 2px 4px rgba(0,0,0,0.5)',"

        # 描边样式
        stroke_style = ""
        if config.stroke_color and config.stroke_width > 0:
            stroke_style = f"WebkitTextStroke: '{config.stroke_width}px {config.stroke_color}',"

        component_code = f"""import React from 'react';
import {{ AbsoluteFill, interpolate, useCurrentFrame }} from 'remotion';

// 文字动画: {config.animation_type} ({preset['description']})
// 文字内容: {config.text}

export const {component_name}: React.FC = () => {{
  const frame = useCurrentFrame();
{anim_logic}
  return (
    <AbsoluteFill style={{
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: '{config.background_color}',
    }}>
      <div style={{
        fontSize: {config.font_size},
        fontFamily: '{config.font_family}',
        fontWeight: '{config.font_weight}',
        color: '{config.color}',
        opacity,
        transform,
        textAlign: '{config.text_align}',
        letterSpacing: '{config.letter_spacing}em',
        lineHeight: {config.line_height},
        {shadow_style}
        {stroke_style}
      }}>
        {text_content}
      </div>
    </AbsoluteFill>
  );
}};
"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(component_code)

        logger.info(f"文字动画组件已生成: {output_path}")
        return output_path

    def generate_subtitle_component(
        self,
        lines: List[Dict[str, Any]],
        output_path: str,
        component_name: str = "AnimatedSubtitles",
    ) -> str:
        """生成字幕动画组件

        Args:
            lines: 字幕行列表 [{text, start, duration, style}]
            output_path: 输出路径
            component_name: 组件名

        Returns:
            生成的文件路径
        """
        # 生成字幕行代码
        lines_code = ""
        for i, line in enumerate(lines):
            text = line.get("text", "")
            start = line.get("start", 0)
            duration = line.get("duration", 60)
            style = line.get("style", {})

            font_size = style.get("font_size", 36)
            color = style.get("color", "#FFFFFF")
            position = style.get("position", "bottom")

            if position == "bottom":
                top_style = "bottom: 60,"
            elif position == "top":
                top_style = "top: 60,"
            else:
                top_style = "justifyContent: 'center',"

            lines_code += f"""
        {{frame >= {start} && frame < {start + duration} && (
          <div style={{
            position: 'absolute',
            {top_style}
            left: 0,
            right: 0,
            textAlign: 'center',
            fontSize: {font_size},
            color: '{color}',
            fontWeight: 'bold',
            textShadow: '2px 2px 4px rgba(0,0,0,0.8)',
            opacity: interpolate(frame, [{start}, {start + 10}, {start + duration - 10}, {start + duration}], [0, 1, 1, 0], {{extrapolateRight: 'clamp', extrapolateLeft: 'clamp'}}),
          }}>
            {text}
          </div>
        )}}
"""

        component_code = f"""import React from 'react';
import {{ AbsoluteFill, interpolate, useCurrentFrame }} from 'remotion';

// 动画字幕组件
// 共 {len(lines)} 行字幕

export const {component_name}: React.FC = () => {{
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill>
{lines_code}
    </AbsoluteFill>
  );
}};
"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(component_code)

        logger.info(f"字幕组件已生成: {output_path} ({len(lines)}行)")
        return output_path

    def list_presets(self) -> List[str]:
        """列出所有文字动画预设"""
        return list(self.presets.keys())


def main():
    """测试文字动画器"""
    animator = TextAnimator()

    print(f"可用文字动画 ({len(animator.list_presets())}种):")
    for name in animator.list_presets():
        print(f"  - {name}: {animator.presets[name]['description']}")

    # 生成霓虹文字
    config = TextAnimationConfig(
        text="Hello Remotion!",
        font_size=72,
        color="#FFFFFF",
        animation_type="neon",
        background_color="#000000",
    )
    output = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\remotion\NeonText.tsx"
    path = animator.generate_text_component(config, output, "NeonText")
    print(f"\n生成文件: {path}")

    # 生成字幕
    lines = [
        {"text": "第一行字幕", "start": 0, "duration": 60, "style": {"font_size": 48}},
        {"text": "第二行字幕", "start": 60, "duration": 60, "style": {"font_size": 48, "color": "#FFD700"}},
    ]
    output2 = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\remotion\Subtitles.tsx"
    path2 = animator.generate_subtitle_component(lines, output2)
    print(f"生成字幕: {path2}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
