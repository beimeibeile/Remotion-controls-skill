"""
cap_template_library - 动画模板库 v2.0
预设动画模板（角色动画、UI动画、文字动画、转场特效）+ 内置预设 + 注册机制
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional


# 内置预设模板（不依赖外部JSON文件）
BUILTIN_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "character_fall": {
        "id": "character_fall",
        "name": "角色下落",
        "category": "character",
        "description": "角色从上方下落，带旋转和弹性着地",
        "config": {
            "composition": "AnimationTemplate",
            "fps": 30, "width": 1080, "height": 1920, "duration": 3,
            "layers": [
                {
                    "type": "image", "src": "{character_image}",
                    "keyframes": {
                        "position": [
                            {"frame": 0, "x": 540, "y": -200, "easing": "easeIn"},
                            {"frame": 60, "x": 540, "y": 960, "easing": "bounce"},
                        ],
                        "rotation": [
                            {"frame": 0, "degrees": 0},
                            {"frame": 60, "degrees": 15},
                        ],
                        "scale": [
                            {"frame": 0, "x": 1.0, "y": 1.0},
                            {"frame": 55, "x": 1.1, "y": 0.9},
                            {"frame": 60, "x": 1.0, "y": 1.0},
                        ],
                    },
                },
            ],
        },
        "variables": {"character_image": "角色图片路径"},
    },
    "character_hit": {
        "id": "character_hit",
        "name": "角色受击",
        "category": "character",
        "description": "角色受击震动+闪白+后退",
        "config": {
            "composition": "AnimationTemplate",
            "fps": 30, "width": 1080, "height": 1920, "duration": 1,
            "layers": [
                {"type": "image", "src": "{character_image}",
                 "keyframes": {
                     "position": [
                         {"frame": 0, "x": 540, "y": 960},
                         {"frame": 5, "x": 520, "y": 960},
                         {"frame": 10, "x": 560, "y": 960},
                         {"frame": 15, "x": 540, "y": 960},
                     ],
                     "opacity": [
                         {"frame": 0, "alpha": 1.0},
                         {"frame": 3, "alpha": 0.3},
                         {"frame": 6, "alpha": 1.0},
                     ],
                 }},
            ],
        },
        "variables": {"character_image": "角色图片路径"},
    },
    "ui_button_click": {
        "id": "ui_button_click",
        "name": "UI按钮点击",
        "category": "ui",
        "description": "按钮点击缩放反馈+波纹扩散",
        "config": {
            "composition": "AnimationTemplate",
            "fps": 30, "width": 1080, "height": 1920, "duration": 0.5,
            "layers": [
                {"type": "shape", "shape": "circle", "x": 540, "y": 960, "size": 100,
                 "keyframes": {"scale": [
                     {"frame": 0, "x": 1.0, "y": 1.0},
                     {"frame": 5, "x": 0.9, "y": 0.9},
                     {"frame": 15, "x": 1.0, "y": 1.0},
                 ]}},
            ],
        },
        "variables": {},
    },
    "text_typewriter": {
        "id": "text_typewriter",
        "name": "打字机文字",
        "category": "text",
        "description": "文字逐字显现（打字机效果）",
        "config": {
            "composition": "AnimationTemplate",
            "fps": 30, "width": 1080, "height": 1920, "duration": 2,
            "layers": [
                {"type": "text", "text": "{text}", "x": 540, "y": 960,
                 "font_size": 48, "color": "#ffffff",
                 "animation": {"type": "typewriter", "speed": 5}},
            ],
        },
        "variables": {"text": "显示的文字内容"},
    },
    "transition_fade": {
        "id": "transition_fade",
        "name": "淡入淡出转场",
        "category": "transition",
        "description": "画面淡入淡出转场",
        "config": {
            "composition": "AnimationTemplate",
            "fps": 30, "width": 1080, "height": 1920, "duration": 1,
            "layers": [
                {"type": "image", "src": "{from_image}",
                 "keyframes": {"opacity": [
                     {"frame": 0, "alpha": 1.0},
                     {"frame": 30, "alpha": 0.0},
                 ]}},
                {"type": "image", "src": "{to_image}",
                 "keyframes": {"opacity": [
                     {"frame": 0, "alpha": 0.0},
                     {"frame": 30, "alpha": 1.0},
                 ]}},
            ],
        },
        "variables": {"from_image": "起始画面", "to_image": "目标画面"},
    },
    "impact_punch": {
        "id": "impact_punch",
        "name": "拳击冲击",
        "category": "effect",
        "description": "拳击冲击波+星星+白闪",
        "config": {
            "composition": "AnimationTemplate",
            "fps": 30, "width": 1080, "height": 1920, "duration": 0.5,
            "layers": [
                {"type": "shape", "shape": "circle", "x": "{impact_x}", "y": "{impact_y}",
                 "size": 50, "color": "#ffffff",
                 "keyframes": {"scale": [
                     {"frame": 0, "x": 0.5, "y": 0.5},
                     {"frame": 15, "x": 3.0, "y": 3.0},
                 ], "opacity": [
                     {"frame": 0, "alpha": 1.0},
                     {"frame": 15, "alpha": 0.0},
                 ]}},
            ],
        },
        "variables": {"impact_x": "冲击点X", "impact_y": "冲击点Y"},
    },
}


class TemplateLibrary:
    """动画模板库 v2.0"""

    def __init__(self, templates_dir: Optional[str] = None):
        if templates_dir is None:
            self.templates_dir = Path(__file__).parent.parent.parent / "templates"
        else:
            self.templates_dir = Path(templates_dir)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._registry: Dict[str, Dict[str, Any]] = dict(BUILTIN_TEMPLATES)

    def register_template(self, template_id: str, template: Dict[str, Any]) -> bool:
        """注册自定义模板"""
        if "config" not in template:
            return False
        template["id"] = template_id
        self._registry[template_id] = template
        return True

    def list_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出所有模板（内置+外部）"""
        templates = []
        # 内置模板
        for tid, t in self._registry.items():
            if category is None or t.get("category") == category:
                templates.append({
                    "id": tid,
                    "name": t.get("name", tid),
                    "category": t.get("category", "general"),
                    "description": t.get("description", ""),
                    "source": "builtin",
                })
        # 外部JSON模板
        if self.templates_dir.exists():
            for f in self.templates_dir.glob("**/*.json"):
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        t = json.load(fp)
                    if category is None or t.get("category") == category:
                        templates.append({
                            "id": t.get("id", f.stem),
                            "name": t.get("name", f.stem),
                            "category": t.get("category", "general"),
                            "description": t.get("description", ""),
                            "source": "file",
                            "file": str(f),
                        })
                except Exception:
                    continue
        return templates

    def list_categories(self) -> List[str]:
        """列出所有模板分类"""
        cats = set(t.get("category", "general") for t in self._registry.values())
        if self.templates_dir.exists():
            for f in self.templates_dir.glob("**/*.json"):
                try:
                    with open(f, 'r', encoding='utf-8') as fp:
                        t = json.load(fp)
                    cats.add(t.get("category", "general"))
                except Exception:
                    continue
        return sorted(cats)

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """获取模板配置"""
        if template_id in self._cache:
            return self._cache[template_id]
        # 内置
        if template_id in self._registry:
            self._cache[template_id] = self._registry[template_id]
            return self._registry[template_id]
        # 外部文件
        if self.templates_dir.exists():
            for f in self.templates_dir.glob("**/*.json"):
                if f.stem == template_id:
                    try:
                        with open(f, 'r', encoding='utf-8') as fp:
                            t = json.load(fp)
                        self._cache[template_id] = t
                        return t
                    except Exception:
                        return None
        return None

    def instantiate_template(self, template_id: str,
                             variables: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """实例化模板（替换变量）"""
        template = self.get_template(template_id)
        if template is None:
            return None
        config = json.loads(json.dumps(template.get("config", {})))  # deep copy
        if variables:
            config_str = json.dumps(config)
            for key, value in variables.items():
                config_str = config_str.replace("{" + key + "}", str(value))
            config = json.loads(config_str)
        return config

    def get_template_variables(self, template_id: str) -> Dict[str, str]:
        """获取模板所需变量"""
        template = self.get_template(template_id)
        if template is None:
            return {}
        return template.get("variables", {})

    def render_template(
        self, template_id: str, output_path: str, *,
        variables: Optional[Dict[str, Any]] = None,
        transparent: bool = True,
    ) -> Dict[str, Any]:
        """渲染模板（返回配置，实际渲染由AnimationRenderer负责）"""
        config = self.instantiate_template(template_id, variables)
        if config is None:
            return {"success": False, "error": f"模板不存在: {template_id}"}
        return {
            "success": True,
            "template_id": template_id,
            "config": config,
            "note": "请使用 AnimationRenderer.render_from_config() 渲染",
        }
