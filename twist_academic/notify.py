#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact : SongshGeo@gmail.com
# @GitHub  : https://github.com/SongshGeo

from __future__ import annotations

import datetime as _dt
import socket
import traceback
from functools import wraps
from typing import Any, Callable, Optional

from .lark_notify import LarkNotifier, LarkSettings


def _build_message(
    *,
    title: Optional[str],
    func_name: Optional[str],
    status: str,
    start: Optional[_dt.datetime] = None,
    end: Optional[_dt.datetime] = None,
    exc: Optional[BaseException] = None,
) -> str:
    """Build plain-text content for a finished job."""
    lines: list[str] = []
    if title:
        lines.append(f"[{status.upper()}] {title}")
        lines.append("")
    elif func_name:
        lines.append(f"[{status.upper()}] {func_name}")
        lines.append("")

    if func_name:
        lines.append(f"Function: {func_name}")
    lines.append(f"Status: {status}")
    lines.append(f"Host: {socket.gethostname()}")

    if start and end:
        lines.append(f"Started at: {start.isoformat()}")
        lines.append(f"Finished at: {end.isoformat()}")
        lines.append(f"Duration: {end - start}")

    if exc is not None:
        lines.append("")
        lines.append("Exception:")
        lines.append(f"- type: {type(exc).__name__}")
        lines.append(f"- message: {exc}")
        tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        lines.append("")
        lines.append("Traceback (most recent call last):")
        lines.append(tb)

    return "\n".join(lines)


def _send_text(text: str) -> None:
    settings = LarkSettings.from_env()
    notifier = LarkNotifier(settings)
    notifier.send_text(text)


def _decorator(title: Optional[str] = None):
    def wrapper_func(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def inner(*args, **kwargs):
            start = _dt.datetime.now()
            exc: Optional[BaseException] = None
            status = "success"
            try:
                result = func(*args, **kwargs)
                return result
            except BaseException as err:  # noqa: BLE001
                exc = err
                status = "failure"
                raise
            finally:
                end = _dt.datetime.now()
                text = _build_message(
                    title=title,
                    func_name=func.__name__,
                    status=status,
                    start=start,
                    end=end,
                    exc=exc,
                )
                _send_text(text)

        return inner

    return wrapper_func


def notify(arg: Any = None, *, title: Optional[str] = None):
    """Unified notification API.

    Usage:
        - @notify
        - @notify(title="my job")
        - notify("just send this text")
    """
    if isinstance(arg, str) and not callable(arg):
        _send_text(arg if title is None else f"{title}\n\n{arg}")
        return None

    if callable(arg) and title is None:
        return _decorator()(arg)

    return _decorator(title=title)
