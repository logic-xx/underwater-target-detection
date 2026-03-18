"""项目配置模块。

这里集中管理所有可变配置，避免把路径、默认阈值、端口等信息写死在代码里。
后续切换开发环境、测试环境、生产环境时，只需要改 `.env` 即可。
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# `backend/app/core/config.py` 往上三级就是仓库根目录。
# 之所以取项目根目录，是因为 `.env`、`uploads/`、`outputs/`、`metadata/`
# 都位于仓库级别，而不是 `backend/` 目录内部。
PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """读取 `.env` 中的后端配置并提供辅助属性。

    `BaseSettings` 会自动从环境变量或 `.env` 文件中读取值。
    这里既保留了配置原始字符串，也提供了转换后的 `Path` 属性，
    方便业务代码直接使用。
    """

    # 服务监听地址与端口。
    backend_host: str = Field(default="127.0.0.1", alias="BACKEND_HOST")
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")

    # 真实模型接入后会使用该路径；当前 mock 版本只保留配置入口，不实际加载。
    model_path: str = Field(default="weights/best.pt", alias="MODEL_PATH")

    # 文件系统目录配置：上传文件、处理结果、metadata 均由配置控制。
    upload_dir: str = Field(default="uploads", alias="UPLOAD_DIR")
    output_dir: str = Field(default="outputs", alias="OUTPUT_DIR")
    metadata_dir: str = Field(default="metadata", alias="METADATA_DIR")

    # 检测默认参数：当前主要用于记录 metadata 和未来真实推理的默认值。
    default_conf: float = Field(default=0.5, alias="DEFAULT_CONF")
    default_iou: float = Field(default=0.5, alias="DEFAULT_IOU")

    # 文件大小限制，接口接收文件后会据此校验。
    max_image_size_mb: int = Field(default=20, alias="MAX_IMAGE_SIZE_MB")
    max_video_size_mb: int = Field(default=500, alias="MAX_VIDEO_SIZE_MB")

    # 指定 `.env` 文件位置，并允许 `.env` 中包含当前类未显式声明的额外字段。
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    def resolve_path(self, value: str) -> Path:
        """把配置里的路径统一转换成绝对路径。

        - 如果本身已经是绝对路径，直接返回；
        - 如果是相对路径，则默认相对于项目根目录解析。
        """
        path = Path(value)
        if path.is_absolute():
            return path
        return PROJECT_ROOT / path

    @property
    def model_path_path(self) -> Path:
        """模型文件的绝对路径。"""
        return self.resolve_path(self.model_path)

    @property
    def upload_dir_path(self) -> Path:
        """上传目录的绝对路径。"""
        return self.resolve_path(self.upload_dir)

    @property
    def output_dir_path(self) -> Path:
        """输出目录的绝对路径。"""
        return self.resolve_path(self.output_dir)

    @property
    def metadata_dir_path(self) -> Path:
        """metadata 目录的绝对路径。"""
        return self.resolve_path(self.metadata_dir)

    def ensure_directories(self) -> None:
        """确保运行时需要的目录存在。

        这里会同时创建总目录和图片/视频子目录，避免业务代码每次都判断目录是否存在。
        """
        for directory in (
            self.upload_dir_path,
            self.output_dir_path,
            self.metadata_dir_path,
            self.upload_dir_path / "images",
            self.upload_dir_path / "videos",
            self.output_dir_path / "images",
            self.output_dir_path / "videos",
        ):
            directory.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """返回全局复用的配置对象。

    配置通常在整个进程生命周期内不需要重复构建，因此使用缓存可以避免重复解析 `.env`。
    """
    return Settings()
