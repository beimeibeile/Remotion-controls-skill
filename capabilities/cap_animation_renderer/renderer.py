"""
cap_animation_renderer - 动画渲染器 v2.0
从动画指令 JSON 渲染透明背景视频，支持关键帧/缓动/多图层/PNG序列+ProRes 4444管线
"""
import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple


# 外部工具路径（环境变量可覆盖）
FFMPEG = os.environ.get("AVE_FFMPEG", shutil.which("ffmpeg") or r"D:\Ai\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe")
FFPROBE = os.environ.get("AVE_FFPROBE", shutil.which("ffprobe") or r"D:\Ai\ffmpeg-master-latest-win64-gpl\bin\ffprobe.exe")


# 缓动曲线常量（对应Remotion Easing）
EASING = {
    "linear": "linear",
    "ease_in": "easeIn",
    "ease_out": "easeOut",
    "ease_in_out": "easeInOut",
    "spring": "spring",
    "bounce": "bounce",
    "anticipate": "anticipate",
}


class KeyframeBuilder:
    """关键帧动画配置构建器"""

    def __init__(self):
        self.position: List[Dict] = []
        self.scale: List[Dict] = []
        self.rotation: List[Dict] = []
        self.opacity: List[Dict] = []

    def add_position(self, frame: int, x: float, y: float, easing: str = "ease_out"):
        """添加位置关键帧"""
        self.position.append({"frame": frame, "x": x, "y": y, "easing": EASING.get(easing, easing)})
        return self

    def add_scale(self, frame: int, sx: float, sy: float = None, easing: str = "ease_out"):
        """添加缩放关键帧"""
        self.scale.append({"frame": frame, "x": sx, "y": sy if sy is not None else sx, "easing": EASING.get(easing, easing)})
        return self

    def add_rotation(self, frame: int, degrees: float, easing: str = "ease_out"):
        """添加旋转关键帧"""
        self.rotation.append({"frame": frame, "degrees": degrees, "easing": EASING.get(easing, easing)})
        return self

    def add_opacity(self, frame: int, alpha: float, easing: str = "ease_out"):
        """添加透明度关键帧（0-1）"""
        self.opacity.append({"frame": frame, "alpha": max(0.0, min(1.0, alpha)), "easing": EASING.get(easing, easing)})
        return self

    def build(self) -> Dict[str, Any]:
        """构建关键帧配置"""
        return {
            "position": sorted(self.position, key=lambda k: k["frame"]),
            "scale": sorted(self.scale, key=lambda k: k["frame"]),
            "rotation": sorted(self.rotation, key=lambda k: k["frame"]),
            "opacity": sorted(self.opacity, key=lambda k: k["frame"]),
        }


class LayerBuilder:
    """多图层合成配置构建器"""

    def __init__(self):
        self.layers: List[Dict[str, Any]] = []

    def add_image_layer(self, image_path: str, *,
                        x: float = 0, y: float = 0,
                        width: float = None, height: float = None,
                        keyframes: Dict = None,
                        z_index: int = 0) -> "LayerBuilder":
        """添加图片图层"""
        layer = {
            "type": "image",
            "src": image_path,
            "x": x, "y": y,
            "z_index": z_index,
        }
        if width: layer["width"] = width
        if height: layer["height"] = height
        if keyframes: layer["keyframes"] = keyframes
        self.layers.append(layer)
        return self

    def add_text_layer(self, text: str, *,
                       x: float = 0, y: float = 0,
                       font_size: int = 48, color: str = "#ffffff",
                       font_family: str = "Arial",
                       keyframes: Dict = None,
                       z_index: int = 1) -> "LayerBuilder":
        """添加文字图层"""
        layer = {
            "type": "text",
            "text": text,
            "x": x, "y": y,
            "font_size": font_size,
            "color": color,
            "font_family": font_family,
            "z_index": z_index,
        }
        if keyframes: layer["keyframes"] = keyframes
        self.layers.append(layer)
        return self

    def add_shape_layer(self, shape: str = "circle", *,
                        x: float = 0, y: float = 0,
                        size: float = 100, color: str = "#ffffff",
                        keyframes: Dict = None,
                        z_index: int = 0) -> "LayerBuilder":
        """添加形状图层（circle/rect/line）"""
        layer = {
            "type": "shape",
            "shape": shape,
            "x": x, "y": y,
            "size": size,
            "color": color,
            "z_index": z_index,
        }
        if keyframes: layer["keyframes"] = keyframes
        self.layers.append(layer)
        return self

    def build(self) -> List[Dict[str, Any]]:
        """构建图层列表（按z_index排序）"""
        return sorted(self.layers, key=lambda l: l.get("z_index", 0))


class AnimationRenderer:
    """动画渲染器 v2.0"""

    def __init__(self, project_path: str, output_dir: Optional[str] = None):
        self.project_path = Path(project_path)
        self.output_dir = Path(output_dir) if output_dir else self.project_path / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._last_render_info: Dict[str, Any] = {}

    def render_from_config(
        self,
        config: Dict[str, Any],
        output_name: Optional[str] = None,
        *,
        transparent: bool = True,
        use_prores: bool = False,
    ) -> Dict[str, Any]:
        """
        从动画配置渲染视频

        配置格式:
        {
          "composition": "AnimationTemplate",
          "fps": 30, "width": 1080, "height": 1920, "duration": 20,
          "layers": [...]
        }
        """
        composition = config.get("composition", "AnimationTemplate")
        fps = config.get("fps", 30)
        width = config.get("width", 1080)
        height = config.get("height", 1920)

        if use_prores:
            # PNG序列 + ProRes 4444 管线（保留Alpha通道）
            return self._render_prores_pipeline(config, composition, fps, width, height, output_name)

        if output_name is None:
            output_name = f"{composition}_{fps}fps.webm"
        output_path = str(self.output_dir / output_name)

        # 延迟import避免循环依赖
        from ..cap_api_wrapper.api import RemotionAPI
        api = RemotionAPI(str(self.project_path))
        result = api.render_media(
            entry="src/index.ts",
            composition=composition,
            output=output_path,
            transparent=transparent,
            fps=fps, width=width, height=height,
            props=config, codec="webm",
        )
        self._last_render_info = {"output": output_path, "method": "direct", "config": config}
        return result

    def _render_prores_pipeline(
        self, config: Dict, composition: str,
        fps: int, width: int, height: int,
        output_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        PNG序列渲染 + ffmpeg合成ProRes 4444（已验证保留Alpha通道）
        PIT-024: CLI --transparent会丢失Alpha，必须用此管线
        """
        from ..cap_api_wrapper.api import RemotionAPI
        api = RemotionAPI(str(self.project_path))

        # 1. PNG序列渲染（--sequence标志，输出element-00.png格式）
        frames_dir = self.output_dir / f"{composition}_frames"
        frames_dir.mkdir(exist_ok=True)
        seq_result = api.render_media(
            entry="src/index.ts",
            composition=composition,
            output=str(frames_dir),
            transparent=True,
            fps=fps, width=width, height=height,
            props=config, sequence=True,
        )

        # 2. ffmpeg合成ProRes 4444
        if output_name is None:
            output_name = f"{composition}_prores4444.mov"
        output_path = str(self.output_dir / output_name)

        # Remotion PNG序列输出格式为element-00.png, element-01.png...
        ffmpeg_cmd = [
            FFMPEG, "-y",
            "-framerate", str(fps),
            "-i", str(frames_dir / "element-%02d.png"),
            "-c:v", "prores_ks",
            "-profile:v", "4",
            "-pix_fmt", "yuva444p12le",
            output_path,
        ]
        proc = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

        result = {
            "success": proc.returncode == 0,
            "output": output_path,
            "method": "prores_png_sequence",
            "frames_dir": str(frames_dir),
            "ffmpeg_returncode": proc.returncode,
        }
        if proc.returncode != 0:
            result["error"] = proc.stderr[-500:]
        self._last_render_info = result
        return result

    def render_from_json_file(
        self, json_path: str, output_name: Optional[str] = None, *,
        transparent: bool = True, use_prores: bool = False,
    ) -> Dict[str, Any]:
        """从 JSON 文件渲染"""
        with open(json_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return self.render_from_config(config, output_name, transparent=transparent, use_prores=use_prores)

    def verify_output(self, output_path: str, *,
                      expected_duration: float = None,
                      expected_width: int = None,
                      expected_height: int = None,
                      check_alpha: bool = True) -> Dict[str, Any]:
        """验证渲染输出（时长/分辨率/Alpha通道）"""
        result = {"path": output_path, "exists": os.path.exists(output_path)}
        if not result["exists"]:
            return result

        result["size_bytes"] = os.path.getsize(output_path)

        # ffprobe检测
        try:
            proc = subprocess.run(
                [FFPROBE, "-v", "error", "-select_streams", "v:0",
                 "-show_entries", "stream=codec_name,width,height,pix_fmt,duration",
                 "-of", "json", output_path],
                capture_output=True, text=True, timeout=10,
            )
            if proc.returncode == 0:
                info = json.loads(proc.stdout).get("streams", [{}])[0]
                result["codec"] = info.get("codec_name")
                result["width"] = int(info.get("width", 0))
                result["height"] = int(info.get("height", 0))
                result["pix_fmt"] = info.get("pix_fmt")
                result["duration"] = float(info.get("duration", 0))
                result["has_alpha"] = "a" in (info.get("pix_fmt") or "")

                if expected_duration:
                    result["duration_match"] = abs(result["duration"] - expected_duration) < 0.5
                if expected_width:
                    result["width_match"] = result["width"] == expected_width
                if expected_height:
                    result["height_match"] = result["height"] == expected_height
        except Exception as e:
            result["probe_error"] = str(e)

        return result

    def get_render_info(self) -> Dict[str, Any]:
        """获取最近一次渲染信息"""
        return dict(self._last_render_info)

    @staticmethod
    def create_fall_animation(start_frame: int, end_frame: int,
                              start_x: float, start_y: float,
                              end_y: float) -> Dict:
        """便捷创建下落动画配置（豆包被打等场景）"""
        kb = KeyframeBuilder()
        kb.add_position(start_frame, start_x, start_y, "ease_in")
        kb.add_position(end_frame, start_x, end_y, "ease_in")
        kb.add_rotation(start_frame, 0, "ease_in")
        kb.add_rotation(end_frame, 15, "ease_in")
        return kb.build()
