---
name: remotion-controls-skill
description: Remotion 代码驱动视频动画专业控制技能。用 React/TypeScript 代码精确控制2D动画，原生支持透明背景(Alpha通道)渲染，可输出WebM/MOV带透明通道视频，适用于剪映模板动画素材制作、UI动画、文字排版动画、角色2D动画等场景。提供API服务化、模板库、质量控制和自学习进化能力。
version: 1.0.0
authors:
  - Remotion Controls Team
---

# Remotion Controls Skill

用代码驱动视频动画的专业控制技能。Remotion 是一个基于 React 的视频创作框架，用代码精确控制每一帧，原生支持透明背景渲染。

## 姊妹项目（8姊妹skill）

| 项目 | 定位 | 角色 |
|------|------|------|
| **ai-video-editor** | AI视频剪辑框架（大脑/集成平台） | 🚢 航空母舰 |
| **jianying-editor** | 剪映工程控制 | ✂️ 剪辑底层 |
| **Pr-controls-skill** | Pr工程控制 | 🎬 专业剪辑 |
| **Ps-controls-skill** | Photoshop控制 | 🖼️ 图像处理 |
| **Comfyui-controls-skill** | ComfyUI智能管理 | 🚀 AI算力 |
| **Blender-controls-skill** | Blender智能管理 | 🎨 3D特效 |
| **remotion-controls-skill** | Remotion代码动画（本项目） | 💻 代码动画 |
| **anysearch-skill** | 深度搜索 | 📡 情报搜索 |

> 单体都能干活，任意组合互相增强。能力注册中心v3.2统一调度，智能路由选择最佳skill。

## 核心能力（模块下沉后）

本skill已接收ai-video-editor下沉的2个代码动画模块，具备完整独立工作能力：

- **Remotion执行器**：remotion_executor（PNG序列+ffmpeg ProRes 4444管线，Alpha通道保留）
- **动画渲染适配器**：animation_render_adapter
- **透明背景管线**：PNG序列 → ProRes 4444，适用于剪映模板动画素材

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

## 透明背景渲染说明（已验证流程）

Remotion 原生支持透明背景，但 **CLI 的 `--transparent` 编码会丢失 Alpha 通道**（WebM VP8/VP9、MOV ProRes 均验证失败）。

**已验证的正确流程（PIT-024）：**

1. **PNG序列渲染**：`npx remotion render src/index.ts Composition out/frames --sequence`（输出带Alpha的PNG序列）
2. **ffmpeg合成ProRes 4444**：
   ```bash
   ffmpeg -y -framerate 30 -i out/frames/%04d.png \
     -c:v prores_ks -profile:v 4 -pix_fmt yuva444p12le \
     out/animation.mov
   ```
3. **验证Alpha通道**：`python verify_animation.py out/animation.mov`

**剪映集成注意事项（PIT-024）：**
- `add_media_safe` 导入 ProRes 4444 mov 时会自动转码为 H.264 mp4，**丢失Alpha**（66MB→0.07MB）
- 必须**手动导入**：直接复制 mov 到草稿 materials 目录 → 创建 VideoMaterial → 注册到 materials.videos → VideoSegment(material=anim_material) → add_segment

## 动画素材质量标准

完整标准见 [QUALITY_STANDARD.md](QUALITY_STANDARD.md)。

**合格动画素材的硬性指标：**
- Alpha通道保留（yuva444p12le）
- ProRes 4444 编码（profile=4）
- 分辨率/帧率/时长与配置一致
- 内容覆盖率 ≥ 50%（10点采样）
- 文件大小合理（≤15MB/秒）

**自动化验证：**
```bash
python verify_animation.py <动画文件> --duration 20 --width 1080 --height 1920
```

## 基础动画组件库

位于 `remotion-project/src/components/`，所有组件均支持透明背景。

### 角色与运动组件

| 组件 | 说明 |
|------|------|
| **CharacterSprite** | 角色精灵：多姿态切换、位置/缩放/旋转/透明度关键帧动画 |
| **MotionPath** | 运动路径：线性/贝塞尔/弹性/弹跳运动 |
| **FlashEffect** | 闪白特效：快速淡入缓慢淡出 |
| **ShakeEffect** | 震动特效：振幅衰减的随机震动 |
| **FadeEffect** | 淡入淡出：可控淡入/淡出时长 |
| **PopEffect** | 弹出特效：弹性缩放弹出 |
| **SlideEffect** | 滑动特效：四方向缓出滑动 |

### 文字动画组件（TextAnimations.tsx）

| 组件 | 说明 | 适用场景 |
|------|------|---------|
| **TextReveal** | 逐字显现：打字机/淡入/上滑/左滑 | 旁白、台词、标题入场 |
| **TextPop** | 弹出文字：缩放/旋转/弹跳 | 关键词强调、卡点 |
| **TextWave** | 波浪文字：逐字正弦浮动 | 趣味风格、背景音乐节奏 |
| **TextGlitch** | 故障风：RGB分离+抖动 | 科技感、故障艺术、转场 |
| **TextGradient** | 渐变流光：颜色流动+扫光 | 标题、品牌名、高级感 |
| **KineticText** | 动态排版：多行组合动画 | 开场标题、片尾字幕 |

### 转场特效组件（TransitionEffects.tsx）

| 组件 | 说明 | 适用场景 |
|------|------|---------|
| **FadeTransition** | 淡入淡出转场（in/out/inOut） | 通用转场、情绪过渡 |
| **SlideTransition** | 滑动转场（上下左右） | 场景切换、内容替换 |
| **ZoomTransition** | 缩放转场（推近/拉远） | 强调重点、镜头推进 |
| **WipeTransition** | 擦除转场（上下左右/对角线） | 创意转场、风格化 |
| **BlurTransition** | 模糊转场（先模糊后清晰） | 梦幻过渡、回忆闪回 |
| **GlitchTransition** | 故障风转场（RGB分离+扫描线） | 科技感、故障艺术 |

### 冲击特效组件（ImpactEffects.tsx）

| 组件 | 说明 | 适用场景 |
|------|------|---------|
| **PunchImpact** | 拳击冲击（冲击波+星星+白闪） | 打斗、击打、碰撞 |
| **ImpactFlash** | 冲击闪光（快速白闪） | 重击、爆炸、卡点 |
| **ParticleBurst** | 粒子爆发（星星/火花/碎片） | 庆祝、爆炸、冲击 |
| **Shockwave** | 冲击波（多环扩散） | 能量释放、爆炸、震感 |
| **SpeedLines** | 速度线（放射状） | 高速冲击、冲刺、连击 |

**使用示例：**
```tsx
import { PunchImpact, ParticleBurst, FadeTransition } from "./components";

// 打斗场景
<PunchImpact startFrame={90} x={540} y={800} scale={1.2} />
<ParticleBurst startFrame={90} x={540} y={800} count={16} particleType="star" />
<FadeTransition direction="in" duration={15} startFrame={0} color="#1a1a2e" />
```

**使用示例：**
```tsx
import { CharacterSprite, FlashEffect, TextReveal, TextPop } from "./components";

<CharacterSprite
  poses={[
    { name: "idle", image: "/doubao_normal.png", frameRange: [0, 90],
      position: [{frame: 0, x: 0, y: 0}, {frame: 90, x: 100, y: 0}] },
    { name: "falling", image: "/doubao_falling.png", frameRange: [90, 150] },
  ]}
  width={250} height={250}
/>
<FlashEffect startFrame={90} duration={10} />
<TextReveal text="被打了!" fontSize={56} startFrame={95} revealType="typewriter" />
<TextPop text="痛!" fontSize={72} color="#ff6b6b" startFrame={110} popType="bounce" />
```

## 项目结构

```
remotion-controls-skill/
├── SKILL.md                    # 本文件
├── QUALITY_STANDARD.md         # 动画素材质量标准
├── verify_animation.py         # 自动化验证工具
├── remotion_controls.py        # 主控制脚本（CLI/API）
├── .env.example                # 环境变量示例
├── .gitignore
├── capabilities/
│   ├── cap_api_wrapper/        # Remotion API 封装
│   ├── cap_animation_renderer/ # 动画渲染器
│   ├── cap_template_library/   # 动画模板库
│   ├── cap_quality_control/    # 质量控制
│   └── cap_self_evolution/     # 自学习进化
├── remotion-project/           # Remotion 项目
│   ├── src/
│   │   ├── components/         # 基础动画组件库
│   │   │   ├── CharacterSprite.tsx
│   │   │   ├── MotionPath.tsx
│   │   │   ├── Effects.tsx
│   │   │   └── index.ts
│   │   ├── AnimationTemplate.tsx  # JSON驱动的动画模板
│   │   ├── Root.tsx
│   │   └── index.ts
│   ├── public/                 # 静态素材（角色/道具图片）
│   └── package.json
└── out/                        # 渲染输出
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
