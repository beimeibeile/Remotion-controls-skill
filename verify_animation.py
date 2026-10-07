#!/usr/bin/env python3
"""
Remotion 动画素材自动化验证工具 v1.0
验证透明背景动画素材是否符合质量标准

用法:
    python verify_animation.py <动画文件路径> [--duration 预期时长秒] [--width 预期宽度] [--height 预期高度]
"""

import sys
import os
import json
import shutil
import subprocess
import argparse
from pathlib import Path

# 外部工具路径（环境变量可覆盖）
FFMPEG = os.environ.get("AVE_FFMPEG", shutil.which("ffmpeg") or r"D:\Ai\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe")
FFPROBE = os.environ.get("AVE_FFPROBE", shutil.which("ffprobe") or r"D:\Ai\ffmpeg-master-latest-win64-gpl\bin\ffprobe.exe")


def run_ffprobe(file_path: str) -> dict:
    """运行ffprobe获取视频信息"""
    cmd = [
        FFPROBE, "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        file_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": result.stderr}
    return json.loads(result.stdout)


def extract_frame(file_path: str, time_sec: float, output_path: str, fmt: str = "png") -> bool:
    """提取指定时间的帧（默认PNG保留Alpha通道）"""
    cmd = [
        FFMPEG, "-y",
        "-ss", str(time_sec),
        "-i", file_path,
        "-vframes", "1",
    ]
    if fmt == "png":
        cmd.extend(["-pix_fmt", "rgba"])
    else:
        cmd.extend(["-q:v", "2"])
    cmd.append(output_path)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def check_frame_has_content(frame_path: str) -> dict:
    """
    检查帧是否有可见内容
    对于透明背景动画：检查是否有非透明像素（Alpha>10）
    对于普通视频：检查平均亮度

    Returns:
        dict: {"has_content": bool, "alpha_ratio": float, "brightness": float, "detail": str}
    """
    try:
        from PIL import Image
        import numpy as np
        img = Image.open(frame_path)

        # 检查是否有Alpha通道
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            img = img.convert("RGBA")
            arr = np.array(img)
            alpha = arr[:, :, 3]
            # 非透明像素比例
            alpha_ratio = float((alpha > 10).sum() / alpha.size)
            # 非透明区域的平均亮度
            rgb = arr[:, :, :3]
            mask = alpha > 10
            if mask.any():
                brightness = float(rgb[mask].mean())
            else:
                brightness = 0.0
            has_content = alpha_ratio > 0.001  # 至少0.1%非透明像素
            return {
                "has_content": has_content,
                "alpha_ratio": alpha_ratio,
                "brightness": brightness,
                "detail": f"非透明像素={alpha_ratio*100:.1f}%, 亮度={brightness:.1f}"
            }
        else:
            # 无Alpha通道，检查亮度
            img_gray = img.convert("L")
            arr = np.array(img_gray)
            brightness = float(arr.mean())
            has_content = brightness > 5
            return {
                "has_content": has_content,
                "alpha_ratio": 1.0,
                "brightness": brightness,
                "detail": f"亮度={brightness:.1f}"
            }
    except ImportError:
        # 回退：用ffmpeg检查亮度
        cmd = [
            FFMPEG, "-i", frame_path,
            "-vf", "signalstats",
            "-f", "null", "-"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        for line in result.stderr.split("\n"):
            if "YAVG" in line:
                try:
                    brightness = float(line.split("YAVG=")[1].split()[0])
                    return {
                        "has_content": brightness > 5,
                        "alpha_ratio": 1.0,
                        "brightness": brightness,
                        "detail": f"亮度={brightness:.1f}"
                    }
                except (IndexError, ValueError):
                    pass
        return {"has_content": False, "alpha_ratio": 0, "brightness": -1, "detail": "无法解析"}


def verify_animation(file_path: str, expected_duration: float = None,
                     expected_width: int = 1080, expected_height: int = 1920,
                     expected_fps: int = 30) -> dict:
    """
    验证动画素材是否符合质量标准

    Returns:
        dict: {
            "passed": bool,
            "checks": [{name, status, detail, severity}],
            "summary": str
        }
    """
    results = {
        "file": file_path,
        "passed": True,
        "checks": [],
        "summary": ""
    }

    def add_check(name: str, status: str, detail: str, severity: str = "error"):
        results["checks"].append({
            "name": name,
            "status": status,
            "detail": detail,
            "severity": severity
        })
        if status == "FAIL" and severity == "error":
            results["passed"] = False

    # 1. 文件存在检查
    if not os.path.exists(file_path):
        add_check("文件存在", "FAIL", f"文件不存在: {file_path}")
        results["summary"] = "验证失败：文件不存在"
        return results

    file_size = os.path.getsize(file_path)
    if file_size == 0:
        add_check("文件非空", "FAIL", "文件大小为0")
        results["summary"] = "验证失败：文件为空"
        return results
    add_check("文件存在", "PASS", f"文件大小: {file_size/1024/1024:.2f}MB")

    # 2. ffprobe解析
    info = run_ffprobe(file_path)
    if "error" in info:
        add_check("ffprobe解析", "FAIL", f"解析失败: {info['error']}")
        results["summary"] = "验证失败：无法解析视频"
        return results
    add_check("ffprobe解析", "PASS", "解析成功")

    # 3. 视频流检查
    video_stream = None
    for stream in info.get("streams", []):
        if stream.get("codec_type") == "video":
            video_stream = stream
            break

    if not video_stream:
        add_check("视频流", "FAIL", "未找到视频流")
        results["summary"] = "验证失败：无视频流"
        return results

    # 4. Alpha通道检查
    pix_fmt = video_stream.get("pix_fmt", "")
    has_alpha = "a" in pix_fmt.lower() and "yuva" in pix_fmt.lower()
    if has_alpha:
        add_check("Alpha通道", "PASS", f"pix_fmt={pix_fmt}")
    else:
        add_check("Alpha通道", "FAIL", f"无Alpha通道: pix_fmt={pix_fmt}（需要yuva444p12le）")

    # 5. 编码格式检查
    codec = video_stream.get("codec_name", "")
    if "prores" in codec.lower():
        profile = video_stream.get("profile", "")
        add_check("编码格式", "PASS", f"codec={codec}, profile={profile}")
    else:
        add_check("编码格式", "FAIL", f"非ProRes编码: codec={codec}（需要prores_ks profile=4）")

    # 6. 分辨率检查
    width = video_stream.get("width", 0)
    height = video_stream.get("height", 0)
    if width == expected_width and height == expected_height:
        add_check("分辨率", "PASS", f"{width}x{height}")
    else:
        add_check("分辨率", "FAIL", f"{width}x{height}（预期{expected_width}x{expected_height}）", "warning")

    # 7. 帧率检查
    fps_str = video_stream.get("r_frame_rate", "0/1")
    try:
        num, den = fps_str.split("/")
        fps = float(num) / float(den) if float(den) != 0 else 0
        if abs(fps - expected_fps) < 1:
            add_check("帧率", "PASS", f"{fps:.1f}fps")
        else:
            add_check("帧率", "FAIL", f"{fps:.1f}fps（预期{expected_fps}fps）", "warning")
    except (ValueError, ZeroDivisionError):
        add_check("帧率", "FAIL", f"无法解析帧率: {fps_str}")

    # 8. 时长检查
    duration = float(info.get("format", {}).get("duration", 0))
    if expected_duration:
        if abs(duration - expected_duration) < 0.1:
            add_check("时长", "PASS", f"{duration:.2f}s")
        else:
            add_check("时长", "FAIL", f"{duration:.2f}s（预期{expected_duration}s）", "warning")
    else:
        add_check("时长", "PASS", f"{duration:.2f}s")

    # 9. 文件大小合理性检查
    max_size_mb = duration * 15  # 每秒最多15MB
    if file_size / 1024 / 1024 <= max_size_mb:
        add_check("文件大小", "PASS", f"{file_size/1024/1024:.2f}MB（上限{max_size_mb:.0f}MB）")
    else:
        add_check("文件大小", "FAIL", f"{file_size/1024/1024:.2f}MB（超过上限{max_size_mb:.0f}MB）", "warning")

    # 10. 动画内容覆盖检查（多点采样）
    tmp_dir = os.path.join(os.path.dirname(file_path), ".verify_tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    # 在10个时间点采样，检查内容覆盖率
    sample_points = [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95]
    content_count = 0
    content_details = []
    for i, ratio in enumerate(sample_points):
        t = duration * ratio
        frame_path = os.path.join(tmp_dir, f"sample_{i}.png")
        if extract_frame(file_path, t, frame_path, fmt="png"):
            result = check_frame_has_content(frame_path)
            if result["has_content"]:
                content_count += 1
            content_details.append(f"{t:.1f}s:{result['alpha_ratio']*100:.0f}%")
        else:
            content_details.append(f"{t:.1f}s:ERR")

    coverage = content_count / len(sample_points)
    # 短动画（<10秒）阈值降低，因为可能有合理的空档期
    min_coverage = 0.3 if duration < 10 else 0.5
    if coverage >= min_coverage:
        add_check("内容覆盖", "PASS", f"覆盖率={coverage*100:.0f}% ({content_count}/{len(sample_points)}) | {' '.join(content_details)}")
    elif coverage > 0:
        add_check("内容覆盖", "FAIL", f"覆盖率过低={coverage*100:.0f}% ({content_count}/{len(sample_points)}) | {' '.join(content_details)}")
    else:
        add_check("内容覆盖", "FAIL", f"全程无内容 | {' '.join(content_details)}")

    # 首帧检查（记录用，不影响通过）
    first_frame = os.path.join(tmp_dir, "first_frame.png")
    if extract_frame(file_path, 0.1, first_frame, fmt="png"):
        result = check_frame_has_content(first_frame)
        status = "PASS" if result["has_content"] else "INFO"
        add_check("首帧内容", status, result["detail"], "info")
    else:
        add_check("首帧内容", "SKIP", "无法提取首帧")

    # 末帧检查（记录用，不影响通过）
    last_frame = os.path.join(tmp_dir, "last_frame.png")
    if extract_frame(file_path, max(0.1, duration - 0.1), last_frame, fmt="png"):
        result = check_frame_has_content(last_frame)
        status = "PASS" if result["has_content"] else "INFO"
        add_check("末帧内容", status, result["detail"], "info")
    else:
        add_check("末帧内容", "SKIP", "无法提取末帧")

    # 清理临时文件
    import shutil
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir, ignore_errors=True)

    # 汇总
    passed_count = sum(1 for c in results["checks"] if c["status"] == "PASS")
    fail_count = sum(1 for c in results["checks"] if c["status"] == "FAIL")
    skip_count = sum(1 for c in results["checks"] if c["status"] == "SKIP")

    if results["passed"]:
        results["summary"] = f"✅ 验证通过：{passed_count}项通过，{fail_count}项失败，{skip_count}项跳过"
    else:
        results["summary"] = f"❌ 验证失败：{passed_count}项通过，{fail_count}项失败，{skip_count}项跳过"

    return results


def print_results(results: dict):
    """打印验证结果"""
    print("=" * 60)
    print(f"动画素材验证: {os.path.basename(results['file'])}")
    print("=" * 60)

    for check in results["checks"]:
        status_icon = {"PASS": "✅", "FAIL": "❌", "SKIP": "⚠️"}.get(check["status"], "?")
        print(f"  {status_icon} {check['name']}: {check['detail']}")

    print("-" * 60)
    print(results["summary"])
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Remotion动画素材验证工具")
    parser.add_argument("file", help="动画文件路径")
    parser.add_argument("--duration", type=float, help="预期时长（秒）")
    parser.add_argument("--width", type=int, default=1080, help="预期宽度（默认1080）")
    parser.add_argument("--height", type=int, default=1920, help="预期高度（默认1920）")
    parser.add_argument("--fps", type=int, default=30, help="预期帧率（默认30）")
    parser.add_argument("--json", action="store_true", help="输出JSON格式")

    args = parser.parse_args()

    results = verify_animation(
        args.file,
        expected_duration=args.duration,
        expected_width=args.width,
        expected_height=args.height,
        expected_fps=args.fps
    )

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print_results(results)

    sys.exit(0 if results["passed"] else 1)


if __name__ == "__main__":
    main()
