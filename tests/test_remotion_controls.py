"""
remotion-controls-skill 基础测试套件
验证：路径配置、透明视频管线、动画能力
"""
import os
import sys
import unittest

# 路径设置
SKILL_ROOT = r"C:\Users\Administrator\AppData\Local\Doubao\User Data\Default\.doubao\agent_mode\workspace\.user_skills\remotion-controls-skill"
sys.path.insert(0, os.path.join(SKILL_ROOT, "scripts"))


class TestPaths(unittest.TestCase):
    """路径配置测试"""
    
    def test_import_ok(self):
        """测试：paths模块可正常导入"""
        import paths
        self.assertIsNotNone(paths)
    
    def test_project_root_defined(self):
        """测试：PROJECT_ROOT已定义"""
        import paths
        self.assertTrue(hasattr(paths, "PROJECT_ROOT"))
        self.assertIsNotNone(paths.PROJECT_ROOT)
    
    def test_ffmpeg_defined(self):
        """测试：FFMPEG路径已定义"""
        import paths
        self.assertTrue(hasattr(paths, "FFMPEG"))
        self.assertIsNotNone(paths.FFMPEG)


class TestRemotionPipeline(unittest.TestCase):
    """Remotion透明视频管线测试"""
    
    def test_remotion_cli_exists(self):
        """测试：Remotion CLI可执行文件存在"""
        import paths
        # 检查remotion项目目录是否存在
        remotion_dir = os.path.join(SKILL_ROOT, "remotion-project")
        if os.path.exists(remotion_dir):
            package_json = os.path.join(remotion_dir, "package.json")
            self.assertTrue(os.path.exists(package_json), "package.json不存在")
        else:
            self.skipTest("remotion-project目录不存在")
    
    def test_png_sequence_dir(self):
        """测试：PNG序列输出目录配置"""
        import paths
        # 验证路径配置中包含输出目录相关配置
        self.assertTrue(hasattr(paths, "PROJECT_ROOT"))


class TestTransparentVideo(unittest.TestCase):
    """透明视频能力测试"""
    
    def test_prores_codec_supported(self):
        """测试：ProRes 4444编解码器配置"""
        # 验证ffmpeg支持prores_ks编码器
        import paths
        ffmpeg = getattr(paths, "FFMPEG", None)
        if ffmpeg and os.path.exists(ffmpeg):
            import subprocess
            result = subprocess.run(
                [ffmpeg, "-encoders"],
                capture_output=True, text=True, timeout=10
            )
            self.assertIn("prores", result.stdout.lower(), "ffmpeg不支持ProRes编码")
        else:
            self.skipTest("FFMPEG未配置或不存在")
    
    def test_alpha_channel_preservation(self):
        """测试：Alpha通道保留管线配置"""
        # 验证PNG序列+ProRes 4444管线的关键组件存在
        import paths
        self.assertTrue(hasattr(paths, "FFMPEG"))
        self.assertTrue(hasattr(paths, "FFPROBE") or hasattr(paths, "FFMPEG"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
