"""示例1: 关键帧+多图层构建动画配置"""
import os, sys
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SKILL_ROOT not in sys.path:
    sys.path.insert(0, SKILL_ROOT)
from capabilities.cap_animation_renderer.renderer import KeyframeBuilder, LayerBuilder

def main():
    # 构建角色下落动画关键帧
    kb = KeyframeBuilder()
    kb.add_position(0, 540, -200, "ease_in")
    kb.add_position(60, 540, 960, "bounce")
    kb.add_rotation(0, 0, "ease_in")
    kb.add_rotation(60, 15, "ease_in")
    keyframes = kb.build()

    # 构建多图层
    lb = LayerBuilder()
    lb.add_image_layer("character.png", keyframes=keyframes, z_index=1)
    lb.add_text_layer("被打了！", x=540, y=300, font_size=64, color="#ff0000", z_index=2)
    layers = lb.build()

    config = {
        "composition": "AnimationTemplate",
        "fps": 30, "width": 1080, "height": 1920, "duration": 3,
        "layers": layers,
    }
    print(f"动画配置: {len(layers)}图层, {len(keyframes['position'])}位置关键帧")

if __name__ == "__main__":
    main()
