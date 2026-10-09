"""
Remotion模板导出工具
- 模板打包
- 模板元数据
- 模板版本管理
- 模板导出/导入
- 模板市场格式
"""

import os
import sys
import logging
import json
import shutil
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class TemplateMeta:
    """模板元数据"""
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    category: str = "general"  # intro/outro/transition/title/overlay/general
    tags: List[str] = field(default_factory=list)
    duration: int = 60
    width: int = 1920
    height: int = 1080
    fps: int = 30
    dependencies: List[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


class TemplateExporter:
    """Remotion模板导出工具"""

    def __init__(self):
        self.templates: Dict[str, TemplateMeta] = {}

    def create_template(
        self,
        name: str,
        source_dir: str,
        output_dir: str,
        description: str = "",
        category: str = "general",
        tags: List[str] = None,
        version: str = "1.0.0",
    ) -> Optional[str]:
        """创建模板包

        Args:
            name: 模板名
            source_dir: 源目录
            output_dir: 输出目录
            description: 描述
            category: 分类
            tags: 标签
            version: 版本

        Returns:
            模板包路径，失败返回None
        """
        if not os.path.exists(source_dir):
            logger.error(f"源目录不存在: {source_dir}")
            return None

        # 创建模板目录
        template_dir = os.path.join(output_dir, f"{name}_v{version}")
        os.makedirs(template_dir, exist_ok=True)

        # 复制源文件
        src_files = []
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.endswith((".tsx", ".ts", ".jsx", ".js", ".json", ".css")):
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, source_dir)
                    dst_path = os.path.join(template_dir, rel_path)
                    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                    shutil.copy2(src_path, dst_path)
                    src_files.append(rel_path)

        # 创建元数据
        now = datetime.now().isoformat()
        meta = TemplateMeta(
            name=name,
            version=version,
            description=description,
            category=category,
            tags=tags or [],
            created_at=now,
            updated_at=now,
        )

        meta_path = os.path.join(template_dir, "template.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({
                "name": meta.name,
                "version": meta.version,
                "description": meta.description,
                "author": meta.author,
                "category": meta.category,
                "tags": meta.tags,
                "duration": meta.duration,
                "width": meta.width,
                "height": meta.height,
                "fps": meta.fps,
                "dependencies": meta.dependencies,
                "created_at": meta.created_at,
                "updated_at": meta.updated_at,
                "files": src_files,
            }, f, indent=2, ensure_ascii=False)

        # 创建README
        readme_path = os.path.join(template_dir, "README.md")
        readme = f"""# {name}

{description}

## 信息

- **版本**: {version}
- **分类**: {category}
- **标签**: {', '.join(tags or [])}
- **尺寸**: {meta.width}x{meta.height}
- **帧率**: {meta.fps}fps
- **创建时间**: {now}

## 文件

{chr(10).join(f'- {f}' for f in src_files)}

## 使用

```tsx
import {{ {name} }} from './{name}';

<{name} />
```
"""
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme)

        self.templates[name] = meta
        logger.info(f"模板已创建: {template_dir} ({len(src_files)}个文件)")
        return template_dir

    def export_template_zip(
        self,
        template_dir: str,
        output_path: str,
    ) -> Optional[str]:
        """导出模板为ZIP包

        Args:
            template_dir: 模板目录
            output_path: 输出ZIP路径

        Returns:
            ZIP路径，失败返回None
        """
        if not os.path.exists(template_dir):
            logger.error(f"模板目录不存在: {template_dir}")
            return None

        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            shutil.make_archive(
                output_path.replace(".zip", ""),
                "zip",
                template_dir
            )
            logger.info(f"模板已导出: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"导出模板失败: {e}")
            return None

    def import_template(
        self,
        template_path: str,
        extract_dir: str,
    ) -> Optional[TemplateMeta]:
        """导入模板

        Args:
            template_path: 模板ZIP路径或目录
            extract_dir: 解压目录

        Returns:
            模板元数据，失败返回None
        """
        try:
            if template_path.endswith(".zip"):
                shutil.unpack_archive(template_path, extract_dir)
                template_dir = extract_dir
            else:
                template_dir = template_path

            # 读取元数据
            meta_path = os.path.join(template_dir, "template.json")
            if os.path.exists(meta_path):
                with open(meta_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                meta = TemplateMeta(
                    name=data.get("name", "Unknown"),
                    version=data.get("version", "1.0.0"),
                    description=data.get("description", ""),
                    category=data.get("category", "general"),
                    tags=data.get("tags", []),
                )
                self.templates[meta.name] = meta
                logger.info(f"模板已导入: {meta.name} v{meta.version}")
                return meta
            else:
                logger.warning("模板元数据不存在")
                return None
        except Exception as e:
            logger.error(f"导入模板失败: {e}")
            return None

    def list_templates(self, category: str = None) -> List[TemplateMeta]:
        """列出模板

        Args:
            category: 分类过滤

        Returns:
            模板列表
        """
        if category:
            return [t for t in self.templates.values() if t.category == category]
        return list(self.templates.values())

    def generate_template_index(
        self,
        templates_dir: str,
        output_path: str,
    ) -> bool:
        """生成模板索引

        Args:
            templates_dir: 模板目录
            output_path: 索引输出路径

        Returns:
            True成功，False失败
        """
        index = []
        if os.path.exists(templates_dir):
            for item in os.listdir(templates_dir):
                item_path = os.path.join(templates_dir, item)
                meta_path = os.path.join(item_path, "template.json")
                if os.path.isdir(item_path) and os.path.exists(meta_path):
                    try:
                        with open(meta_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        index.append(data)
                    except Exception:
                        pass

        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump({
                    "total": len(index),
                    "templates": index,
                    "generated_at": datetime.now().isoformat(),
                }, f, indent=2, ensure_ascii=False)
            logger.info(f"模板索引已生成: {output_path} ({len(index)}个模板)")
            return True
        except Exception as e:
            logger.error(f"生成模板索引失败: {e}")
            return False

    def validate_template(self, template_dir: str) -> Tuple[bool, List[str]]:
        """验证模板完整性

        Args:
            template_dir: 模板目录

        Returns:
            (是否有效, 问题列表)
        """
        issues = []

        if not os.path.exists(template_dir):
            issues.append("模板目录不存在")
            return False, issues

        # 检查必需文件
        required_files = ["template.json"]
        for f in required_files:
            if not os.path.exists(os.path.join(template_dir, f)):
                issues.append(f"缺少必需文件: {f}")

        # 检查组件文件
        has_component = False
        for root, dirs, files in os.walk(template_dir):
            for file in files:
                if file.endswith((".tsx", ".jsx")):
                    has_component = True
                    break
        if not has_component:
            issues.append("未找到组件文件(.tsx/.jsx)")

        return len(issues) == 0, issues


def main():
    """测试模板导出工具"""
    exporter = TemplateExporter()

    # 创建测试模板
    source = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\remotion"
    output = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\templates"

    if os.path.exists(source):
        template_dir = exporter.create_template(
            name="TestTemplate",
            source_dir=source,
            output_dir=output,
            description="测试模板",
            category="intro",
            tags=["test", "demo"],
        )
        if template_dir:
            print(f"模板创建成功: {template_dir}")

            # 验证模板
            valid, issues = exporter.validate_template(template_dir)
            print(f"模板验证: {'通过' if valid else '失败'}")
            if issues:
                print(f"问题: {issues}")
    else:
        print(f"源目录不存在: {source}")
        print("模板导出工具就绪")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
