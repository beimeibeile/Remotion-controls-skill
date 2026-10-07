# Remotion Controls Skill - API 参考文档

## 主控入口: RemotionControls

```python
from remotion_controls import RemotionControls, create_controls
rc = create_controls(project_path="./remotion-project")
```

## 核心类

### AnimationRenderer
动画渲染器，支持：
- `render_from_config(config, output_name, transparent, use_prores)` - 从配置渲染
- `render_from_json_file(json_path, ...)` - 从JSON文件渲染
- `verify_output(output_path, ...)` - 验证输出（时长/分辨率/Alpha）
- `_render_prores_pipeline(...)` - PNG序列+ProRes 4444管线（保留Alpha）

### KeyframeBuilder
关键帧构建器：
- `add_position(frame, x, y, easing)`
- `add_scale(frame, sx, sy, easing)`
- `add_rotation(frame, degrees, easing)`
- `add_opacity(frame, alpha, easing)`
- `build()` -> Dict

### LayerBuilder
多图层构建器：
- `add_image_layer(image_path, x, y, keyframes, z_index)`
- `add_text_layer(text, x, y, font_size, color, keyframes, z_index)`
- `add_shape_layer(shape, x, y, size, color, keyframes, z_index)`
- `build()` -> List[Dict]（按z_index排序）

### TemplateLibrary
模板库：
- `list_templates(category)` - 列出模板
- `list_categories()` - 列出分类
- `get_template(template_id)` - 获取模板
- `instantiate_template(template_id, variables)` - 实例化（替换变量）
- `register_template(template_id, template)` - 注册自定义模板

## 内置模板（6个）
| ID | 分类 | 说明 |
|----|------|------|
| character_fall | character | 角色下落+旋转+弹性着地 |
| character_hit | character | 角色受击震动+闪白+后退 |
| ui_button_click | ui | 按钮点击缩放反馈+波纹 |
| text_typewriter | text | 打字机文字效果 |
| transition_fade | transition | 淡入淡出转场 |
| impact_punch | effect | 拳击冲击波+白闪 |

## 缓动曲线
linear, ease_in, ease_out, ease_in_out, spring, bounce, anticipate

## PIT-024 重要
CLI `--transparent` 会丢失Alpha通道。
正确流程：PNG序列渲染 + ffmpeg合成ProRes 4444（`use_prores=True`）。
