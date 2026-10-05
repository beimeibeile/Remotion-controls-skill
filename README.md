# Remotion Controls Skill

用代码驱动视频动画的专业控制技能。与 ComfyUI-controls-skill、Blender-controls-skill 并列的第三大垂类技能。

## 核心能力

**透明背景动画渲染** — 这是本技能的核心价值。用 React 代码精确控制多图层关键帧动画，渲染带 Alpha 通道的视频，用于剪映模板的动画层。

### 5 大能力模块

| 模块 | 功能 |
|------|------|
| `cap_api_wrapper` | Remotion API 封装（render/still/list_compositions） |
| `cap_animation_renderer` | 动画渲染器（从 JSON 配置渲染透明背景视频） |
| `cap_template_library` | 动画模板库（预设模板管理） |
| `cap_quality_control` | 质量控制（帧率/分辨率/Alpha通道/时长/文件大小检测） |
| `cap_self_evolution` | 自学习进化（渲染参数记录/最佳实践生成） |

## 快速开始

### 渲染透明背景视频（推荐）

```bash
python remotion_controls.py render-transparent \
  --comp AnimationTemplate \
  --output out/animation.mov \
  --frames 0-600 \
  --props '{"layers": [...]}'
```

输出格式：MOV ProRes 4444 (`yuva444p12le`)，剪映完全兼容，含 Alpha 通道。

### 其他命令

```bash
# 列出所有 Composition
python remotion_controls.py list

# 渲染单帧 PNG（透明）
python remotion_controls.py still --comp AnimationTemplate --output frame.png --transparent

# 检查视频 Alpha 通道
python remotion_controls.py check-alpha --video out/animation.mov

# 从 JSON 配置渲染
python remotion_controls.py render-json --input animation.json --output out.mp4
```

## 动画配置格式

```json
{
  "composition": "AnimationTemplate",
  "fps": 30,
  "width": 1080,
  "height": 1920,
  "duration": 20,
  "layers": [
    {
      "id": "character",
      "image": "character.png",
      "keyframes": [
        {"time": 0, "x": 200, "y": 380, "scale": 0.38, "opacity": 1},
        {"time": 2, "x": 200, "y": 380, "scale": 0.38, "opacity": 1},
        {"time": 3, "x": 540, "y": 960, "scale": 0.5, "opacity": 1, "easing": "ease-in"},
        {"time": 4, "x": 540, "y": 1400, "scale": 0.3, "opacity": 0.8, "easing": "ease-out"}
      ]
    }
  ]
}
```

### 关键帧属性

| 属性 | 说明 | 单位 |
|------|------|------|
| `time` | 时间点 | 秒 |
| `x` | 水平位置（相对画布左上角） | 像素 |
| `y` | 垂直位置 | 像素 |
| `scale` | 缩放比例 | 倍 |
| `opacity` | 透明度 | 0-1 |
| `rotation` | 旋转角度 | 度 |
| `easing` | 缓动曲线 | linear/ease-in/ease-out/ease-in-out/spring |

## 技术架构

### 透明背景渲染方案（已验证）

Remotion CLI 直接编码的 WebM/MOV 会丢失 Alpha 通道。可靠方案：

1. **Remotion 渲染 PNG 序列**（`--transparent --sequence`）— 每帧都是 RGBA
2. **ffmpeg 合成 ProRes 4444**（`-c:v prores_ks -profile:v 4 -pix_fmt yuva444p12le`）— 保留 Alpha
3. **输出 MOV** — 剪映专业版完全兼容

验证结果：5秒 1080x1920，4.59MB，`yuva444p12le`，Alpha=True ✅

### Remotion 项目结构

```
remotion-project/
├── package.json          # Remotion 4.0.0 + React 18 + TypeScript
├── tsconfig.json
├── src/
│   ├── index.ts          # 入口
│   ├── Root.tsx          # 注册 Composition
│   ├── AnimationTemplate.tsx  # 核心动画组件
│   ├── types.ts          # 类型定义
│   └── easing.ts         # 缓动函数
├── public/               # 素材目录（PNG图片）
└── test_animation.json   # 测试动画配置
```

## 与其他垂类技能的定位差异

| 技能 | 定位 | 适用场景 |
|------|------|----------|
| **ComfyUI-controls-skill** | AI 生成（图/视频/音频） | 角色图、场景图、道具图、AI视频、音效生成 |
| **Blender-controls-skill** | 3D 动画/特效 | 3D角色动画、粒子特效、物理模拟、3D转场 |
| **Remotion-controls-skill** | 代码驱动 2D 动画 | 透明背景动画层、UI动画、文字动画、精确关键帧控制 |

## 环境要求

- Node.js >= 18
- Python >= 3.10
- ffmpeg（用于 ProRes 编码）
- Remotion 4.0.0（已在 remotion-project 中配置）

## 开发计划

- [ ] 更多预设动画模板（角色入场/出场、UI动效、文字动画）
- [ ] API 服务化（HTTP 接口远程渲染）
- [ ] 与 ai-video-editor 深度集成（导演引擎直接调用）
- [ ] 动画模板市场（社区分享）
- [ ] 性能优化（并行渲染、增量渲染）

## 许可证

MIT License
