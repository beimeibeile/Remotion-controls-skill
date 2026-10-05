"""
cap_animation_renderer - 动画渲染器
从动画指令 JSON 渲染透明背景视频
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

from ..cap_api_wrapper.api import RemotionAPI


class AnimationRenderer:
    """动画渲染器"""

    def __init__(self, project_path: str, output_dir: Optional[str] = None):
        self.api = RemotionAPI(project_path)
        self.output_dir = Path(output_dir) if output_dir else Path(project_path) / "output"
        self.output_dir.mkdir(exist_ok=True)

    def render_from_config(
        self,
        config: Dict[str, Any],
        output_name: Optional[str] = None,
        *,
        transparent: bool = True,
    ) -> Dict[str, Any]:
        """
        从动画配置渲染视频

        配置格式:
        {
          "composition": "AnimationTemplate",
          "fps": 30,
          "width": 1080,
          "height": 1920,
          "duration": 20,
          "layers": [...]
        }
        """
        composition = config.get("composition", "AnimationTemplate")
        fps = config.get("fps", 30)
        width = config.get("width", 1080)
        height = config.get("height", 1920)

        if output_name is None:
            output_name = f"{composition}_{fps}fps.webm"

        output_path = str(self.output_dir / output_name)

        return self.api.render_media(
            entry="src/index.ts",
            composition=composition,
            output=output_path,
            transparent=transparent,
            fps=fps,
            width=width,
            height=height,
            props=config,
            codec="webm",
        )

    def render_from_json_file(
        self,
        json_path: str,
        output_name: Optional[str] = None,
        *,
        transparent: bool = True,
    ) -> Dict[str, Any]:
        """从 JSON 文件渲染"""
        with open(json_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return self.render_from_config(config, output_name, transparent=transparent)
