"""文件管理工具。

把文件保存、复制、metadata 写入、URL 构造这些通用能力集中在这里，
可以避免 service 层重复写同样的文件系统逻辑。
"""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


def generate_task_id() -> str:
    """生成任务 ID。

    格式：UTC 时间戳 + 8 位 UUID，兼顾可读性与低冲突概率。
    这个 ID 会同时用于：
    - 上传文件名
    - 输出文件名
    - metadata 文件名
    - 接口返回的 `task_id`
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"{timestamp}_{uuid4().hex[:8]}"


async def save_upload_file(upload_file: UploadFile, destination: Path) -> int:
    """保存上传文件到目标路径，并返回文件字节数。"""
    destination.parent.mkdir(parents=True, exist_ok=True)

    # 这里直接一次性读取全部内容，适合当前 MVP/小中型文件场景。
    # 如果后续要支持超大视频，可以再改成分块写入。
    content = await upload_file.read()
    destination.write_bytes(content)
    await upload_file.close()
    return len(content)


def copy_file(source: Path, destination: Path) -> None:
    """复制文件到目标路径。"""
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def save_metadata(destination: Path, payload: dict) -> None:
    """把任务结果写成 JSON metadata 文件。"""
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def build_public_url(path: Path, root_directory: Path, public_prefix: str) -> str:
    """把磁盘绝对路径转换成前端可访问的静态 URL。

    例如：
    - 磁盘路径：`outputs/images/result_xxx.jpg`
    - 根目录：`outputs`
    - 前缀：`/outputs`
    最终返回：`/outputs/images/result_xxx.jpg`
    """
    relative_path = path.relative_to(root_directory).as_posix()
    return f"{public_prefix}/{relative_path}"
