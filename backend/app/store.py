"""内存数据仓库：给每个业务模块准备一份可筛选、可流转的示例数据。

真实项目里这里会换成数据库访问层；当前实现只依赖标准库，保证克隆下来就能起。
"""
from __future__ import annotations

from datetime import date
from typing import Any

from app.seed import SEED_ROWS


class Store:
    def __init__(self) -> None:
        self._tables: dict[str, list[dict[str, Any]]] = {
            name: [dict(row) for row in rows] for name, rows in SEED_ROWS.items()
        }

    def module_names(self) -> list[str]:
        return sorted(self._tables)

    def rows(self, module: str) -> list[dict[str, Any]]:
        return self._tables.setdefault(module, [])

    def find(self, module: str, entry_id: int) -> dict[str, Any] | None:
        for row in self.rows(module):
            if int(row.get("id", 0)) == entry_id:
                return row
        return None

    def append(self, module: str, entry: dict[str, Any]) -> None:
        """写入一条新记录：统一补上创建日期，概览的「今日新增」按它统计。"""
        entry.setdefault("created_at", date.today().isoformat())
        self.rows(module).append(entry)

    def overview(self, labels: dict[str, str] | None = None) -> dict[str, object]:
        """汇总各业务模块指标，卡片与表格同源，前端不做二次计算。

        口径说明：
        - total/记录总量：模块全部记录数，与列表接口返回的 total 一致；
        - created/今日新增：created_at 为今天的记录数，历史记录不计入；
        - pending/abnormal：与列表行上的 pending/abnormal 标记同口径。
        没有记录的模块照样返回一行零值，不缺列、不返回 null。
        """
        label_map = labels or {}
        # 按 labels（路由注册顺序，与左侧导航一致）排，labels 之外的表补在最后
        ordered = [name for name in label_map if name in self._tables]
        ordered.extend(name for name in self.module_names() if name not in label_map)

        today = date.today().isoformat()
        modules: list[dict[str, object]] = []
        for name in ordered:
            rows = self.rows(name)
            modules.append({
                "name": label_map.get(name, name),
                "total": len(rows),
                "created": sum(1 for row in rows if str(row.get("created_at") or "")[:10] == today),
                "pending": sum(1 for row in rows if row.get("pending")),
                "abnormal": sum(1 for row in rows if row.get("abnormal")),
            })

        cards = [
            {"label": "业务模块", "value": len(modules)},
            {"label": "记录总量", "value": sum(int(item["total"]) for item in modules)},
            {"label": "今日新增", "value": sum(int(item["created"]) for item in modules)},
            {"label": "待处理", "value": sum(int(item["pending"]) for item in modules)},
            {"label": "异常量", "value": sum(int(item["abnormal"]) for item in modules)},
        ]
        return {"generated_at": today, "cards": cards, "modules": modules}


store = Store()
