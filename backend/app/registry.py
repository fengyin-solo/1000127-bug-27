"""业务模块目录：概览、导航与列表页共用的唯一口径。

key 必须与数据表名、接口前缀一致；label 是给运营看的中文名；
date_field 是该模块代表「记录创建/发生时间」的字段，概览用它统计今日新增，
没有可靠时间字段的模块置 None，今日新增一律按 0 处理而不是拿历史总量冒充。
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModuleSpec:
    key: str
    label: str
    date_field: str | None = None


MODULES: tuple[ModuleSpec, ...] = (
    ModuleSpec("order", "冷链订单", "下单时间"),
    ModuleSpec("waybill", "运单管理", "装车时间"),
    ModuleSpec("vehicle", "冷藏车管理"),
    ModuleSpec("driver", "司机管理"),
    ModuleSpec("temperature", "温控监控", "采集时间"),
    ModuleSpec("excursion", "温度异常", "发生时间"),
    ModuleSpec("warehouse", "冷库管理"),
    ModuleSpec("inbound", "入库管理", "入库时间"),
    ModuleSpec("outbound", "出库管理", "出库时间"),
    ModuleSpec("inventory", "库存管理", "入库日期"),
    ModuleSpec("trace", "批次追溯"),
    ModuleSpec("quality", "质检管理", "检测时间"),
    ModuleSpec("route", "线路管理"),
    ModuleSpec("dispatch", "调度派单", "计划发车时间"),
    ModuleSpec("device", "温控设备"),
    ModuleSpec("maint", "维保工单", "期望完成时间"),
    ModuleSpec("alarm", "告警中心", "触发时间"),
    ModuleSpec("customer", "客户管理"),
    ModuleSpec("billing", "计费结算"),
    ModuleSpec("report", "报表导出", "生成时间"),
    ModuleSpec("setting", "系统设置"),
)

MODULE_KEYS: tuple[str, ...] = tuple(spec.key for spec in MODULES)
MODULE_SPECS: dict[str, ModuleSpec] = {spec.key: spec for spec in MODULES}
