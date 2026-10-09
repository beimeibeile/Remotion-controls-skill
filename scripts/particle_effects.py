"""
Remotion粒子特效系统
- 粒子爆炸
- 粒子雨
- 粒子飘雪
- 粒子星空
- 粒子火焰
- 粒子组件代码生成
"""

import os
import sys
import logging
import random
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ParticleConfig:
    """粒子配置"""
    particle_type: str = "explosion"  # explosion/rain/snow/stars/fire/confetti
    count: int = 50
    duration: int = 120
    colors: List[str] = field(default_factory=lambda: ["#FF6B6B", "#4ECDC4", "#FFD93D", "#6BCB77"])
    size_range: Tuple[float, float] = (2, 8)
    speed_range: Tuple[float, float] = (1, 5)
    gravity: float = 0.1
    opacity: float = 1.0


# 粒子预设
PARTICLE_PRESETS = {
    "explosion": {
        "description": "粒子爆炸",
        "count": 100,
        "duration": 60,
        "colors": ["#FF6B6B", "#FFD93D", "#FF8C42", "#FFFFFF"],
        "size_range": (3, 10),
        "speed_range": (3, 10),
        "gravity": 0.15,
    },
    "rain": {
        "description": "粒子雨",
        "count": 80,
        "duration": 120,
        "colors": ["#4A90D9", "#6BB3F0", "#87CEEB"],
        "size_range": (1, 3),
        "speed_range": (8, 15),
        "gravity": 0.5,
    },
    "snow": {
        "description": "粒子飘雪",
        "count": 60,
        "duration": 180,
        "colors": ["#FFFFFF", "#F0F8FF", "#E6F3FF"],
        "size_range": (2, 6),
        "speed_range": (1, 3),
        "gravity": 0.05,
    },
    "stars": {
        "description": "粒子星空",
        "count": 100,
        "duration": 120,
        "colors": ["#FFFFFF", "#FFD700", "#87CEEB", "#FFB6C1"],
        "size_range": (1, 4),
        "speed_range": (0.1, 0.5),
        "gravity": 0,
    },
    "fire": {
        "description": "粒子火焰",
        "count": 70,
        "duration": 60,
        "colors": ["#FF4500", "#FF6347", "#FFD700", "#FF8C00"],
        "size_range": (5, 15),
        "speed_range": (2, 6),
        "gravity": -0.1,
    },
    "confetti": {
        "description": "五彩纸屑",
        "count": 120,
        "duration": 120,
        "colors": ["#FF6B6B", "#4ECDC4", "#FFD93D", "#6BCB77", "#9B59B6", "#3498DB"],
        "size_range": (4, 10),
        "speed_range": (2, 8),
        "gravity": 0.2,
    },
    "sparkles": {
        "description": "闪光粒子",
        "count": 40,
        "duration": 90,
        "colors": ["#FFD700", "#FFFFFF", "#FFEC8B"],
        "size_range": (2, 6),
        "speed_range": (0.5, 2),
        "gravity": 0,
    },
    "bubbles": {
        "description": "气泡粒子",
        "count": 50,
        "duration": 120,
        "colors": ["#87CEEB", "#ADD8E6", "#B0E0E6"],
        "size_range": (5, 20),
        "speed_range": (1, 3),
        "gravity": -0.05,
    },
}


class ParticleEffects:
    """Remotion粒子特效系统"""

    def __init__(self):
        self.presets = PARTICLE_PRESETS

    def _generate_particle_data(self, config: ParticleConfig) -> List[Dict[str, Any]]:
        """生成粒子初始数据"""
        particles = []
        for i in range(config.count):
            angle = random.uniform(0, 2 * 3.14159)
            speed = random.uniform(*config.speed_range)
            size = random.uniform(*config.size_range)
            color = random.choice(config.colors)

            if config.particle_type == "explosion":
                start_x = 0
                start_y = 0
                vx = speed * 0.1 * random.choice([-1, 1])
                vy = speed * 0.1 * random.choice([-1, 1])
            elif config.particle_type == "rain":
                start_x = random.uniform(-960, 960)
                start_y = random.uniform(-1080, 0)
                vx = 0
                vy = speed
            elif config.particle_type == "snow":
                start_x = random.uniform(-960, 960)
                start_y = random.uniform(-1080, 0)
                vx = random.uniform(-0.5, 0.5)
                vy = speed
            elif config.particle_type == "stars":
                start_x = random.uniform(-960, 960)
                start_y = random.uniform(-540, 540)
                vx = 0
                vy = 0
            elif config.particle_type == "fire":
                start_x = random.uniform(-50, 50)
                start_y = 200
                vx = random.uniform(-1, 1)
                vy = -speed
            elif config.particle_type == "confetti":
                start_x = random.uniform(-960, 960)
                start_y = random.uniform(-600, -400)
                vx = random.uniform(-2, 2)
                vy = speed
            elif config.particle_type == "bubbles":
                start_x = random.uniform(-400, 400)
                start_y = random.uniform(200, 400)
                vx = random.uniform(-0.5, 0.5)
                vy = -speed
            else:  # sparkles
                start_x = random.uniform(-300, 300)
                start_y = random.uniform(-200, 200)
                vx = 0
                vy = 0

            particles.append({
                "id": i,
                "startX": round(start_x, 2),
                "startY": round(start_y, 2),
                "vx": round(vx, 4),
                "vy": round(vy, 4),
                "size": round(size, 2),
                "color": color,
                "rotation": random.uniform(0, 360),
                "rotationSpeed": random.uniform(-5, 5),
            })
        return particles

    def generate_particle_component(
        self,
        config: ParticleConfig,
        output_path: str,
        component_name: str = "ParticleEffect",
    ) -> str:
        """生成粒子特效组件

        Args:
            config: 粒子配置
            output_path: 输出路径
            component_name: 组件名

        Returns:
            生成的文件路径
        """
        particles = self._generate_particle_data(config)

        # 生成粒子数据JSON
        particles_json = "[\n"
        for p in particles:
            particles_json += f"  {{id: {p['id']}, startX: {p['startX']}, startY: {p['startY']}, vx: {p['vx']}, vy: {p['vy']}, size: {p['size']}, color: '{p['color']}', rotation: {p['rotation']}, rotationSpeed: {p['rotationSpeed']}}},\n"
        particles_json += "]"

        # 根据粒子类型确定形状
        if config.particle_type in ["rain", "snow", "stars", "sparkles"]:
            shape = "borderRadius: '50%'"
        elif config.particle_type == "confetti":
            shape = "borderRadius: 2"
        elif config.particle_type == "bubbles":
            shape = "borderRadius: '50%', border: '2px solid rgba(255,255,255,0.5)', backgroundColor: 'rgba(135,206,235,0.3)'"
        else:
            shape = "borderRadius: '50%'"

        component_code = f"""import React from 'react';
import {{ AbsoluteFill, interpolate, useCurrentFrame }} from 'remotion';

// 粒子特效: {config.particle_type} ({self.presets.get(config.particle_type, {{}}).get('description', '自定义')})
// 粒子数量: {config.count}
// 时长: {config.duration}帧

const PARTICLES = {particles_json};

export const {component_name}: React.FC = () => {{
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{ backgroundColor: 'transparent', overflow: 'hidden' }}>
      {{PARTICLES.map((p) => {{
        const progress = frame / {config.duration};
        const x = p.startX + p.vx * frame;
        const y = p.startY + p.vy * frame + {config.gravity} * frame * frame * 0.5;
        const opacity = interpolate(frame, [0, {config.duration}], [{config.opacity}, 0], {{
          extrapolateRight: 'clamp',
          extrapolateLeft: 'clamp',
        }});
        const rotation = p.rotation + p.rotationSpeed * frame;
        const scale = interpolate(frame, [0, {config.duration // 2}, {config.duration}], [0, 1, 0.5], {{
          extrapolateRight: 'clamp',
          extrapolateLeft: 'clamp',
        }});

        return (
          <div
            key={{p.id}}
            style={{
              position: 'absolute',
              left: '50%',
              top: '50%',
              width: p.size,
              height: p.size,
              backgroundColor: p.color,
              {shape},
              transform: `translate(${{x}}px, ${{y}}px) rotate(${{rotation}}deg) scale(${{scale}})`,
              opacity,
              boxShadow: config.particle_type === 'fire' ? `0 0 ${{p.size * 2}}px ${{p.color}}` : 'none',
            }}
          />
        );
      }})}}
    </AbsoluteFill>
  );
}};
"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(component_code)

        logger.info(f"粒子特效组件已生成: {output_path} ({config.count}个粒子)")
        return output_path

    def list_presets(self) -> List[str]:
        """列出所有粒子预设"""
        return list(self.presets.keys())


def main():
    """测试粒子特效系统"""
    effects = ParticleEffects()

    print(f"可用粒子特效 ({len(effects.list_presets())}种):")
    for name in effects.list_presets():
        print(f"  - {name}: {effects.presets[name]['description']}")

    # 生成爆炸粒子
    config = ParticleConfig(
        particle_type="explosion",
        count=100,
        duration=60,
    )
    output = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\remotion\ExplosionParticles.tsx"
    path = effects.generate_particle_component(config, output, "ExplosionParticles")
    print(f"\n生成爆炸粒子: {path}")

    # 生成飘雪粒子
    config2 = ParticleConfig(
        particle_type="snow",
        count=60,
        duration=180,
    )
    output2 = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\remotion\SnowParticles.tsx"
    path2 = effects.generate_particle_component(config2, output2, "SnowParticles")
    print(f"生成飘雪粒子: {path2}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
