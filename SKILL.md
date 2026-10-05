---
name: remotion-controls-skill
description: Remotion 代码驱动视频动画专业控制技能。用 React/TypeScript 代码精确控制2D动画，原生支持透明背景(Alpha通道)渲染，可输出WebM/MOV带透明通道视频，适用于剪映模板动画素材制作、UI动画、文字排版动画、角色2D动画等场景。提供API服务化、模板库、质量控制和自学习进化能力。
version: 1.0.0
authors:
  - Remotion Controls Team
---

# Remotion Controls Skill

用代码驱动视频动画的专业控制技能。Remotion 是一个基于 React 的视频创作框架，用代码精确控制每一帧，原生支持透明背景渲染。

## 核心能力

| 能力 | 说明 |
|------|------|
| **透明背景渲染** | 原生支持 Alpha 通道，输出 WebM(VP9) / MOV(ProRes 4444) 带透明视频 |
| **代码精确控制** | 用 React/TypeScript 精确控制位置、缩放、旋转、透明度、缓动曲线 |
| **API服务化** | HTTP API 接收动画指令，输出视频文件 |
| **模板库** | 预设动画模板（角色动画、UI动画、文字动画、转场特效） |
| **质量控制** | 帧率、分辨率、码率、Alpha通道完整性自动检测 |
| **自学习进化** | 记录渲染参数与效果评分，优化预设参数 |

## 与 ComfyUI / Blender 的定位差异

| 技能 | 核心优势 | 适用场景 |
|------|---------|---------|
| **ComfyUI-controls** | AI生成（图/视频/音频），创意不可控 | 角色图/场景图/特效视频生成 |
| **Blender-controls** | 3D动画，物理模拟，高质量渲染 | 3D角色动画、产品展示、物理特效 |
| **Remotion-controls** | 2D代码动画，精确可控，透明背景 | 模板动画素材、UI动画、文字排版、2D角色动画 |

## 快速开始

### 1. 安装依赖

```bash
cd remotion-project
npm install
```

### 2. 渲染透明背景视频

```bash
# CLI 方式
npx remotion render src/index.ts MyComp out/video.webm --transparent

# API 方式
python remotion_controls.py render --composition MyComp --output out/video.webm --transparent
```

### 3. 启动 API 服务

```bash
python remotion_controls.py serve --port 8765
```

## 透明背景渲染说明

Remotion 原生支持透明背景，关键配置：

1. **Composition 背景透明**：React 组件根元素不设置背景色，或设置 `background: 'transparent'`
2. **渲染标志**：`--transparent` 或 `renderMedia({ transparent: true })`
3. **输出格式**：
   - WebM (VP9)：文件小，兼容性好，剪映支持
   - MOV (ProRes 4444)：质量高，文件大，专业剪辑软件支持
4. **验证 Alpha**：用 ffprobe 检查输出视频是否包含 Alpha 通道

## 项目结构

```
remotion-controls-skill/
├── SKILL.md                    # 本文件
├── README.md                   # 项目说明
├── remotion_controls.py        # 主控制脚本（CLI/API）
├── .env.example                # 环境变量示例
├── .gitignore
├── capabilities/
│   ├── cap_api_wrapper/        # Remotion API 封装
│   ├── cap_animation_renderer/ # 动画渲染器
│   ├── cap_template_library/   # 动画模板库
│   ├── cap_quality_control/    # 质量控制
│   └── cap_self_evolution/     # 自学习进化
├── templates/                   # Remotion 项目模板
└── examples/                    # 示例动画
```

## 能力模块

### cap_api_wrapper — Remotion API 封装
- `render_media()`：渲染视频（支持透明背景）
- `render_still()`：渲染单帧图片
- `select_composition()`：获取可用 Composition 列表
- `get_props_schema()`：获取 Composition 的 Props 定义

### cap_animation_renderer — 动画渲染器
- 输入动画指令 JSON → 输出透明背景视频
- 支持关键帧动画（位置/缩放/旋转/透明度）
- 支持缓动曲线（ease-in/ease-out/ease-in-out/linear/spring）
- 支持多图层合成

### cap_template_library — 动画模板库
- 角色动画模板（豆包被打、表情切换等）
- UI动画模板（按钮点击、页面切换等）
- 文字动画模板（打字机、淡入淡出、弹跳等）
- 转场特效模板（淡入淡出、滑动、缩放等）

### cap_quality_control — 质量控制
- 帧率检测（24/30/60fps）
- 分辨率检测（1080p/4K）
- Alpha通道完整性检测
- 视频时长与预期对比
- 文件大小合理性检查

### cap_self_evolution — 自学习进化
- 记录渲染参数与效果评分
- 优化预设参数
- 生成最佳实践文档
- 模板效果排行榜

## 环境变量

```env
REMOTION_PROJECT_PATH=./remotion-project
REMOTION_OUTPUT_DIR=./output
REMOTION_DEFAULT_FPS=30
REMOTION_DEFAULT_WIDTH=1080
REMOTION_DEFAULT_HEIGHT=1920
REMOTION_API_PORT=8765
```

## 与 ai-video-editor 的集成

Remotion-controls-skill 作为 ai-video-editor 的动画素材制作工具：

1. ai-video-editor 的导演引擎输出动画指令
2. Remotion-controls-skill 接收指令，渲染透明背景视频
3. 透明背景视频作为剪映模板的动画素材层
4. 用户替换背景后，动画完美叠加

## 注意事项

- Remotion 需要 Node.js 18+ 环境
- 透明背景视频建议使用 WebM 格式（剪映兼容性好）
- 长视频渲染耗时较长，建议分段渲染后合成
- 动画中避免使用 CSS 滤镜（部分滤镜不支持透明背景）
