# 透明动画素材库 v1.0

> 基于Remotion的可复用透明背景动画组件库，输出ProRes 4444格式，可直接导入剪映使用。

## 一、素材库概览

| 分类 | 组件数 | 状态 | 说明 |
|------|--------|------|------|
| 角色动画 | 1 | ✅ 可用 | CharacterSprite - 角色精灵动画 |
| 特效动画 | 2 | ✅ 可用 | Effects, ImpactEffects |
| 文字动画 | 1 | ✅ 可用 | TextAnimations |
| 转场特效 | 1 | ✅ 可用 | TransitionEffects |
| 运动路径 | 1 | ✅ 可用 | MotionPath |
| 测试组件 | 4 | ✅ 可用 | AlphaTest, ComponentTest, TextAnimationTest, EffectTest |
| 模板组件 | 1 | ✅ 可用 | AnimationTemplate |
| 案例组件 | 1 | ⚠️ 待优化 | DoubaoHitAnimation |

## 二、组件详细说明

### 2.1 角色动画

#### CharacterSprite
- **文件**: `components/CharacterSprite.tsx`
- **功能**: 角色精灵动画，支持多帧序列播放
- **参数**:
  - `frames`: 帧图片URL数组
  - `fps`: 播放帧率
  - `loop`: 是否循环
  - `scale`: 缩放比例
- **适用场景**: 角色待机、行走、跳跃等循环动画

### 2.2 特效动画

#### Effects
- **文件**: `components/Effects.tsx`
- **功能**: 通用特效集合
- **包含特效**: 闪光、粒子、光晕等
- **适用场景**: 强调、装饰、氛围营造

#### ImpactEffects
- **文件**: `components/ImpactEffects.tsx`
- **功能**: 冲击/打击特效
- **包含特效**: 冲击波、震屏、爆炸、火花等
- **适用场景**: 打斗、碰撞、强调瞬间

### 2.3 文字动画

#### TextAnimations
- **文件**: `components/TextAnimations.tsx`
- **功能**: 文字入场/出场/循环动画
- **包含动画**: 打字机、弹跳、淡入、滑动、缩放等
- **适用场景**: 标题、字幕、强调文字

### 2.4 转场特效

#### TransitionEffects
- **文件**: `components/TransitionEffects.tsx`
- **功能**: 场景转场动画
- **包含转场**: 淡入淡出、滑动、缩放、旋转、遮罩等
- **适用场景**: 场景切换、镜头转场

### 2.5 运动路径

#### MotionPath
- **文件**: `components/MotionPath.tsx`
- **功能**: 沿路径运动的动画
- **参数**:
  - `path`: 路径点数组
  - `duration`: 运动时长
  - `easing`: 缓动函数
- **适用场景**: 物体沿轨迹运动、引导动画

## 三、测试组件

### AlphaTest
- **功能**: Alpha通道测试动画
- **内容**: 红色方块+蓝色圆形移动+透明度渐变
- **用途**: 验证ProRes 4444 Alpha通道保留
- **规格**: 1080x1920, 30fps, 3秒(90帧)

### ComponentTest
- **功能**: 组件综合测试
- **用途**: 验证各组件渲染正确性

### TextAnimationTest
- **功能**: 文字动画测试
- **用途**: 验证文字动画效果

### EffectTest
- **功能**: 特效测试
- **用途**: 验证特效渲染效果

## 四、模板组件

### AnimationTemplate
- **文件**: `AnimationTemplate.tsx`
- **功能**: 可配置动画模板
- **配置**: 通过animation-config.ts配置角色、动作、特效
- **用途**: 快速生成定制化动画

## 五、案例组件

### DoubaoHitAnimation
- **文件**: `DoubaoHitAnimation.tsx`
- **功能**: 豆包被打案例动画
- **状态**: ⚠️ 待优化（需达到原视频80%以上效果）
- **依赖**: 角色素材、动作配置、特效组合

## 六、使用流程

### 6.1 渲染单个动画为ProRes 4444

```python
from capabilities.cap_animation_renderer.renderer import AnimationRenderer

renderer = AnimationRenderer(
    project_path="path/to/remotion-project",
    output_dir="./output"
)

result = renderer.render_from_config(
    config={"composition": "AlphaTest", "fps": 30, "width": 1080, "height": 1920},
    output_name="my_animation.mov",
    use_prores=True,
)
# result["success"] == True
# result["output"] == "./output/my_animation.mov"
```

### 6.2 验证动画质量

```bash
python verify_animation.py output/my_animation.mov --duration 3 --width 1080 --height 1920
```

### 6.3 导入剪映

1. 将.mov文件复制到剪映工程的materials目录
2. 在剪映中导入素材（避免自动转码丢失Alpha）
3. 拖到时间线，叠加在其他视频上方
4. 透明背景自动生效

## 七、质量标准

所有素材库动画必须通过以下验证：

| 指标 | 标准 |
|------|------|
| Alpha通道 | 必须保留（yuva444p12le） |
| 编码格式 | ProRes 4444 (profile=4) |
| 分辨率 | 1080x1920（竖屏）或按需 |
| 帧率 | 30fps |
| 首末帧 | 非全黑/非全透明 |
| 文件大小 | 10秒≤100MB |

详见 [QUALITY_STANDARD.md](./QUALITY_STANDARD.md)

## 八、待开发组件

### 高优先级
- [ ] 角色入场动画（从屏幕外滑入/弹入）
- [ ] 角色出场动画（滑出/淡出/缩小消失）
- [ ] 表情切换动画（开心/生气/惊讶等）
- [ ] 手势动画（指、挥、拍等）

### 中优先级
- [ ] 道具动画（弹弓、飞钩、飞石、传送门）
- [ ] UI动画（印章、弹出、进度条）
- [ ] 环境特效（雨、雪、风、光斑）

### 低优先级
- [ ] 复杂角色动作（打斗组合技）
- [ ] 粒子系统（自定义粒子效果）
- [ ] 3D透视动画

## 九、目录结构

```
remotion-project/
├── src/
│   ├── components/          # 可复用组件
│   │   ├── CharacterSprite.tsx
│   │   ├── Effects.tsx
│   │   ├── ImpactEffects.tsx
│   │   ├── MotionPath.tsx
│   │   ├── TextAnimations.tsx
│   │   ├── TransitionEffects.tsx
│   │   └── index.ts
│   ├── AlphaTest.tsx        # 测试组件
│   ├── AnimationTemplate.tsx # 模板组件
│   ├── DoubaoHitAnimation.tsx # 案例组件
│   ├── animation-config.ts  # 动画配置
│   ├── easing.ts            # 缓动函数
│   ├── types.ts             # 类型定义
│   ├── Root.tsx             # 注册Composition
│   └── index.ts             # 入口
└── ANIMATION_LIBRARY.md     # 本文档
```
