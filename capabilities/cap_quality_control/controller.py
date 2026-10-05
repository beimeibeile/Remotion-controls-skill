"""
cap_quality_control - 质量控制
帧率、分辨率、Alpha通道完整性、视频时长、文件大小检测
"""
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional


class QualityController:
    """质量控制器"""

    def __init__(self):
        self.checks = []

    def check_video(self, video_path: str, expected: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        全面检查视频质量

        Args:
            video_path: 视频文件路径
            expected: 期望值字典 {fps, width, height, duration, has_alpha, max_size_mb}

        Returns:
            检查结果字典
        """
        path = Path(video_path)
        if not path.exists():
            return {"success": False, "error": f"文件不存在: {video_path}"}

        result = {
            "file": str(path.absolute()),
            "file_size_mb": round(path.stat().st_size / 1024 / 1024, 2),
            "checks": {},
            "passed": True,
            "warnings": [],
        }

        # ffprobe 探测
        probe = self._ffprobe(video_path)
        if probe:
            video_stream = next((s for s in probe.get("streams", []) if s.get("codec_type") == "video"), {})
            result["checks"]["codec"] = video_stream.get("codec_name", "")
            result["checks"]["pix_fmt"] = video_stream.get("pix_fmt", "")
            result["checks"]["width"] = video_stream.get("width", 0)
            result["checks"]["height"] = video_stream.get("height", 0)
            result["checks"]["fps"] = self._parse_fps(video_stream.get("r_frame_rate", "0/0"))
            result["checks"]["duration"] = float(probe.get("format", {}).get("duration", 0))

            # Alpha 通道检测
            pix_fmt = video_stream.get("pix_fmt", "")
            has_alpha = any(a in pix_fmt for a in ["yuva", "rgba", "bgra", "gbra", "ya"])
            result["checks"]["has_alpha"] = has_alpha

        # 与期望值对比
        if expected:
            for key, expected_val in expected.items():
                actual_val = result["checks"].get(key)
                if actual_val is not None:
                    if key == "duration":
                        diff = abs(actual_val - expected_val)
                        if diff > 1.0:
                            result["passed"] = False
                            result["warnings"].append(f"{key}: 期望{expected_val}s, 实际{actual_val:.1f}s, 差异{diff:.1f}s")
                    elif key == "has_alpha":
                        if expected_val and not actual_val:
                            result["passed"] = False
                            result["warnings"].append(f"{key}: 期望有Alpha通道, 实际无")
                    elif key == "max_size_mb":
                        if result["file_size_mb"] > expected_val:
                            result["passed"] = False
                            result["warnings"].append(f"文件大小: {result['file_size_mb']}MB > {expected_val}MB")
                    else:
                        if actual_val != expected_val:
                            result["warnings"].append(f"{key}: 期望{expected_val}, 实际{actual_val}")

        return result

    def _ffprobe(self, video_path: str) -> Optional[Dict[str, Any]]:
        """用 ffprobe 探测视频信息"""
        cmd = ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", video_path]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception:
            pass
        return None

    def _parse_fps(self, fps_str: str) -> float:
        """解析帧率字符串 (如 '30/1')"""
        try:
            num, den = fps_str.split('/')
            return round(float(num) / float(den), 2) if float(den) != 0 else 0
        except Exception:
            return 0
