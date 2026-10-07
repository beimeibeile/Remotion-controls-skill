"""
cap_api_wrapper - Remotion API 封装
封装 Remotion 的 renderMedia / renderStill / selectComposition 等 API
"""
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List


class RemotionAPI:
    """Remotion API 封装"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)

    def _run(self, args: List[str]) -> subprocess.CompletedProcess:
        # Windows上npx是PowerShell脚本，需用cmd /c调用
        import sys
        if sys.platform == "win32":
            cmd = ["cmd", "/c", "npx", "remotion"] + args
        else:
            cmd = ["npx", "remotion"] + args
        return subprocess.run(
            cmd, cwd=str(self.project_path),
            capture_output=True, text=True, encoding='utf-8', errors='replace'
        )

    def render_media(
        self,
        entry: str,
        composition: str,
        output: str,
        *,
        transparent: bool = False,
        fps: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        props: Optional[Dict[str, Any]] = None,
        codec: str = "webm",
        sequence: bool = False,
    ) -> Dict[str, Any]:
        """渲染视频
        sequence=True时渲染PNG序列（输出目录内为element-00.png等）
        """
        args = ["render", entry, composition, output]
        if transparent:
            args.append("--transparent")
        if sequence:
            args.append("--sequence")
        if fps:
            args.extend(["--fps", str(fps)])
        if width:
            args.extend(["--width", str(width)])
        if height:
            args.extend(["--height", str(height)])
        if codec and not sequence:
            args.extend(["--codec", codec])
        if props:
            args.extend(["--props", json.dumps(props, ensure_ascii=False)])

        result = self._run(args)
        output_path = Path(output)
        return {
            "success": result.returncode == 0 and output_path.exists(),
            "output": str(output_path.absolute()) if output_path.exists() else None,
            "file_size": output_path.stat().st_size if output_path.exists() else 0,
        }

    def render_still(
        self,
        entry: str,
        composition: str,
        output: str,
        frame: int = 0,
        *,
        transparent: bool = False,
        props: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """渲染单帧图片"""
        args = ["still", entry, composition, output, "--frame", str(frame)]
        if transparent:
            args.append("--transparent")
        if props:
            args.extend(["--props", json.dumps(props, ensure_ascii=False)])

        result = self._run(args)
        output_path = Path(output)
        return {
            "success": result.returncode == 0 and output_path.exists(),
            "output": str(output_path.absolute()) if output_path.exists() else None,
        }

    def list_compositions(self, entry: str = "src/index.ts") -> List[Dict[str, Any]]:
        """列出所有 Composition"""
        result = self._run(["compositions", entry, "--json"])
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                pass
        return []
