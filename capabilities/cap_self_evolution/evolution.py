"""
cap_self_evolution - 自学习进化
记录渲染参数与效果评分，优化预设参数，生成最佳实践文档
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional


class SelfEvolution:
    """自学习进化模块"""

    def __init__(self, memory_dir: Optional[str] = None):
        if memory_dir is None:
            self.memory_dir = Path(__file__).parent.parent.parent / "memory"
        else:
            self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        self.history_file = self.memory_dir / "render_history.json"
        self.best_practices_file = self.memory_dir / "best_practices.md"

    def record_render(
        self,
        template_id: str,
        params: Dict[str, Any],
        output_path: str,
        quality_score: float,
        *,
        render_time_sec: Optional[float] = None,
        file_size_mb: Optional[float] = None,
        notes: Optional[str] = None,
    ) -> None:
        """记录一次渲染"""
        history = self._load_history()
        record = {
            "timestamp": datetime.now().isoformat(),
            "template_id": template_id,
            "params": params,
            "output_path": output_path,
            "quality_score": quality_score,
            "render_time_sec": render_time_sec,
            "file_size_mb": file_size_mb,
            "notes": notes,
        }
        history.append(record)
        self._save_history(history)

    def get_best_params(self, template_id: str, top_n: int = 3) -> List[Dict[str, Any]]:
        """获取某模板的最佳参数（按质量评分排序）"""
        history = self._load_history()
        records = [r for r in history if r.get("template_id") == template_id]
        records.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
        return records[:top_n]

    def generate_best_practices(self) -> str:
        """生成最佳实践文档"""
        history = self._load_history()
        if not history:
            return "# 最佳实践\n\n暂无渲染记录。\n"

        # 按模板分组
        templates = {}
        for r in history:
            tid = r.get("template_id", "unknown")
            if tid not in templates:
                templates[tid] = []
            templates[tid].append(r)

        lines = ["# Remotion 渲染最佳实践\n"]
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        lines.append(f"总渲染次数: {len(history)}\n")

        for tid, records in templates.items():
            lines.append(f"\n## {tid}\n")
            lines.append(f"- 渲染次数: {len(records)}")
            avg_score = sum(r.get("quality_score", 0) for r in records) / len(records)
            lines.append(f"- 平均质量分: {avg_score:.1f}")

            best = max(records, key=lambda x: x.get("quality_score", 0))
            lines.append(f"- 最佳质量分: {best.get('quality_score', 0):.1f}")
            lines.append(f"- 最佳参数:\n```json\n{json.dumps(best.get('params', {}), ensure_ascii=False, indent=2)}\n```")

        content = "\n".join(lines)
        with open(self.best_practices_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return content

    def _load_history(self) -> List[Dict[str, Any]]:
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_history(self, history: List[Dict[str, Any]]) -> None:
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
