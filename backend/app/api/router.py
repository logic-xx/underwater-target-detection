"""路由聚合入口。

`main.py` 只需要引入这个总路由对象，而不需要关心每个业务子路由具体定义在哪。
这样后续扩展更多接口时，入口文件仍然保持简洁。
"""

from fastapi import APIRouter

from app.api.detect import router as detect_router
from app.api.health import router as health_router


api_router = APIRouter()
# 先注册健康检查，再注册业务路由。这里的顺序通常影响不大，
# 但从阅读角度看，基础路由放前面更直观。
api_router.include_router(health_router)
api_router.include_router(detect_router)
