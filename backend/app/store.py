"""内存数据仓库：给每个业务模块准备一份可筛选、可流转的示例数据。

真实项目里这里会换成数据库访问层；当前实现只依赖标准库，保证克隆下来就能起。
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

from app.registry import MODULES
from app.seed import SEED_ROWS


class Store:
    def __init__(self) -> None:
        self._tables: dict[str, list[dict[str, Any]]] = {
            name: [dict(row) for row in rows] for name, rows in SEED_ROWS.items()
        }

    def module_names(self) -> list[str]:
        """返回概览口径下的全部模块：以模块目录为准，空表也要出现。"""
        return [spec.key for spec in MODULES]

    def rows(self, module: str) -> list[dict[str, Any]]:
        return self._tables.setdefault(module, [])

    def find(self, module: str, entry_id: int) -> dict[str, Any] | None:
        for row in self.rows(module):
            if int(row.get("id", 0)) == entry_id:
                return row
        return None

    def overview(self, *, today: date | None = None) -> dict[str, object]:
        """运营概览汇总。

        口径与各列表页保持一致：total 就是该模块列表的全部记录数；
        created 只统计模块时间字段落在「今天」的记录，没有时间字段的模块按 0 处理，
        绝不能拿历史总量充当今日新增。模块目录里即使一条记录都没有，也输出零值行。
        """
        today = today or date.today()
        today_text = today.isoformat()
        modules: list[dict[str, object]] = []
        for spec in MODULES:
            rows = self.rows(spec.key)
            created = 0
            if spec.date_field:
                created = sum(
                    1
                    for row in rows
                    if str(row.get(spec.date_field) or "")[:10] == today_text
                )
            modules.append({
                "key": spec.key,
                "name": spec.label,
                "total": len(rows),
                "created": created,
                "pending": sum(1 for row in rows if row.get("pending")),
                "abnormal": sum(1 for row in rows if row.get("abnormal")),
            })
        cards = [
            {"label": "业务模块", "value": len(modules)},
            {"label": "今日新增", "value": sum(int(item["created"]) for item in modules)},
            {"label": "记录总量", "value": sum(int(item["total"]) for item in modules)},
            {"label": "待处理", "value": sum(int(item["pending"]) for item in modules)},
            {"label": "异常量", "value": sum(int(item["abnormal"]) for item in modules)},
        ]
        return {
            "cards": cards,
            "modules": modules,
            "date": today_text,
            "generated_at": datetime.now().replace(microsecond=0).isoformat(),
        }


store = Store()
