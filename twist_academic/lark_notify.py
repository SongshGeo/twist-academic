#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact : SongshGeo@gmail.com
# @GitHub  : https://github.com/SongshGeo

from __future__ import annotations

import base64
import dataclasses
import hashlib
import hmac
import json
import os
import time
from typing import Optional
from urllib import request


@dataclasses.dataclass(slots=True)
class LarkSettings:
    """Runtime configuration for sending notifications to a Lark bot webhook."""

    webhook: str
    secret: Optional[str] = None

    @classmethod
    def from_env(cls, prefix: str = "TWIST_LARK_") -> "LarkSettings":
        """Create settings from environment variables."""
        webhook = os.getenv(prefix + "WEBHOOK")
        if not webhook:
            raise RuntimeError(f"Missing required env var: {prefix}WEBHOOK")
        secret = os.getenv(prefix + "SECRET")
        return cls(webhook=webhook, secret=secret)


class LarkNotifier:
    """Notifier that sends plain-text messages to a Lark webhook bot."""

    def __init__(self, settings: LarkSettings, timeout: float = 5.0) -> None:
        """Initialize a notifier."""
        self._settings = settings
        self._timeout = timeout

    def _build_sign_fields(self) -> dict[str, str]:
        """Build timestamp/signature fields when secret is configured."""
        if not self._settings.secret:
            return {}

        timestamp = str(int(time.time()))
        string_to_sign = f"{timestamp}\n{self._settings.secret}"
        digest = hmac.new(
            string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        sign = base64.b64encode(digest).decode("utf-8")
        return {"timestamp": timestamp, "sign": sign}

    def send_text(self, text: str) -> None:
        """Send a plain-text message to the configured webhook."""
        payload: dict = {
            "msg_type": "text",
            "content": {"text": text},
        }
        payload.update(self._build_sign_fields())

        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            url=self._settings.webhook,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=self._timeout):
            return None
