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
    ) -> Dict[str, Any]:
        """渲染视频"""
        args = ["render", entry, composition, output]
        if transparent:
            args.append("--transparent")
        if fps:
            args.extend(["--fps", str(fps)])
        if width:
            args.extend(["--width", str(width)])
        if height:
            args.extend(["--height", str(height)])
        if codec:
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
