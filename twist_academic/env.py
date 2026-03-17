#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact : SongshGeo@gmail.com
# @GitHub  : https://github.com/SongshGeo

from __future__ import annotations

import os
from pathlib import Path


def load_dotenv(path: str | Path = ".env") -> None:
    """Load a minimal .env file into environment variables."""
    p = Path(path)
    if not p.is_file():
        return

    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        os.environ.setdefault(key, value)
