"""
Remotion UI动画组件库
- 按钮动画
- 进度条动画
- 加载动画
- 卡片动画
- 图标动画
- 数据可视化动画
- UI组件代码生成
"""

import os
import sys
import logging
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class UIAnimationConfig:
    """UI动画配置"""
    component_type: str = "button"  # button/progress/loader/card/icon/chart/counter
    animation_type: str = "pulse"  # pulse/bounce/fill/rotate/slide/count
    duration: int = 60
    color: str = "#4A90D9"
    secondary_color: str = "#FFFFFF"
    size: int = 100


# UI动画预设
UI_ANIMATION_PRESETS = {
    "button_pulse": {
        "description": "按钮脉冲动画",
        "component_type": "button",
        "animation_type": "pulse",
        "duration": 60,
    },
    "button_bounce": {
        "description": "按钮弹跳动画",
        "component_type": "button",
        "animation_type": "bounce",
        "duration": 45,
    },
    "progress_fill": {
        "description": "进度条填充动画",
        "component_type": "progress",
        "animation_type": "fill",
        "duration": 120,
    },
    "loader_spinner": {
        "description": "加载旋转动画",
        "component_type": "loader",
        "animation_type": "rotate",
        "duration": 60,
    },
    "loader_dots": {
        "description": "加载点动画",
        "component_type": "loader",
        "animation_type": "bounce",
        "duration": 45,
    },
    "card_slide": {
        "description": "卡片滑入动画",
        "component_type": "card",
        "animation_type": "slide",
        "duration": 30,
    },
    "card_hover": {
        "description": "卡片悬停动画",
        "component_type": "card",
        "animation_type": "pulse",
        "duration": 60,
    },
    "icon_bounce": {
        "description": "图标弹跳动画",
        "component_type": "icon",
        "animation_type": "bounce",
        "duration": 45,
    },
    "icon_rotate": {
        "description": "图标旋转动画",
        "component_type": "icon",
        "animation_type": "rotate",
        "duration": 60,
    },
    "chart_bar": {
        "description": "柱状图动画",
        "component_type": "chart",
        "animation_type": "fill",
        "duration": 90,
    },
    "counter_count": {
        "description": "数字计数动画",
        "component_type": "counter",
        "animation_type": "count",
        "duration": 60,
    },
    "notification_slide": {
        "description": "通知滑入动画",
        "component_type": "card",
        "animation_type": "slide",
        "duration": 30,
    },
}


class UIAnimator:
    """Remotion UI动画组件生成器"""

    def __init__(self):
        self.presets = UI_ANIMATION_PRESETS

    def generate_button_component(
        self,
        config: UIAnimationConfig,
        output_path: str,
        component_name: str = "AnimatedButton",
        button_text: str = "Click Me",
    ) -> str:
        """生成按钮动画组件"""
        if config.animation_type == "pulse":
            anim_logic = f"""
  const scale = interpolate(frame, [0, 30, 60], [1, 1.05, 1], {{
    extrapolateRight: 'extend',
    extrapolateLeft: 'extend',
  }});
  const boxShadow = `0 0 ${{interpolate(frame, [0, 30, 60], [10, 30, 10])}}px {config.color}`;
"""
        else:  # bounce
            anim_logic = f"""
  const scale = interpolate(frame, [0, 15, 30, 45], [1, 1.1, 0.95, 1], {{
    extrapolateRight: 'extend',
    extrapolateLeft: 'extend',
  }});
  const boxShadow = '0 4px 15px rgba(0,0,0,0.2)';
"""

        component_code = f"""import React from 'react';
import {{ AbsoluteFill, interpolate, useCurrentFrame }} from 'remotion';

// UI组件: 动画按钮 ({config.animation_type})

export const {component_name}: React.FC = () => {{
  const frame = useCurrentFrame();
{anim_logic}
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
      <button style={{
        padding: '16px 32px',
        fontSize: 18,
        fontWeight: 'bold',
        color: '{config.secondary_color}',
        backgroundColor: '{config.color}',
        border: 'none',
        borderRadius: 12,
        cursor: 'pointer',
        transform: `scale(${{scale}})`,
        boxShadow,
        transition: 'all 0.2s',
      }}>
        {button_text}
      </button>
    </AbsoluteFill>
  );
}};
"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(component_code)
        return output_path

    def generate_progress_component(
        self,
        config: UIAnimationConfig,
        output_path: str,
        component_name: str = "AnimatedProgress",
        progress_target: float = 0.75,
    ) -> str:
        """生成进度条动画组件"""
        component_code = f"""import React from 'react';
import {{ AbsoluteFill, interpolate, useCurrentFrame }} from 'remotion';

// UI组件: 进度条动画

export const {component_name}: React.FC = () => {{
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, {config.duration}], [0, {progress_target}], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
      <div style={{
        width: 400,
        height: 24,
        backgroundColor: '#E0E0E0',
        borderRadius: 12,
        overflow: 'hidden',
      }}>
        <div style={{
          width: `${{progress * 100}}%`,
          height: '100%',
          backgroundColor: '{config.color}',
          borderRadius: 12,
          transition: 'width 0.1s linear',
        }} />
      </div>
      <div style={{
        position: 'absolute',
        marginTop: 50,
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333',
      }}>
        {{Math.round(progress * 100)}}%
      </div>
    </AbsoluteFill>
  );
}};
"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(component_code)
        return output_path

    def generate_loader_component(
        self,
        config: UIAnimationConfig,
        output_path: str,
        component_name: str = "AnimatedLoader",
    ) -> str:
        """生成加载动画组件"""
        if config.animation_type == "rotate":
            component_code = f"""import React from 'react';
import {{ AbsoluteFill, interpolate, useCurrentFrame }} from 'remotion';

// UI组件: 加载旋转动画

export const {component_name}: React.FC = () => {{
  const frame = useCurrentFrame();
  const rotation = (frame / {config.duration}) * 360;

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
      <div style={{
        width: {config.size},
        height: {config.size},
        border: `6px solid #E0E0E0`,
        borderTop: `6px solid {config.color}`,
        borderRadius: '50%',
        animation: `spin {config.duration / 30}s linear infinite`,
        transform: `rotate(${{rotation}}deg)`,
      }} />
    </AbsoluteFill>
  );
}};
"""
        else:  # dots
            component_code = f"""import React from 'react';
import {{ AbsoluteFill, interpolate, useCurrentFrame }} from 'remotion';

// UI组件: 加载点动画

export const {component_name}: React.FC = () => {{
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', flexDirection: 'row', gap: 12 }}>
      {{[0, 1, 2].map((i) => {{
        const delay = i * 10;
        const scale = interpolate(frame, [delay, delay + 15, delay + 30], [1, 1.5, 1], {{
          extrapolateRight: 'extend',
          extrapolateLeft: 'clamp',
        }});
        return (
          <div key={{i}} style={{
            width: 20,
            height: 20,
            borderRadius: '50%',
            backgroundColor: '{config.color}',
            transform: `scale(${{scale}})`,
          }} />
        );
      }})}}
    </AbsoluteFill>
  );
}};
"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(component_code)
        return output_path

    def generate_card_component(
        self,
        config: UIAnimationConfig,
        output_path: str,
        component_name: str = "AnimatedCard",
        title: str = "Card Title",
        content: str = "Card content goes here",
    ) -> str:
        """生成卡片动画组件"""
        if config.animation_type == "slide":
            anim_logic = f"""
  const translateX = interpolate(frame, [0, {config.duration}], [-500, 0], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});
  const opacity = interpolate(frame, [0, {config.duration}], [0, 1], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }});
  const transform = `translateX(${{translateX}}px)`;
"""
        else:  # pulse/hover
            anim_logic = f"""
  const scale = interpolate(frame, [0, 30, 60], [1, 1.02, 1], {{
    extrapolateRight: 'extend',
    extrapolateLeft: 'extend',
  }});
  const opacity = 1;
  const transform = `scale(${{scale}})`;
"""

        component_code = f"""import React from 'react';
import {{ AbsoluteFill, interpolate, useCurrentFrame }} from 'remotion';

// UI组件: 卡片动画 ({config.animation_type})

export const {component_name}: React.FC = () => {{
  const frame = useCurrentFrame();
{anim_logic}
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
      <div style={{
        width: 320,
        padding: 24,
        backgroundColor: '#FFFFFF',
        borderRadius: 16,
        boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
        opacity,
        transform,
      }}>
        <h2 style={{ margin: 0, marginBottom: 12, color: '#333' }}>{title}</h2>
        <p style={{ margin: 0, color: '#666', lineHeight: 1.6 }}>{content}</p>
      </div>
    </AbsoluteFill>
  );
}};
"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(component_code)
        return output_path

    def generate_counter_component(
        self,
        config: UIAnimationConfig,
        output_path: str,
        component_name: str = "AnimatedCounter",
        target_value: int = 1000,
        prefix: str = "",
        suffix: str = "",
    ) -> str:
        """生成数字计数动画组件"""
        component_code = f"""import React from 'react';
import {{ AbsoluteFill, interpolate, useCurrentFrame }} from 'remotion';

// UI组件: 数字计数动画

export const {component_name}: React.FC = () => {{
  const frame = useCurrentFrame();
  const value = Math.floor(interpolate(frame, [0, {config.duration}], [0, {target_value}], {{
    extrapolateRight: 'clamp',
    extrapolateLeft: 'clamp',
  }}));

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
      <div style={{
        fontSize: 72,
        fontWeight: 'bold',
        color: '{config.color}',
        fontFamily: 'monospace',
      }}>
        {prefix}{{value.toLocaleString()}}{suffix}
      </div>
    </AbsoluteFill>
  );
}};
"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(component_code)
        return output_path

    def generate_chart_component(
        self,
        config: UIAnimationConfig,
        output_path: str,
        component_name: str = "AnimatedChart",
        data: List[float] = None,
    ) -> str:
        """生成柱状图动画组件"""
        data = data or [30, 60, 45, 80, 55, 90, 70]
        max_val = max(data) if data else 100

        bars_code = ""
        for i, val in enumerate(data):
            delay = i * 10
            height_pct = (val / max_val) * 100
            bars_code += f"""
        <div key={{ {i} }} style={{
          width: 40,
          height: `${{interpolate(frame, [{delay}, {delay + 30}], [0, {height_pct}], {{extrapolateRight: 'clamp', extrapolateLeft: 'clamp'}})}}%`,
          backgroundColor: '{config.color}',
          borderRadius: '4px 4px 0 0',
          transition: 'height 0.1s linear',
        }} />
"""

        component_code = f"""import React from 'react';
import {{ AbsoluteFill, interpolate, useCurrentFrame }} from 'remotion';

// UI组件: 柱状图动画

export const {component_name}: React.FC = () => {{
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
      <div style={{
        display: 'flex',
        alignItems: 'flex-end',
        gap: 16,
        height: 200,
        padding: 20,
        backgroundColor: '#F5F5F5',
        borderRadius: 12,
      }}>
{bars_code}
      </div>
    </AbsoluteFill>
  );
}};
"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(component_code)
        return output_path

    def list_presets(self) -> List[str]:
        """列出所有UI动画预设"""
        return list(self.presets.keys())


def main():
    """测试UI动画组件生成器"""
    animator = UIAnimator()

    print(f"可用UI动画 ({len(animator.list_presets())}种):")
    for name in animator.list_presets():
        print(f"  - {name}: {animator.presets[name]['description']}")

    # 生成按钮
    config = UIAnimationConfig(component_type="button", animation_type="pulse", color="#4A90D9")
    output = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\remotion\AnimatedButton.tsx"
    path = animator.generate_button_component(config, output, "AnimatedButton", "Subscribe")
    print(f"\n生成按钮: {path}")

    # 生成进度条
    config2 = UIAnimationConfig(component_type="progress", animation_type="fill", color="#4CAF50", duration=120)
    output2 = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\remotion\AnimatedProgress.tsx"
    path2 = animator.generate_progress_component(config2, output2, "AnimatedProgress", 0.85)
    print(f"生成进度条: {path2}")

    # 生成计数器
    config3 = UIAnimationConfig(component_type="counter", animation_type="count", color="#FF6B6B", duration=90)
    output3 = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\remotion\AnimatedCounter.tsx"
    path3 = animator.generate_counter_component(config3, output3, "AnimatedCounter", 10000, "+", "")
    print(f"生成计数器: {path3}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
