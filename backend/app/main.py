"""FastAPI 应用入口。

这个文件只负责三件事：
1. 创建 FastAPI 应用对象；
2. 注册总路由和静态文件目录；
3. 把异常统一包装成项目约定的响应格式。

真正的业务逻辑不应该写在这里，而应该继续下沉到 `api/`、`services/`
和 `utils/` 中，这样后续接入真实模型时更容易维护。
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import get_settings
from app.schemas.common import error_response


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """应用生命周期钩子。

    FastAPI 启动时会先执行 `yield` 之前的代码，关闭时再回到 `yield` 之后。
    这里目前只做一件基础工作：确保上传目录、输出目录、metadata 目录存在。
    """
    settings.ensure_directories()
    yield


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用实例。"""

    # 这里再次确保目录存在，是为了在挂载 StaticFiles 之前就创建好目录。
    # 否则如果目录还不存在，应用在启动阶段就可能直接报错。
    settings.ensure_directories()

    # 创建 Web 应用对象。
    app = FastAPI(
        title="Underwater Target Detection System",
        version="0.1.0",
        lifespan=lifespan,
    )

    # 注册总路由。后续新增业务路由时，只需要在 `api/router.py` 中聚合即可。
    app.include_router(api_router)

    # 挂载静态文件目录：
    # - `/outputs` 给前端访问检测结果图片/视频
    # - `/uploads` 主要用于调试或需要时查看原始上传文件
    app.mount("/outputs", StaticFiles(directory=settings.output_dir_path), name="outputs")
    app.mount("/uploads", StaticFiles(directory=settings.upload_dir_path), name="uploads")

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: FastAPI, exc: HTTPException) -> JSONResponse:
        """处理业务层主动抛出的 HTTP 错误。

        例如文件类型不合法、文件过大、参数不在允许范围内时，
        service 中会抛出 `HTTPException`，这里统一改写为：
        `{"code": 1, "message": "...", "data": null}`。
        """
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(message=str(exc.detail)).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _: FastAPI, exc: RequestValidationError
    ) -> JSONResponse:
        """处理 FastAPI/Pydantic 的请求参数校验错误。

        比如缺少文件字段、`conf` 不是数字等问题，都会先进入这里。
        这里取第一条错误信息返回，保持对前端更简洁。
        """
        first_error = exc.errors()[0] if exc.errors() else {}
        message = first_error.get("msg", "request validation failed")
        return JSONResponse(
            status_code=422,
            content=error_response(message=message).model_dump(),
        )

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(_: FastAPI, exc: Exception) -> JSONResponse:
        """处理未预期的异常，避免默认报错页面直接暴露给前端。"""
        return JSONResponse(
            status_code=500,
            content=error_response(message=str(exc) or "internal server error").model_dump(),
        )

    return app


#
# 模块级别直接暴露 `app`，这样 `uvicorn app.main:app --reload` 可以直接启动。
#
app = create_app()
