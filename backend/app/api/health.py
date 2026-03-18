"""健康检查接口。

这个接口通常用于：
1. 本地快速确认后端是否已经成功启动；
2. 前端联调时检查服务是否可达；
3. 未来部署后做服务存活探针。
"""

from fastapi import APIRouter

from app.schemas.common import SuccessResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=SuccessResponse[dict[str, str]])
async def health_check() -> SuccessResponse[dict[str, str]]:
    # 保持返回结构与项目统一响应格式一致。
    return SuccessResponse(data={"status": "ok"})
