"""
Remotion动画模板库
预设动画模板，支持快速生成常见动画效果
适用于剪映模板动画素材、UI动画、文字排版动画
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class AnimationTemplate:
    """动画模板定义"""
    template_id: str
    name: str
    category: str           # intro/outro/loop/transition/ui/text
    description: str
    duration: float         # 秒
    parameters: Dict[str, Any] = field(default_factory=dict)
    composition: str = "DefaultComp"
    transparent: bool = True


# ============ 预设动画模板库 ============
ANIMATION_TEMPLATES: Dict[str, AnimationTemplate] = {
    # ===== 入场动画 =====
    "fade_in": AnimationTemplate(
        template_id="fade_in",
        name="淡入",
        category="intro",
        description="元素从透明渐变为不透明",
        duration=0.5,
        parameters={"from_opacity": 0, "to_opacity": 1, "easing": "ease-out"},
    ),
    "slide_in_left": AnimationTemplate(
        template_id="slide_in_left",
        name="左滑入",
        category="intro",
        description="元素从左侧滑入画面",
        duration=0.6,
        parameters={"from_x": -100, "to_x": 0, "easing": "ease-out"},
    ),
    "slide_in_right": AnimationTemplate(
        template_id="slide_in_right",
        name="右滑入",
        category="intro",
        description="元素从右侧滑入画面",
        duration=0.6,
        parameters={"from_x": 100, "to_x": 0, "easing": "ease-out"},
    ),
    "slide_in_top": AnimationTemplate(
        template_id="slide_in_top",
        name="上滑入",
        category="intro",
        description="元素从上方滑入画面",
        duration=0.6,
        parameters={"from_y": -100, "to_y": 0, "easing": "ease-out"},
    ),
    "slide_in_bottom": AnimationTemplate(
        template_id="slide_in_bottom",
        name="下滑入",
        category="intro",
        description="元素从下方滑入画面",
        duration=0.6,
        parameters={"from_y": 100, "to_y": 0, "easing": "ease-out"},
    ),
    "zoom_in": AnimationTemplate(
        template_id="zoom_in",
        name="放大入场",
        category="intro",
        description="元素从小到大缩放入场",
        duration=0.5,
        parameters={"from_scale": 0, "to_scale": 1, "easing": "ease-out-back"},
    ),
    "bounce_in": AnimationTemplate(
        template_id="bounce_in",
        name="弹跳入",
        category="intro",
        description="元素弹跳入场",
        duration=0.8,
        parameters={"bounces": 3, "height": 50, "easing": "bounce"},
    ),
    "rotate_in": AnimationTemplate(
        template_id="rotate_in",
        name="旋转入场",
        category="intro",
        description="元素旋转入场",
        duration=0.6,
        parameters={"from_rotation": -180, "to_rotation": 0, "easing": "ease-out"},
    ),

    # ===== 出场动画 =====
    "fade_out": AnimationTemplate(
        template_id="fade_out",
        name="淡出",
        category="outro",
        description="元素从不透明渐变为透明",
        duration=0.5,
        parameters={"from_opacity": 1, "to_opacity": 0, "easing": "ease-in"},
    ),
    "slide_out_left": AnimationTemplate(
        template_id="slide_out_left",
        name="左滑出",
        category="outro",
        description="元素向左侧滑出画面",
        duration=0.6,
        parameters={"from_x": 0, "to_x": -100, "easing": "ease-in"},
    ),
    "slide_out_right": AnimationTemplate(
        template_id="slide_out_right",
        name="右滑出",
        category="outro",
        description="元素向右侧滑出画面",
        duration=0.6,
        parameters={"from_x": 0, "to_x": 100, "easing": "ease-in"},
    ),
    "zoom_out": AnimationTemplate(
        template_id="zoom_out",
        name="缩小出场",
        category="outro",
        description="元素从大到小缩放出场",
        duration=0.5,
        parameters={"from_scale": 1, "to_scale": 0, "easing": "ease-in"},
    ),

    # ===== 循环动画 =====
    "pulse": AnimationTemplate(
        template_id="pulse",
        name="脉冲",
        category="loop",
        description="元素周期性缩放脉冲",
        duration=2.0,
        parameters={"min_scale": 0.95, "max_scale": 1.05, "speed": 1.0},
    ),
    "float": AnimationTemplate(
        template_id="float",
        name="漂浮",
        category="loop",
        description="元素上下漂浮",
        duration=3.0,
        parameters={"amplitude": 20, "speed": 1.0},
    ),
    "shake": AnimationTemplate(
        template_id="shake",
        name="抖动",
        category="loop",
        description="元素左右抖动",
        duration=0.5,
        parameters={"amplitude": 10, "frequency": 20},
    ),
    "spin": AnimationTemplate(
        template_id="spin",
        name="旋转",
        category="loop",
        description="元素持续旋转",
        duration=4.0,
        parameters={"speed": 1.0, "direction": "cw"},
    ),
    "glow": AnimationTemplate(
        template_id="glow",
        name="发光",
        category="loop",
        description="元素发光强度周期性变化",
        duration=2.0,
        parameters={"min_glow": 0.3, "max_glow": 1.0, "color": "#00ffff"},
    ),

    # ===== 转场动画 =====
    "cross_fade": AnimationTemplate(
        template_id="cross_fade",
        name="交叉淡入淡出",
        category="transition",
        description="两个元素交叉淡入淡出",
        duration=0.8,
        parameters={"overlap": 0.5},
    ),
    "wipe_left": AnimationTemplate(
        template_id="wipe_left",
        name="向左擦除",
        category="transition",
        description="画面向左擦除转场",
        duration=0.6,
        parameters={"direction": "left"},
    ),
    "wipe_right": AnimationTemplate(
        template_id="wipe_right",
        name="向右擦除",
        category="transition",
        description="画面向右擦除转场",
        duration=0.6,
        parameters={"direction": "right"},
    ),
    "scale_transition": AnimationTemplate(
        template_id="scale_transition",
        name="缩放转场",
        category="transition",
        description="前一个缩小后一个放大",
        duration=0.7,
        parameters={"min_scale": 0.8},
    ),

    # ===== UI动画 =====
    "button_hover": AnimationTemplate(
        template_id="button_hover",
        name="按钮悬停",
        category="ui",
        description="按钮悬停放大效果",
        duration=0.3,
        parameters={"hover_scale": 1.05, "normal_scale": 1.0},
    ),
    "loading_spinner": AnimationTemplate(
        template_id="loading_spinner",
        name="加载旋转",
        category="ui",
        description="加载指示器旋转动画",
        duration=1.0,
        parameters={"speed": 1.0, "color": "#ffffff"},
    ),
    "progress_bar": AnimationTemplate(
        template_id="progress_bar",
        name="进度条",
        category="ui",
        description="进度条填充动画",
        duration=2.0,
        parameters={"from": 0, "to": 100, "color": "#00ff00"},
    ),

    # ===== 文字动画 =====
    "typewriter": AnimationTemplate(
        template_id="typewriter",
        name="打字机",
        category="text",
        description="文字逐字显示",
        duration=2.0,
        parameters={"speed": 0.05, "cursor": True},
    ),
    "text_fade_up": AnimationTemplate(
        template_id="text_fade_up",
        name="文字上浮淡入",
        category="text",
        description="文字逐行上浮淡入",
        duration=1.0,
        parameters={"delay_per_line": 0.1, "distance": 20},
    ),
    "text_gradient": AnimationTemplate(
        template_id="text_gradient",
        name="文字渐变",
        category="text",
        description="文字颜色渐变动画",
        duration=3.0,
        parameters={"colors": ["#ff0000", "#00ff00", "#0000ff"], "speed": 1.0},
    ),
}


class AnimationTemplateLibrary:
    """动画模板库管理器"""
    
    def __init__(self):
        self.templates = ANIMATION_TEMPLATES.copy()
        self.custom_templates: Dict[str, AnimationTemplate] = {}
    
    def list_templates(self, category: str = None) -> List[Dict[str, Any]]:
        """列出所有模板（可按类别筛选）"""
        result = []
        for tid, tpl in self.templates.items():
            if category and tpl.category != category:
                continue
            result.append({
                "id": tpl.template_id,
                "name": tpl.name,
                "category": tpl.category,
                "description": tpl.description,
                "duration": tpl.duration,
                "transparent": tpl.transparent,
            })
        return result
    
    def get_template(self, template_id: str) -> Optional[AnimationTemplate]:
        """获取模板"""
        return self.templates.get(template_id) or self.custom_templates.get(template_id)
    
    def get_categories(self) -> List[str]:
        """获取所有类别"""
        return list(set(t.category for t in self.templates.values()))
    
    def search_templates(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索模板"""
        keyword = keyword.lower()
        result = []
        for tid, tpl in self.templates.items():
            if (keyword in tpl.name.lower() or 
                keyword in tpl.description.lower() or 
                keyword in tpl.category.lower()):
                result.append({
                    "id": tpl.template_id,
                    "name": tpl.name,
                    "category": tpl.category,
                    "description": tpl.description,
                })
        return result
    
    def add_custom_template(self, template: AnimationTemplate) -> None:
        """添加自定义模板"""
        self.custom_templates[template.template_id] = template
        logger.info("添加自定义动画模板: %s", template.name)
    
    def generate_remotion_code(self, template_id: str, 
                                custom_params: Dict[str, Any] = None) -> str:
        """
        生成Remotion组件代码
        
        Args:
            template_id: 模板ID
            custom_params: 自定义参数覆盖
        
        Returns:
            TypeScript/React组件代码
        """
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"模板不存在: {template_id}")
        
        params = {**template.parameters, **(custom_params or {})}
        
        # 生成组件名（PascalCase）
        comp_name = ''.join(word.capitalize() for word in template_id.split('_'))
        
        # 生成基础组件代码
        code = f"""import React from 'react';
import {{ AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig }} from 'remotion';

// 动画模板: {template.name} ({template.template_id})
// 类别: {template.category}
// 描述: {template.description}
// 时长: {template.duration}秒

export const {comp_name}: React.FC = () => {{
  const frame = useCurrentFrame();
  const {{ fps }} = useVideoConfig();
  const progress = frame / ({template.duration} * fps);

  // 参数配置
  const params = {json.dumps(params, ensure_ascii=False, indent=4)};

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
      {{/* 动画内容 */}}
      <div style={{{{
        // 在这里应用动画效果
        opacity: 1,
        transform: 'scale(1)',
      }}}}>
        {{/* 替换为你的内容 */}}
      </div>
    </AbsoluteFill>
  );
}};
"""
        return code
    
    def get_template_summary(self) -> Dict[str, Any]:
        """获取模板库摘要"""
        categories = self.get_categories()
        summary = {
            "total_templates": len(self.templates),
            "custom_templates": len(self.custom_templates),
            "categories": {},
        }
        for cat in categories:
            cat_templates = [t for t in self.templates.values() if t.category == cat]
            summary["categories"][cat] = len(cat_templates)
        return summary


# ============ 便捷函数 ============
def list_all_templates(category: str = None) -> List[Dict[str, Any]]:
    """列出所有动画模板"""
    library = AnimationTemplateLibrary()
    return library.list_templates(category)


def get_animation_template(template_id: str) -> Optional[AnimationTemplate]:
    """获取指定动画模板"""
    library = AnimationTemplateLibrary()
    return library.get_template(template_id)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    library = AnimationTemplateLibrary()
    summary = library.get_template_summary()
    
    print("=" * 60)
    print("Remotion动画模板库")
    print("=" * 60)
    print(f"总模板数: {summary['total_templates']}")
    print(f"自定义模板: {summary['custom_templates']}")
    print(f"\n按类别:")
    for cat, count in summary["categories"].items():
        print(f"  {cat}: {count}个")
    
    print("\n" + "=" * 60)
    print("入场动画:")
    for tpl in library.list_templates("intro"):
        print(f"  - {tpl['name']} ({tpl['id']}): {tpl['description']}")
    
    print("\n循环动画:")
    for tpl in library.list_templates("loop"):
        print(f"  - {tpl['name']} ({tpl['id']}): {tpl['description']}")
