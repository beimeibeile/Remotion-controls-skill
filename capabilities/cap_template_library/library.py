"""
cap_template_library - 动画模板库
预设动画模板（角色动画、UI动画、文字动画、转场特效）
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional


class TemplateLibrary:
    """动画模板库"""

    def __init__(self, templates_dir: Optional[str] = None):
        if templates_dir is None:
            self.templates_dir = Path(__file__).parent.parent.parent / "templates"
        else:
            self.templates_dir = Path(templates_dir)
        self._cache: Dict[str, Dict[str, Any]] = {}

    def list_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出所有模板"""
        templates = []
        if not self.templates_dir.exists():
            return templates

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
                        "file": str(f),
                    })
            except Exception:
                continue
        return templates

    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """获取模板配置"""
        if template_id in self._cache:
            return self._cache[template_id]

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

    def render_template(
        self,
        template_id: str,
        output_path: str,
        *,
        variables: Optional[Dict[str, Any]] = None,
        transparent: bool = True,
    ) -> Dict[str, Any]:
        """渲染模板（需要配合 RemotionAPI）"""
        template = self.get_template(template_id)
        if template is None:
            return {"success": False, "error": f"模板不存在: {template_id}"}

        config = dict(template.get("config", {}))
        if variables:
            config["variables"] = variables

        # 这里需要外部传入 RemotionAPI 实例来渲染
        # 模板库只负责提供配置，渲染由 AnimationRenderer 负责
        return {
            "success": True,
            "template_id": template_id,
            "config": config,
            "note": "请使用 AnimationRenderer.render_from_config() 渲染",
        }
