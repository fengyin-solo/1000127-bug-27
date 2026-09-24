"""冷链物流温控运营平台 后端服务入口。

启动：uvicorn app.main:app --host 127.0.0.1 --port 8000
健康检查：GET /api/health
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import ROUTERS
from app.store import store

app = FastAPI(title="冷链物流温控运营平台", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for module in ROUTERS:
    app.include_router(module.router)


# 模块 key -> 中文模块名，直接取路由注册时的 prefix/tags，与列表页标题保持同一来源
MODULE_LABELS = {
    module.router.prefix.split("/")[-1]: module.router.tags[0]
    for module in ROUTERS
    if module.router.tags
}


@app.get("/api/health")
def health() -> dict[str, object]:
    """健康检查：确认服务已经监听、示例数据已经就绪。"""
    return {"ok": True, "app": settings.app_name, "modules": len(store.module_names())}


@app.get("/api/overview")
def overview() -> dict[str, object]:
    """运营概览：把各业务模块的总量、今日新增、待处理与异常量汇总成看板卡片。"""
    return store.overview(labels=MODULE_LABELS)
