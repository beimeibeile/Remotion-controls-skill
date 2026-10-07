"""示例2: 使用内置模板渲染动画"""
import os, sys
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SKILL_ROOT not in sys.path:
    sys.path.insert(0, SKILL_ROOT)
from capabilities.cap_template_library.library import TemplateLibrary

def main():
    lib = TemplateLibrary()
    print("可用分类:", lib.list_categories())
    print()
    for t in lib.list_templates():
        print(f"  [{t['category']}] {t['id']}: {t['name']} - {t['description']}")
    print()
    # 实例化模板
    config = lib.instantiate_template("character_fall", {"character_image": "doubao.png"})
    print(f"character_fall 实例化: {len(config.get('layers', []))}图层")

if __name__ == "__main__":
    main()
