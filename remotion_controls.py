#!/usr/bin/env python3
"""
Remotion Controls - 主控制脚本
用代码驱动视频动画的专业控制技能

用法:
  python remotion_controls.py render --comp MyComp --output out.webm --transparent
  python remotion_controls.py serve --port 8765
  python remotion_controls.py list-compositions
  python remotion_controls.py render-json --input animation.json --output out.webm
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

# 项目根目录
SKILL_ROOT = Path(__file__).parent
REMOTION_PROJECT = SKILL_ROOT / "remotion-project"
OUTPUT_DIR = SKILL_ROOT / "output"

# 确保输出目录存在
OUTPUT_DIR.mkdir(exist_ok=True)


class RemotionControls:
    """Remotion 主控制器"""

    def __init__(self, project_path: Optional[str] = None):
        self.project_path = Path(project_path) if project_path else REMOTION_PROJECT

    def _run_npx(self, args: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
        """运行 npx 命令"""
        work_dir = cwd or self.project_path
        cmd = ["npx", "remotion"] + args
        print(f"  运行: {' '.join(cmd)}")
        print(f"  目录: {work_dir}")
        # Windows上npx是.cmd脚本，需要shell=True
        use_shell = os.name == 'nt'
        result = subprocess.run(
            cmd,
            cwd=str(work_dir),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            shell=use_shell,
        )
        if result.returncode != 0:
            print(f"  ❌ 错误: {result.stderr}")
        return result

    def list_compositions(self) -> List[Dict[str, Any]]:
        """列出所有可用的 Composition"""
        result = self._run_npx(["compositions", "src/index.ts", "--json"])
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                print(f"  ⚠️ 无法解析输出: {result.stdout[:200]}")
        return []

    def render_transparent(
        self,
        composition: str,
        output: str,
        *,
        fps: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        props: Optional[Dict[str, Any]] = None,
        frames: Optional[str] = None,
        output_format: str = "prores",
        cleanup: bool = True,
    ) -> Dict[str, Any]:
        """
        渲染带透明背景(Alpha通道)的视频

        完整流程：Remotion渲染PNG序列 → ffmpeg合成ProRes 4444(yuva444p12le)
        这是经过验证的唯一可靠方案（Remotion直接编码的WebM/MOV会丢失Alpha）

        Args:
            composition: Composition 名称
            output: 输出文件路径（.mov）
            fps: 帧率
            width: 宽度
            height: 高度
            props: 传递给 Composition 的 Props
            frames: 渲染帧范围，如 "0-150"
            output_format: 输出格式 (prores / apng)
            cleanup: 是否清理临时PNG序列

        Returns:
            渲染结果字典
        """
        import shutil
        import tempfile

        # 如果有props，写入animation-config.ts文件（避免命令行长度限制）
        config_file = self.project_path / "src" / "animation-config.ts"
        if props:
            config_content = (
                "// 动画配置 - 由 render-transparent 命令自动生成\n"
                "// 不要手动编辑此文件\n"
                f"export const animationConfig = {json.dumps(props, ensure_ascii=False, indent=2)};\n"
            )
            config_file.write_text(config_content, encoding='utf-8')
            print(f"  已写入配置到: {config_file.name}")

        # 临时目录存放PNG序列
        seq_dir = Path(tempfile.mkdtemp(prefix="remotion_seq_"))
        print(f"  临时序列目录: {seq_dir}")

        try:
            # Step 1: Remotion 渲染 PNG 序列（带透明）
            render_args = ["render", "src/index.ts", composition, str(seq_dir),
                          "--transparent", "--sequence"]
            if fps:
                render_args.extend(["--fps", str(fps)])
            if width:
                render_args.extend(["--width", str(width)])
            if height:
                render_args.extend(["--height", str(height)])
            if frames:
                render_args.extend(["--frames", frames])
            # 注意：props已写入animation-config.ts，不通过命令行传递（避免Windows命令行长度限制）

            print("  Step 1: 渲染PNG序列...")
            result = self._run_npx(render_args)
            if result.returncode != 0:
                return {"success": False, "error": "PNG序列渲染失败", "stderr": result.stderr[-500:]}

            # 检查序列文件
            png_files = sorted(seq_dir.glob("*.png"))
            if not png_files:
                return {"success": False, "error": "未找到PNG序列文件"}
            print(f"  序列帧数: {len(png_files)}")

            # 确定文件名模式（自动检测前缀和数字位数）
            first_name = png_files[0].name
            import re
            # 匹配 element-00.png, element-000.png, 0000.png 等格式
            m = re.match(r'^(.+?-)(\d+)\.png$', first_name)
            if m:
                prefix = m.group(1)  # 如 "element-"
                digits = len(m.group(2))  # 数字位数
                seq_pattern = f"{prefix}%0{digits}d.png"
            else:
                # 纯数字文件名如 0000.png
                m2 = re.match(r'^(\d+)\.png$', first_name)
                if m2:
                    digits = len(m2.group(1))
                    seq_pattern = f"%0{digits}d.png"
                else:
                    seq_pattern = "%04d.png"  # 兜底
            print(f"  文件名模式: {seq_pattern}")

            # Step 2: ffmpeg 合成带Alpha的视频
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if output_format == "prores":
                # ProRes 4444 with Alpha (yuva444p12le) - 剪映兼容
                print("  Step 2: ffmpeg合成ProRes 4444 (含Alpha)...")
                ffmpeg_cmd = [
                    "ffmpeg", "-y",
                    "-framerate", str(fps or 30),
                    "-i", str(seq_dir / seq_pattern),
                    "-c:v", "prores_ks",
                    "-profile:v", "4",
                    "-pix_fmt", "yuva444p12le",
                    str(output_path)
                ]
            elif output_format == "apng":
                # APNG (rgba) - 文件极小，但剪映可能不支持
                print("  Step 2: ffmpeg合成APNG (含Alpha)...")
                ffmpeg_cmd = [
                    "ffmpeg", "-y",
                    "-framerate", str(fps or 30),
                    "-i", str(seq_dir / seq_pattern),
                    "-plays", "0",
                    "-f", "apng",
                    str(output_path)
                ]
            else:
                return {"success": False, "error": f"不支持的输出格式: {output_format}"}

            ffmpeg_result = subprocess.run(
                ffmpeg_cmd, capture_output=True, text=True, encoding='utf-8', errors='replace'
            )
            if ffmpeg_result.returncode != 0:
                return {"success": False, "error": "ffmpeg合成失败", "stderr": ffmpeg_result.stderr[-500:]}

            # 验证Alpha通道
            alpha_check = self.check_alpha(str(output_path))

            result_data = {
                "success": output_path.exists(),
                "output": str(output_path.absolute()) if output_path.exists() else None,
                "composition": composition,
                "format": output_format,
                "frames": len(png_files),
                "file_size_mb": round(output_path.stat().st_size / 1024 / 1024, 2) if output_path.exists() else 0,
                "alpha_channel": alpha_check.get("has_alpha", False),
                "pix_fmt": alpha_check.get("pix_fmt", ""),
            }

            print(f"  ✅ 渲染完成: {result_data['file_size_mb']}MB, Alpha={result_data['alpha_channel']}, pix_fmt={result_data['pix_fmt']}")
            return result_data

        finally:
            if cleanup and seq_dir.exists():
                shutil.rmtree(seq_dir, ignore_errors=True)
                print(f"  已清理临时目录: {seq_dir}")

    def render_media(
        self,
        composition: str,
        output: str,
        *,
        transparent: bool = False,
        fps: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        props: Optional[Dict[str, Any]] = None,
        format: str = "webm",
    ) -> Dict[str, Any]:
        """
        渲染视频

        Args:
            composition: Composition 名称
            output: 输出文件路径
            transparent: 是否渲染透明背景
            fps: 帧率
            width: 宽度
            height: 高度
            props: 传递给 Composition 的 Props
            format: 输出格式 (webm/mov/mp4)

        Returns:
            渲染结果字典
        """
        args = ["render", "src/index.ts", composition, output]

        if transparent:
            args.append("--transparent")

        if fps:
            args.extend(["--fps", str(fps)])

        if width:
            args.extend(["--width", str(width)])

        if height:
            args.extend(["--height", str(height)])

        if format:
            args.extend(["--codec", format])

        if props:
            props_json = json.dumps(props, ensure_ascii=False)
            args.extend(["--props", props_json])

        result = self._run_npx(args)

        output_path = Path(output)
        success = result.returncode == 0 and output_path.exists()

        return {
            "success": success,
            "output": str(output_path.absolute()) if success else None,
            "composition": composition,
            "transparent": transparent,
            "format": format,
            "file_size": output_path.stat().st_size if success else 0,
            "stdout": result.stdout[-500:] if result.stdout else "",
            "stderr": result.stderr[-500:] if result.stderr else "",
        }

    def render_still(
        self,
        composition: str,
        output: str,
        frame: int = 0,
        *,
        transparent: bool = False,
        props: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """渲染单帧图片"""
        args = ["still", "src/index.ts", composition, output, "--frame", str(frame)]

        if transparent:
            args.append("--transparent")

        if props:
            props_json = json.dumps(props, ensure_ascii=False)
            args.extend(["--props", props_json])

        result = self._run_npx(args)
        output_path = Path(output)

        return {
            "success": result.returncode == 0 and output_path.exists(),
            "output": str(output_path.absolute()) if output_path.exists() else None,
            "frame": frame,
        }

    def render_from_json(
        self,
        input_json: str,
        output: str,
        *,
        transparent: bool = True,
    ) -> Dict[str, Any]:
        """
        从动画指令 JSON 渲染视频

        动画指令格式:
        {
          "composition": "AnimationTemplate",
          "fps": 30,
          "width": 1080,
          "height": 1920,
          "duration": 20,
          "layers": [
            {
              "id": "doubao",
              "image": "assets/doubao.png",
              "keyframes": [
                {"time": 0, "x": 200, "y": 380, "scale": 0.38, "opacity": 1},
                {"time": 3, "x": 200, "y": 380, "scale": 0.38, "opacity": 1}
              ]
            }
          ]
        }
        """
        with open(input_json, 'r', encoding='utf-8') as f:
            anim_config = json.load(f)

        composition = anim_config.get("composition", "AnimationTemplate")
        fps = anim_config.get("fps", 30)
        width = anim_config.get("width", 1080)
        height = anim_config.get("height", 1920)

        return self.render_media(
            composition=composition,
            output=output,
            transparent=transparent,
            fps=fps,
            width=width,
            height=height,
            props=anim_config,
        )

    def check_alpha(self, video_path: str) -> Dict[str, Any]:
        """检查视频是否包含 Alpha 通道"""
        cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0",
               "-show_entries", "stream=pix_fmt,codec_name", "-of", "json", video_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                stream = data.get("streams", [{}])[0]
                pix_fmt = stream.get("pix_fmt", "")
                has_alpha = any(a in pix_fmt for a in ["yuva", "rgba", "bgra", "gbra", "ya"])
                return {
                    "has_alpha": has_alpha,
                    "pix_fmt": pix_fmt,
                    "codec": stream.get("codec_name", ""),
                }
            except json.JSONDecodeError:
                pass
        return {"has_alpha": False, "error": result.stderr}


def main():
    parser = argparse.ArgumentParser(description="Remotion Controls - 代码驱动视频动画控制")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # render 命令
    render_parser = subparsers.add_parser("render", help="渲染视频")
    render_parser.add_argument("--comp", required=True, help="Composition 名称")
    render_parser.add_argument("--output", required=True, help="输出文件路径")
    render_parser.add_argument("--transparent", action="store_true", help="渲染透明背景")
    render_parser.add_argument("--fps", type=int, help="帧率")
    render_parser.add_argument("--width", type=int, help="宽度")
    render_parser.add_argument("--height", type=int, help="高度")
    render_parser.add_argument("--format", default="webm", help="输出格式")

    # render-json 命令
    rj_parser = subparsers.add_parser("render-json", help="从JSON指令渲染视频")
    rj_parser.add_argument("--input", required=True, help="动画指令JSON文件")
    rj_parser.add_argument("--output", required=True, help="输出文件路径")
    rj_parser.add_argument("--no-transparent", action="store_true", help="不渲染透明背景")

    # render-transparent 命令（推荐：PNG序列→ProRes 4444，可靠Alpha）
    rt_parser = subparsers.add_parser("render-transparent", help="渲染带Alpha通道的透明背景视频（推荐）")
    rt_parser.add_argument("--comp", required=True, help="Composition 名称")
    rt_parser.add_argument("--output", required=True, help="输出文件路径(.mov)")
    rt_parser.add_argument("--fps", type=int, help="帧率")
    rt_parser.add_argument("--width", type=int, help="宽度")
    rt_parser.add_argument("--height", type=int, help="高度")
    rt_parser.add_argument("--frames", help="渲染帧范围，如 0-150")
    rt_parser.add_argument("--format", default="prores", choices=["prores", "apng"], help="输出格式")
    rt_parser.add_argument("--props", help="传递给Composition的Props(JSON字符串)")
    rt_parser.add_argument("--props-file", help="从JSON文件读取Props(推荐，避免命令行转义问题)")
    rt_parser.add_argument("--no-cleanup", action="store_true", help="不清理临时PNG序列")

    # list 命令
    subparsers.add_parser("list", help="列出所有 Composition")

    # still 命令
    still_parser = subparsers.add_parser("still", help="渲染单帧图片")
    still_parser.add_argument("--comp", required=True, help="Composition 名称")
    still_parser.add_argument("--output", required=True, help="输出文件路径")
    still_parser.add_argument("--frame", type=int, default=0, help="帧号")
    still_parser.add_argument("--transparent", action="store_true", help="透明背景")

    # check-alpha 命令
    alpha_parser = subparsers.add_parser("check-alpha", help="检查视频Alpha通道")
    alpha_parser.add_argument("--video", required=True, help="视频文件路径")

    # serve 命令
    serve_parser = subparsers.add_parser("serve", help="启动API服务")
    serve_parser.add_argument("--port", type=int, default=8765, help="API端口")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    controls = RemotionControls()

    if args.command == "render":
        print(f"渲染 Composition: {args.comp}")
        result = controls.render_media(
            composition=args.comp,
            output=args.output,
            transparent=args.transparent,
            fps=args.fps,
            width=args.width,
            height=args.height,
            format=args.format,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "render-json":
        print(f"从JSON渲染: {args.input}")
        result = controls.render_from_json(
            input_json=args.input,
            output=args.output,
            transparent=not args.no_transparent,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "render-transparent":
        print(f"渲染透明背景视频: {args.comp}")
        props = None
        if args.props_file:
            try:
                with open(args.props_file, 'r', encoding='utf-8') as f:
                    props = json.load(f)
                print(f"  从文件加载Props: {args.props_file}")
            except Exception as e:
                print(f"⚠️ Props文件读取失败: {e}")
        elif args.props:
            try:
                props = json.loads(args.props)
            except json.JSONDecodeError:
                print(f"⚠️ Props JSON解析失败，忽略")
        result = controls.render_transparent(
            composition=args.comp,
            output=args.output,
            fps=args.fps,
            width=args.width,
            height=args.height,
            props=props,
            frames=args.frames,
            output_format=args.format,
            cleanup=not args.no_cleanup,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "list":
        comps = controls.list_compositions()
        print(f"可用 Composition ({len(comps)}):")
        for c in comps:
            print(f"  - {c.get('id', '?')}: {c.get('width', '?')}x{c.get('height', '?')} @ {c.get('fps', '?')}fps, {c.get('durationInFrames', '?')}帧")

    elif args.command == "still":
        result = controls.render_still(
            composition=args.comp,
            output=args.output,
            frame=args.frame,
            transparent=args.transparent,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "check-alpha":
        result = controls.check_alpha(args.video)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "serve":
        print(f"启动 API 服务在端口 {args.port}...")
        print("（API服务功能开发中）")


if __name__ == "__main__":
    main()
