"""
Remotion运动预设库
- 缓动曲线预设
- 运动路径预设
- 弹簧物理动画
- 循环动画
- 关键帧序列生成
"""

import os
import sys
import logging
from typing import Optional, List, Dict, Any, Tuple, Callable
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class MotionConfig:
    """运动配置"""
    motion_type: str = "ease_in_out"  # 缓动类型
    duration: int = 60
    start_value: float = 0.0
    end_value: float = 1.0
    property_name: str = "opacity"  # opacity/scale/translateX/translateY/rotation


# 缓动函数预设
EASING_PRESETS = {
    "linear": {"description": "线性", "formula": "t"},
    "ease_in": {"description": "缓入", "formula": "t*t"},
    "ease_out": {"description": "缓出", "formula": "t*(2-t)"},
    "ease_in_out": {"description": "缓入缓出", "formula": "t<0.5 ? 2*t*t : -1+(4-2*t)*t"},
    "ease_in_quad": {"description": "二次缓入", "formula": "t*t"},
    "ease_out_quad": {"description": "二次缓出", "formula": "t*(2-t)"},
    "ease_in_cubic": {"description": "三次缓入", "formula": "t*t*t"},
    "ease_out_cubic": {"description": "三次缓出", "formula": "(t-1)*(t-1)*(t-1)+1"},
    "ease_in_back": {"description": "回退缓入", "formula": "t*t*((1.70158+1)*t-1.70158)"},
    "ease_out_back": {"description": "回退缓出", "formula": "(t-1)*(t-1)*((1.70158+1)*(t-1)+1.70158)+1"},
    "ease_in_out_back": {"description": "回退缓入缓出", "formula": "t<0.5 ? (t*2)*(t*2)*((2.5949+1)*t*2-2.5949)/2 : ((t*2-2)*(t*2-2)*((2.5949+1)*(t*2-2)+2.5949)+2)/2"},
    "ease_out_bounce": {"description": "弹跳缓出", "formula": "bounce(t)"},
    "ease_out_elastic": {"description": "弹性缓出", "formula": "elastic(t)"},
    "ease_in_expo": {"description": "指数缓入", "formula": "t===0 ? 0 : Math.pow(2, 10*(t-1))"},
    "ease_out_expo": {"description": "指数缓出", "formula": "t===1 ? 1 : 1-Math.pow(2, -10*t)"},
}

# 运动路径预设
MOTION_PATH_PRESETS = {
    "straight": {
        "description": "直线运动",
        "points": [(0, 0), (1, 1)],
    },
    "arc_up": {
        "description": "上抛弧线",
        "points": [(0, 0), (0.5, 1), (1, 0)],
    },
    "arc_down": {
        "description": "下落弧线",
        "points": [(0, 1), (0.5, 0), (1, 1)],
    },
    "sine_wave": {
        "description": "正弦波",
        "points": [(0, 0.5), (0.25, 1), (0.5, 0.5), (0.75, 0), (1, 0.5)],
    },
    "circle": {
        "description": "圆周运动",
        "points": [(0.5, 0), (1, 0.5), (0.5, 1), (0, 0.5), (0.5, 0)],
    },
    "figure_8": {
        "description": "8字形",
        "points": [(0.5, 0.5), (0.75, 0), (1, 0.5), (0.75, 1), (0.5, 0.5), (0.25, 0), (0, 0.5), (0.25, 1), (0.5, 0.5)],
    },
    "spiral_in": {
        "description": "螺旋进入",
        "points": [(1, 0.5), (0.75, 0.75), (0.5, 1), (0.25, 0.75), (0.5, 0.5)],
    },
    "bounce_path": {
        "description": "弹跳路径",
        "points": [(0, 1), (0.2, 0), (0.4, 0.5), (0.6, 0), (0.8, 0.3), (1, 0)],
    },
}

# 弹簧物理配置
SPRING_CONFIGS = {
    "gentle": {"description": "轻柔弹簧", "stiffness": 100, "damping": 15, "mass": 1},
    "bouncy": {"description": "弹性弹簧", "stiffness": 200, "damping": 10, "mass": 1},
    "snappy": {"description": "快速弹簧", "stiffness": 300, "damping": 20, "mass": 1},
    "heavy": {"description": "沉重弹簧", "stiffness": 80, "damping": 25, "mass": 2},
    "wobbly": {"description": "摇晃弹簧", "stiffness": 150, "damping": 5, "mass": 1},
}


class MotionPresets:
    """Remotion运动预设库"""

    def __init__(self):
        self.easings = EASING_PRESETS
        self.paths = MOTION_PATH_PRESETS
        self.springs = SPRING_CONFIGS

    def generate_easing_component(
        self,
        easing_type: str = "ease_in_out",
        output_path: str = "",
        component_name: str = "EasingAnimation",
        property_name: str = "opacity",
        duration: int = 60,
    ) -> str:
        """生成缓动动画组件

        Args:
            easing_type: 缓动类型
            output_path: 输出路径
            component_name: 组件名
            property_name: 属性名
            duration: 时长

        Returns:
            生成的文件路径
        """
        easing = self.easings.get(easing_type, self.easings["ease_in_out"])
        formula = easing["formula"]

        # 特殊缓动函数需要辅助函数
        helper_functions = ""
        if "bounce" in formula:
            helper_functions = """
  const bounce = (t: number) => {
    const n1 = 7.5625;
    const d1 = 2.75;
    if (t < 1 / d1) return n1 * t * t;
    if (t < 2 / d1) return n1 * (t -= 1.5 / d1) * t + 0.75;
    if (t < 2.5 / d1) return n1 * (t -= 2.25 / d1) * t + 0.9375;
    return n1 * (t -= 2.625 / d1) * t + 0.984375;
  };
"""
        elif "elastic" in formula:
            helper_functions = """
  const elastic = (t: number) => {
    const c4 = (2 * Math.PI) / 3;
    return t === 0 ? 0 : t === 1 ? 1 : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1;
  };
"""

        component_code = f"""import React from 'react';
import {{ AbsoluteFill, interpolate, useCurrentFrame }} from 'remotion';

// 缓动动画: {easing_type} ({easing['description']})
// 属性: {property_name}
// 时长: {duration}帧

export const {component_name}: React.FC<{{children: React.ReactNode}}> = ({{children}}) => {{
  const frame = useCurrentFrame();
{helper_functions}
  const t = Math.min(frame / {duration}, 1);
  const eased = {formula};
  const value = interpolate(eased, [0, 1], [0, 1]);

  return (
    <AbsoluteFill style={{
      {property_name}: value,
      justifyContent: 'center',
      alignItems: 'center',
    }}>
      {{children}}
    </AbsoluteFill>
  );
}};
"""
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(component_code)
            logger.info(f"缓动组件已生成: {output_path}")
        return component_code

    def generate_spring_component(
        self,
        spring_type: str = "gentle",
        output_path: str = "",
        component_name: str = "SpringAnimation",
        property_name: str = "scale",
        from_value: float = 0.5,
        to_value: float = 1.0,
    ) -> str:
        """生成弹簧物理动画组件

        Args:
            spring_type: 弹簧类型
            output_path: 输出路径
            component_name: 组件名
            property_name: 属性名
            from_value: 起始值
            to_value: 目标值

        Returns:
            生成的文件路径
        """
        spring = self.springs.get(spring_type, self.springs["gentle"])

        component_code = f"""import React from 'react';
import {{ AbsoluteFill, useCurrentFrame, useVideoConfig }} from 'remotion';

// 弹簧动画: {spring_type} ({spring['description']})
// 刚度: {spring['stiffness']}, 阻尼: {spring['damping']}, 质量: {spring['mass']}

export const {component_name}: React.FC<{{children: React.ReactNode}}> = ({{children}}) => {{
  const frame = useCurrentFrame();
  const {{ fps }} = useVideoConfig();

  // 弹簧物理模拟
  const stiffness = {spring['stiffness']};
  const damping = {spring['damping']};
  const mass = {spring['mass']};

  const omega = Math.sqrt(stiffness / mass);
  const zeta = damping / (2 * Math.sqrt(stiffness * mass));
  const t = frame / fps;

  let value: number;
  if (zeta < 1) {{
    // 欠阻尼
    const omega_d = omega * Math.sqrt(1 - zeta * zeta);
    value = 1 - Math.exp(-zeta * omega * t) * (Math.cos(omega_d * t) + (zeta * omega / omega_d) * Math.sin(omega_d * t));
  }} else if (zeta === 1) {{
    // 临界阻尼
    value = 1 - (1 + omega * t) * Math.exp(-omega * t);
  }} else {{
    // 过阻尼
    const omega_d = omega * Math.sqrt(zeta * zeta - 1);
    value = 1 - Math.exp(-zeta * omega * t) * (Math.cosh(omega_d * t) + (zeta * omega / omega_d) * Math.sinh(omega_d * t));
  }}

  const animatedValue = {from_value} + ({to_value} - {from_value}) * value;

  return (
    <AbsoluteFill style={{
      {property_name}: animatedValue,
      justifyContent: 'center',
      alignItems: 'center',
    }}>
      {{children}}
    </AbsoluteFill>
  );
}};
"""
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(component_code)
            logger.info(f"弹簧组件已生成: {output_path}")
        return component_code

    def generate_path_animation(
        self,
        path_type: str = "sine_wave",
        output_path: str = "",
        component_name: str = "PathAnimation",
        duration: int = 120,
        scale_x: float = 500,
        scale_y: float = 300,
    ) -> str:
        """生成路径动画组件

        Args:
            path_type: 路径类型
            output_path: 输出路径
            component_name: 组件名
            duration: 时长
            scale_x: X轴缩放
            scale_y: Y轴缩放

        Returns:
            生成的文件路径
        """
        path = self.paths.get(path_type, self.paths["sine_wave"])
        points = path["points"]

        # 生成路径点
        points_code = "["
        for i, (x, y) in enumerate(points):
            points_code += f"[{x}, {y}]"
            if i < len(points) - 1:
                points_code += ", "
        points_code += "]"

        component_code = f"""import React from 'react';
import {{ AbsoluteFill, interpolate, useCurrentFrame }} from 'remotion';

// 路径动画: {path_type} ({path['description']})
// 时长: {duration}帧

const PATH_POINTS = {points_code};

export const {component_name}: React.FC<{{children: React.ReactNode}}> = ({{children}}) => {{
  const frame = useCurrentFrame();
  const progress = Math.min(frame / {duration}, 1);

  // 沿路径插值
  const totalSegments = PATH_POINTS.length - 1;
  const segmentProgress = progress * totalSegments;
  const segmentIndex = Math.min(Math.floor(segmentProgress), totalSegments - 1);
  const segmentT = segmentProgress - segmentIndex;

  const [x1, y1] = PATH_POINTS[segmentIndex];
  const [x2, y2] = PATH_POINTS[Math.min(segmentIndex + 1, PATH_POINTS.length - 1)];

  const x = interpolate(segmentT, [0, 1], [x1, x2]) * {scale_x};
  const y = interpolate(segmentT, [0, 1], [y1, y2]) * {scale_y};

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
      <div style={{
        transform: `translate(${{x - {scale_x / 2}}}px, ${{y - {scale_y / 2}}}px)`,
      }}>
        {{children}}
      </div>
    </AbsoluteFill>
  );
}};
"""
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(component_code)
            logger.info(f"路径动画组件已生成: {output_path}")
        return component_code

    def list_easings(self) -> List[str]:
        """列出所有缓动预设"""
        return list(self.easings.keys())

    def list_paths(self) -> List[str]:
        """列出所有路径预设"""
        return list(self.paths.keys())

    def list_springs(self) -> List[str]:
        """列出所有弹簧配置"""
        return list(self.springs.keys())


def main():
    """测试运动预设库"""
    presets = MotionPresets()

    print(f"可用缓动 ({len(presets.list_easings())}种):")
    for name in presets.list_easings():
        print(f"  - {name}: {presets.easings[name]['description']}")

    print(f"\n可用路径 ({len(presets.list_paths())}种):")
    for name in presets.list_paths():
        print(f"  - {name}: {presets.paths[name]['description']}")

    print(f"\n可用弹簧 ({len(presets.list_springs())}种):")
    for name in presets.list_springs():
        print(f"  - {name}: {presets.springs[name]['description']}")

    # 生成弹簧动画
    output = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\remotion\SpringAnimation.tsx"
    path = presets.generate_spring_component("bouncy", output, "BouncySpring", "scale", 0.3, 1.0)
    print(f"\n生成弹簧动画: {output}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
