"""冒烟测试: remotion-controls-skill核心模块可导入、可初始化（不依赖Node/Remotion实际运行）"""
import os, sys, json
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SKILL_ROOT not in sys.path:
    sys.path.insert(0, SKILL_ROOT)

passed = 0; failed = 0
def check(name, func):
    global passed, failed
    try:
        func(); print(f"  PASS: {name}"); passed += 1
    except Exception as e:
        print(f"  FAIL: {name} -> {type(e).__name__}: {e}"); failed += 1

print("=== Module Imports ===")
check('remotion_controls', lambda: __import__('remotion_controls'))
check('cap_api_wrapper', lambda: __import__('capabilities.cap_api_wrapper.api', fromlist=['RemotionAPI']))
check('cap_animation_renderer', lambda: __import__('capabilities.cap_animation_renderer.renderer', fromlist=['AnimationRenderer', 'KeyframeBuilder', 'LayerBuilder']))
check('cap_template_library', lambda: __import__('capabilities.cap_template_library.library', fromlist=['TemplateLibrary', 'BUILTIN_TEMPLATES']))
check('cap_quality_control', lambda: __import__('capabilities.cap_quality_control.controller', fromlist=['QualityController']))

print()
print("=== KeyframeBuilder ===")
from capabilities.cap_animation_renderer.renderer import KeyframeBuilder
def test_kf():
    kb = KeyframeBuilder()
    kb.add_position(0, 0, 0).add_position(30, 100, 200, "ease_in")
    kb.add_scale(0, 1.0).add_scale(30, 2.0)
    kb.add_rotation(0, 0).add_rotation(30, 90)
    kb.add_opacity(0, 0.0).add_opacity(15, 1.0)
    cfg = kb.build()
    assert len(cfg["position"]) == 2
    assert len(cfg["scale"]) == 2
    assert len(cfg["rotation"]) == 2
    assert len(cfg["opacity"]) == 2
check('keyframe_builder', test_kf)

print()
print("=== LayerBuilder ===")
from capabilities.cap_animation_renderer.renderer import LayerBuilder
def test_layer():
    lb = LayerBuilder()
    lb.add_image_layer("test.png", x=100, y=200, z_index=1)
    lb.add_text_layer("Hello", font_size=48, z_index=2)
    lb.add_shape_layer("circle", size=50, z_index=0)
    layers = lb.build()
    assert len(layers) == 3
    assert layers[0]["z_index"] == 0  # 按z_index排序
check('layer_builder', test_layer)

print()
print("=== TemplateLibrary ===")
from capabilities.cap_template_library.library import TemplateLibrary, BUILTIN_TEMPLATES
def test_templates():
    lib = TemplateLibrary()
    cats = lib.list_categories()
    assert len(cats) >= 4  # character/ui/text/transition/effect
    t = lib.get_template("character_fall")
    assert t is not None
    assert "config" in t
    inst = lib.instantiate_template("character_fall", {"character_image": "/tmp/x.png"})
    assert inst is not None
    assert "/tmp/x.png" in json.dumps(inst)
check('template_library', test_templates)
check('builtin_count', lambda: len(BUILTIN_TEMPLATES) >= 5)

print()
print(f"=== 结果: {passed} passed, {failed} failed ===")
sys.exit(1 if failed > 0 else 0)
