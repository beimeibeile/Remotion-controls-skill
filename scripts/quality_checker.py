"""
Remotion质量检测工具
- 渲染质量检测
- Alpha通道检测
- 帧率检测
- 分辨率检测
- 码率检测
- 输出文件验证
"""

import os
import sys
import logging
import subprocess
import json
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

FFPROBE = r"D:\Ai\ffmpeg-master-latest-win64-gpl\bin\ffprobe.exe"


@dataclass
class QualityReport:
    """质量报告"""
    file_path: str
    exists: bool = False
    file_size: int = 0
    duration: float = 0.0
    width: int = 0
    height: int = 0
    fps: float = 0.0
    codec: str = ""
    bitrate: int = 0
    has_alpha: bool = False
    has_audio: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    passed: bool = True


class QualityChecker:
    """Remotion输出质量检测工具"""

    def __init__(self, ffprobe_path: str = None):
        self.ffprobe = ffprobe_path or FFPROBE

    def check_file(self, file_path: str) -> QualityReport:
        """检测输出文件质量

        Args:
            file_path: 文件路径

        Returns:
            质量报告
        """
        report = QualityReport(file_path=file_path)

        # 检查文件存在
        if not os.path.exists(file_path):
            report.errors.append(f"文件不存在: {file_path}")
            report.passed = False
            return report
        report.exists = True
        report.file_size = os.path.getsize(file_path)

        # 检查文件大小
        if report.file_size < 1024:  # 小于1KB
            report.errors.append("文件过小，可能渲染失败")
            report.passed = False

        # 使用ffprobe检测
        try:
            result = subprocess.run(
                [self.ffprobe, "-v", "quiet", "-print_format", "json",
                 "-show_format", "-show_streams", file_path],
                capture_output=True, text=True, timeout=30
            )
            info = json.loads(result.stdout)

            # 格式信息
            fmt = info.get("format", {})
            report.duration = float(fmt.get("duration", 0))
            report.bitrate = int(fmt.get("bit_rate", 0))

            # 流信息
            for stream in info.get("streams", []):
                if stream.get("codec_type") == "video":
                    report.width = stream.get("width", 0)
                    report.height = stream.get("height", 0)
                    report.codec = stream.get("codec_name", "")

                    # 帧率
                    fps_str = stream.get("r_frame_rate", "0/1")
                    if "/" in fps_str:
                        num, den = fps_str.split("/")
                        report.fps = float(num) / float(den) if float(den) != 0 else 0
                    else:
                        report.fps = float(fps_str)

                    # Alpha通道检测
                    pix_fmt = stream.get("pix_fmt", "")
                    report.has_alpha = any(x in pix_fmt for x in ["rgba", "yuva", "argb", "abgr"])

                    # 检查分辨率
                    if report.width == 0 or report.height == 0:
                        report.errors.append("分辨率为0")
                        report.passed = False

                    # 检查帧率
                    if report.fps < 1:
                        report.warnings.append("帧率异常低")

                elif stream.get("codec_type") == "audio":
                    report.has_audio = True

        except FileNotFoundError:
            report.warnings.append("ffprobe未找到，跳过详细检测")
        except Exception as e:
            report.warnings.append(f"ffprobe检测失败: {e}")

        # 检查时长
        if report.duration == 0 and report.exists:
            report.errors.append("视频时长为0")
            report.passed = False

        return report

    def check_alpha_channel(self, file_path: str) -> bool:
        """检测Alpha通道

        Args:
            file_path: 文件路径

        Returns:
            True有Alpha通道
        """
        report = self.check_file(file_path)
        return report.has_alpha

    def check_resolution(
        self,
        file_path: str,
        expected_width: int,
        expected_height: int,
    ) -> Tuple[bool, str]:
        """检测分辨率是否匹配

        Args:
            file_path: 文件路径
            expected_width: 期望宽度
            expected_height: 期望高度

        Returns:
            (是否匹配, 消息)
        """
        report = self.check_file(file_path)
        if report.width == expected_width and report.height == expected_height:
            return True, f"分辨率匹配: {report.width}x{report.height}"
        return False, f"分辨率不匹配: 期望{expected_width}x{expected_height}, 实际{report.width}x{report.height}"

    def check_fps(self, file_path: str, expected_fps: float = 30.0) -> Tuple[bool, str]:
        """检测帧率是否匹配

        Args:
            file_path: 文件路径
            expected_fps: 期望帧率

        Returns:
            (是否匹配, 消息)
        """
        report = self.check_file(file_path)
        if abs(report.fps - expected_fps) < 0.5:
            return True, f"帧率匹配: {report.fps:.1f}fps"
        return False, f"帧率不匹配: 期望{expected_fps}fps, 实际{report.fps:.1f}fps"

    def batch_check(self, directory: str, pattern: str = "*.mp4") -> List[QualityReport]:
        """批量检测目录中的文件

        Args:
            directory: 目录路径
            pattern: 文件匹配模式

        Returns:
            质量报告列表
        """
        import glob
        reports = []
        files = glob.glob(os.path.join(directory, pattern))

        for file_path in files:
            report = self.check_file(file_path)
            reports.append(report)

        return reports

    def generate_report(self, reports: List[QualityReport], output_path: str) -> bool:
        """生成质量检测报告

        Args:
            reports: 质量报告列表
            output_path: 输出路径

        Returns:
            True成功，False失败
        """
        passed = sum(1 for r in reports if r.passed)
        failed = len(reports) - passed

        report_data = {
            "summary": {
                "total": len(reports),
                "passed": passed,
                "failed": failed,
                "pass_rate": f"{passed / len(reports) * 100:.1f}%" if reports else "0%",
            },
            "details": [
                {
                    "file": os.path.basename(r.file_path),
                    "passed": r.passed,
                    "resolution": f"{r.width}x{r.height}",
                    "fps": r.fps,
                    "duration": r.duration,
                    "codec": r.codec,
                    "has_alpha": r.has_alpha,
                    "errors": r.errors,
                    "warnings": r.warnings,
                }
                for r in reports
            ],
        }

        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            logger.info(f"质量报告已生成: {output_path}")
            return True
        except Exception as e:
            logger.error(f"生成质量报告失败: {e}")
            return False

    def print_report(self, report: QualityReport):
        """打印质量报告"""
        status = "✅ 通过" if report.passed else "❌ 失败"
        print(f"\n{'='*50}")
        print(f"文件: {os.path.basename(report.file_path)}")
        print(f"状态: {status}")
        print(f"大小: {report.file_size / 1024 / 1024:.2f} MB")
        print(f"分辨率: {report.width}x{report.height}")
        print(f"帧率: {report.fps:.1f} fps")
        print(f"时长: {report.duration:.2f}s")
        print(f"编码: {report.codec}")
        print(f"Alpha通道: {'是' if report.has_alpha else '否'}")
        print(f"音频: {'有' if report.has_audio else '无'}")
        if report.errors:
            print(f"错误: {report.errors}")
        if report.warnings:
            print(f"警告: {report.warnings}")


def main():
    """测试质量检测工具"""
    checker = QualityChecker()

    # 测试检测
    test_file = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\test.mp4"
    if os.path.exists(test_file):
        report = checker.check_file(test_file)
        checker.print_report(report)
    else:
        print(f"测试文件不存在: {test_file}")
        print("质量检测工具就绪，请指定要检测的文件")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
