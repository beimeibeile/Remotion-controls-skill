"""
Remotion素材管理器
- 素材导入
- 素材分类
- 素材预览
- 素材路径管理
- 素材元数据
"""

import os
import sys
import logging
import json
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class AssetInfo:
    """素材信息"""
    name: str
    path: str
    asset_type: str  # image/video/audio/font/svg
    width: int = 0
    height: int = 0
    duration: float = 0.0
    size_bytes: int = 0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AssetManager:
    """Remotion素材管理器"""

    SUPPORTED_IMAGE = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
    SUPPORTED_VIDEO = {".mp4", ".webm", ".mov", ".avi"}
    SUPPORTED_AUDIO = {".mp3", ".wav", ".ogg", ".m4a", ".flac"}
    SUPPORTED_FONT = {".ttf", ".otf", ".woff", ".woff2"}

    def __init__(self, asset_root: str = None):
        self.asset_root = asset_root or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets"
        )
        self.assets: Dict[str, AssetInfo] = {}
        self._ensure_dirs()

    def _ensure_dirs(self):
        """确保素材目录存在"""
        for subdir in ["images", "videos", "audio", "fonts", "svg"]:
            os.makedirs(os.path.join(self.asset_root, subdir), exist_ok=True)

    def scan_directory(self, directory: str = None, asset_type: str = None) -> List[AssetInfo]:
        """扫描目录中的素材

        Args:
            directory: 目录路径（默认asset_root）
            asset_type: 过滤类型

        Returns:
            素材列表
        """
        directory = directory or self.asset_root
        results = []

        if not os.path.exists(directory):
            logger.warning(f"目录不存在: {directory}")
            return results

        for root, dirs, files in os.walk(directory):
            for filename in files:
                ext = os.path.splitext(filename)[1].lower()
                path = os.path.join(root, filename)

                if ext in self.SUPPORTED_IMAGE:
                    a_type = "image"
                elif ext in self.SUPPORTED_VIDEO:
                    a_type = "video"
                elif ext in self.SUPPORTED_AUDIO:
                    a_type = "audio"
                elif ext in self.SUPPORTED_FONT:
                    a_type = "font"
                else:
                    continue

                if asset_type and a_type != asset_type:
                    continue

                try:
                    size = os.path.getsize(path)
                except Exception:
                    size = 0

                asset = AssetInfo(
                    name=filename,
                    path=path,
                    asset_type=a_type,
                    size_bytes=size,
                )
                results.append(asset)
                self.assets[filename] = asset

        logger.info(f"扫描到 {len(results)} 个素材")
        return results

    def import_asset(
        self,
        source_path: str,
        asset_type: str = None,
        new_name: str = None,
    ) -> Optional[AssetInfo]:
        """导入素材到素材库

        Args:
            source_path: 源文件路径
            asset_type: 素材类型（自动检测）
            new_name: 新文件名

        Returns:
            素材信息，失败返回None
        """
        if not os.path.exists(source_path):
            logger.error(f"源文件不存在: {source_path}")
            return None

        ext = os.path.splitext(source_path)[1].lower()
        if not asset_type:
            if ext in self.SUPPORTED_IMAGE:
                asset_type = "image"
            elif ext in self.SUPPORTED_VIDEO:
                asset_type = "video"
            elif ext in self.SUPPORTED_AUDIO:
                asset_type = "audio"
            elif ext in self.SUPPORTED_FONT:
                asset_type = "font"
            else:
                logger.error(f"不支持的素材格式: {ext}")
                return None

        target_dir = os.path.join(self.asset_root, f"{asset_type}s")
        filename = new_name or os.path.basename(source_path)
        target_path = os.path.join(target_dir, filename)

        try:
            import shutil
            shutil.copy2(source_path, target_path)
            size = os.path.getsize(target_path)

            asset = AssetInfo(
                name=filename,
                path=target_path,
                asset_type=asset_type,
                size_bytes=size,
            )
            self.assets[filename] = asset
            logger.info(f"导入素材: {filename} -> {target_path}")
            return asset
        except Exception as e:
            logger.error(f"导入素材失败: {e}")
            return None

    def get_asset(self, name: str) -> Optional[AssetInfo]:
        """获取素材信息"""
        return self.assets.get(name)

    def list_assets(self, asset_type: str = None) -> List[AssetInfo]:
        """列出素材

        Args:
            asset_type: 过滤类型

        Returns:
            素材列表
        """
        if asset_type:
            return [a for a in self.assets.values() if a.asset_type == asset_type]
        return list(self.assets.values())

    def generate_import_statements(self, assets: List[AssetInfo] = None) -> str:
        """生成Remotion导入语句

        Args:
            assets: 素材列表（默认全部）

        Returns:
            导入语句代码
        """
        assets = assets or list(self.assets.values())
        statements = []

        for asset in assets:
            var_name = os.path.splitext(asset.name)[0].replace(" ", "_").replace("-", "_")
            if asset.asset_type == "image":
                statements.append(f"import {var_name} from '{asset.path}';")
            elif asset.asset_type == "video":
                statements.append(f"import {var_name} from '{asset.path}';")
            elif asset.asset_type == "audio":
                statements.append(f"import {var_name} from '{asset.path}';")
            elif asset.asset_type == "font":
                statements.append(f"// Font: {asset.name} ({asset.path})")

        return "\n".join(statements)

    def export_manifest(self, output_path: str) -> bool:
        """导出素材清单

        Args:
            output_path: 输出路径

        Returns:
            True成功，False失败
        """
        manifest = {
            "asset_root": self.asset_root,
            "total_count": len(self.assets),
            "assets": [
                {
                    "name": a.name,
                    "path": a.path,
                    "type": a.asset_type,
                    "width": a.width,
                    "height": a.height,
                    "duration": a.duration,
                    "size_bytes": a.size_bytes,
                    "tags": a.tags,
                }
                for a in self.assets.values()
            ],
        }

        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            logger.info(f"素材清单已导出: {output_path}")
            return True
        except Exception as e:
            logger.error(f"导出素材清单失败: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """获取素材库统计"""
        stats = {
            "total": len(self.assets),
            "by_type": {},
            "total_size": 0,
        }
        for asset in self.assets.values():
            stats["by_type"][asset.asset_type] = stats["by_type"].get(asset.asset_type, 0) + 1
            stats["total_size"] += asset.size_bytes
        return stats


def main():
    """测试素材管理器"""
    manager = AssetManager()

    # 扫描素材
    assets = manager.scan_directory()
    print(f"扫描到 {len(assets)} 个素材")

    # 统计
    stats = manager.get_stats()
    print(f"\n素材库统计:")
    print(f"  总数: {stats['total']}")
    print(f"  总大小: {stats['total_size'] / 1024 / 1024:.2f} MB")
    for t, count in stats["by_type"].items():
        print(f"  {t}: {count}")

    # 生成导入语句
    if assets:
        print(f"\n导入语句示例:")
        print(manager.generate_import_statements(assets[:3]))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
