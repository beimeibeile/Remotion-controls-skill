"""
Remotion合成构建器
- 合成配置管理
- 多图层组合
- 时间线编排
- 组件注册
- 项目结构生成
"""

import os
import sys
import logging
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class LayerConfig:
    """图层配置"""
    name: str
    component: str  # 组件名
    start_frame: int = 0
    duration: int = 60
    props: Dict[str, Any] = field(default_factory=dict)
    z_index: int = 0


@dataclass
class CompositionConfig:
    """合成配置"""
    name: str = "MyComposition"
    width: int = 1920
    height: int = 1080
    fps: int = 30
    duration_in_frames: int = 180
    background_color: str = "#000000"
    layers: List[LayerConfig] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)


class CompositionBuilder:
    """Remotion合成构建器"""

    def __init__(self):
        self.compositions: Dict[str, CompositionConfig] = {}

    def create_composition(
        self,
        name: str,
        width: int = 1920,
        height: int = 1080,
        fps: int = 30,
        duration: int = 180,
        background_color: str = "#000000",
    ) -> CompositionConfig:
        """创建新合成

        Args:
            name: 合成名
            width: 宽度
            height: 高度
            fps: 帧率
            duration: 时长（帧）
            background_color: 背景色

        Returns:
            合成配置
        """
        comp = CompositionConfig(
            name=name,
            width=width,
            height=height,
            fps=fps,
            duration_in_frames=duration,
            background_color=background_color,
        )
        self.compositions[name] = comp
        logger.info(f"创建合成: {name} ({width}x{height}, {fps}fps, {duration}帧)")
        return comp

    def add_layer(
        self,
        composition_name: str,
        layer_name: str,
        component: str,
        start_frame: int = 0,
        duration: int = 60,
        props: Dict[str, Any] = None,
        z_index: int = 0,
    ) -> bool:
        """添加图层到合成

        Args:
            composition_name: 合成名
            layer_name: 图层名
            component: 组件名
            start_frame: 起始帧
            duration: 时长
            props: 属性
            z_index: 层级

        Returns:
            True成功，False失败
        """
        comp = self.compositions.get(composition_name)
        if not comp:
            logger.error(f"合成不存在: {composition_name}")
            return False

        layer = LayerConfig(
            name=layer_name,
            component=component,
            start_frame=start_frame,
            duration=duration,
            props=props or {},
            z_index=z_index,
        )
        comp.layers.append(layer)
        logger.info(f"添加图层: {layer_name} -> {composition_name} (帧{start_frame}-{start_frame + duration})")
        return True

    def add_import(self, composition_name: str, import_path: str) -> bool:
        """添加组件导入

        Args:
            composition_name: 合成名
            import_path: 导入路径

        Returns:
            True成功，False失败
        """
        comp = self.compositions.get(composition_name)
        if not comp:
            return False
        if import_path not in comp.imports:
            comp.imports.append(import_path)
        return True

    def generate_composition_code(
        self,
        composition_name: str,
        output_path: str,
    ) -> str:
        """生成合成组件代码

        Args:
            composition_name: 合成名
            output_path: 输出路径

        Returns:
            生成的文件路径
        """
        comp = self.compositions.get(composition_name)
        if not comp:
            logger.error(f"合成不存在: {composition_name}")
            return ""

        # 生成导入语句
        imports_code = ""
        for imp in comp.imports:
            imports_code += f"import {{ {imp.split('/')[-1].replace('.tsx', '').replace('.ts', '')} }} from '{imp}';\n"

        # 生成图层渲染代码
        layers_code = ""
        for layer in sorted(comp.layers, key=lambda l: l.z_index):
            props_str = ", ".join([f"{k}={v}" for k, v in layer.props.items()])
            layers_code += f"""
        {{frame >= {layer.start_frame} && frame < {layer.start_frame + layer.duration} && (
          <{layer.component} {props_str} />
        )}}
"""

        component_code = f"""import React from 'react';
import {{ AbsoluteFill, useCurrentFrame, Sequence }} from 'remotion';
{imports_code}
// 合成: {comp.name}
// 尺寸: {comp.width}x{comp.height}
// 帧率: {comp.fps}fps
// 时长: {comp.duration_in_frames}帧
// 图层数: {len(comp.layers)}

export const {comp.name}: React.FC = () => {{
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{ backgroundColor: '{comp.background_color}' }}>
{layers_code}
    </AbsoluteFill>
  );
}};
"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(component_code)

        logger.info(f"合成组件已生成: {output_path} ({len(comp.layers)}个图层)")
        return output_path

    def generate_project_structure(
        self,
        output_dir: str,
        project_name: str = "remotion-project",
    ) -> Dict[str, str]:
        """生成完整Remotion项目结构

        Args:
            output_dir: 输出目录
            project_name: 项目名

        Returns:
            生成的文件路径字典
        """
        files = {}

        # package.json
        package_json = {
            "name": project_name,
            "version": "1.0.0",
            "scripts": {
                "start": "remotion studio",
                "build": "remotion render",
                "upgrade": "remotion upgrade",
            },
            "dependencies": {
                "react": "^18.0.0",
                "react-dom": "^18.0.0",
                "remotion": "^4.0.0",
                "@remotion/cli": "^4.0.0",
                "@remotion/bundler": "^4.0.0",
                "@remotion/renderer": "^4.0.0",
            },
            "devDependencies": {
                "typescript": "^5.0.0",
                "@types/react": "^18.0.0",
            },
        }

        files["package.json"] = os.path.join(output_dir, "package.json")
        with open(files["package.json"], "w", encoding="utf-8") as f:
            import json
            json.dump(package_json, f, indent=2)

        # tsconfig.json
        tsconfig = {
            "compilerOptions": {
                "target": "ES2018",
                "module": "commonjs",
                "jsx": "react-jsx",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "outDir": "./dist",
                "rootDir": "./src",
            },
            "include": ["src/**/*"],
        }
        files["tsconfig.json"] = os.path.join(output_dir, "tsconfig.json")
        with open(files["tsconfig.json"], "w", encoding="utf-8") as f:
            import json
            json.dump(tsconfig, f, indent=2)

        # src/index.ts
        index_code = """import { registerRoot } from 'remotion';
import { RemotionRoot } from './Root';

registerRoot(RemotionRoot);
"""
        files["src/index.ts"] = os.path.join(output_dir, "src", "index.ts")
        os.makedirs(os.path.dirname(files["src/index.ts"]), exist_ok=True)
        with open(files["src/index.ts"], "w", encoding="utf-8") as f:
            f.write(index_code)

        # src/Root.tsx
        root_code = """import React from 'react';
import { Composition } from 'remotion';
import { MyComposition } from './compositions/MyComposition';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="MyComposition"
        component={MyComposition}
        durationInFrames={180}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
"""
        files["src/Root.tsx"] = os.path.join(output_dir, "src", "Root.tsx")
        with open(files["src/Root.tsx"], "w", encoding="utf-8") as f:
            f.write(root_code)

        # src/compositions/MyComposition.tsx
        comp_code = """import React from 'react';
import { AbsoluteFill } from 'remotion';

export const MyComposition: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: '#000', justifyContent: 'center', alignItems: 'center' }}>
      <h1 style={{ color: '#fff', fontSize: 72 }}>Hello Remotion</h1>
    </AbsoluteFill>
  );
};
"""
        files["src/compositions/MyComposition.tsx"] = os.path.join(output_dir, "src", "compositions", "MyComposition.tsx")
        os.makedirs(os.path.dirname(files["src/compositions/MyComposition.tsx"]), exist_ok=True)
        with open(files["src/compositions/MyComposition.tsx"], "w", encoding="utf-8") as f:
            f.write(comp_code)

        # remotion.config.ts
        config_code = """import { Config } from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
"""
        files["remotion.config.ts"] = os.path.join(output_dir, "remotion.config.ts")
        with open(files["remotion.config.ts"], "w", encoding="utf-8") as f:
            f.write(config_code)

        logger.info(f"项目结构已生成: {output_dir} ({len(files)}个文件)")
        return files

    def list_compositions(self) -> List[str]:
        """列出所有合成"""
        return list(self.compositions.keys())


def main():
    """测试合成构建器"""
    builder = CompositionBuilder()

    # 创建合成
    comp = builder.create_composition(
        name="IntroAnimation",
        width=1920,
        height=1080,
        fps=30,
        duration=180,
        background_color="#1a1a2e",
    )

    # 添加图层
    builder.add_layer("IntroAnimation", "Background", "BackgroundLayer", 0, 180)
    builder.add_layer("IntroAnimation", "Title", "TitleText", 30, 90, z_index=1)
    builder.add_layer("IntroAnimation", "Particles", "ParticleEffect", 0, 180, z_index=2)

    # 生成合成代码
    output = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\remotion\IntroAnimation.tsx"
    path = builder.generate_composition_code("IntroAnimation", output)
    print(f"生成合成: {path}")

    # 生成项目结构
    project_dir = r"D:\DobaoWork_Project\Ai_Video_Editor\test_output\remotion\demo-project"
    files = builder.generate_project_structure(project_dir, "demo-project")
    print(f"\n生成项目结构: {project_dir}")
    for name, path in files.items():
        print(f"  - {name}: {path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
