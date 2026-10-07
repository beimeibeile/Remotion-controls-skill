# Remotion Controls Skill - 使用规则

## AI调用规则
1. 透明背景动画必须使用 `use_prores=True`（PNG序列+ProRes 4444），CLI `--transparent` 会丢失Alpha
2. 渲染前必须确认Node.js和Remotion CLI已安装
3. 单次渲染时长不超过30秒，长动画需分段
4. 输出必须调用 `verify_output()` 验证Alpha通道存在
5. 与ai-video-editor集成时通过RemotionControls统一入口
6. 模板变量必须全部替换后才能渲染
7. 渲染失败必须重试最多2次，记录错误日志
8. 不得在未验证Alpha通道的情况下将输出导入剪映
