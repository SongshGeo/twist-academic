#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact : SongshGeo@gmail.com
# @GitHub  : https://github.com/SongshGeo

from .env import load_dotenv

load_dotenv()

from .notify import notify  # noqa: E402

__all__ = ["notify"]
