#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact : SongshGeo@gmail.com
# @GitHub  : https://github.com/SongshGeo

from __future__ import annotations

import json
import os
from typing import Any

import pytest
from pytest import MonkeyPatch

from twist_academic.env import load_dotenv
from twist_academic.lark_notify import LarkNotifier, LarkSettings
from twist_academic.notify import notify


class TestLarkNotifier:
    """测试 LarkSettings 与 LarkNotifier 行为。"""

    def test_lark_settings_from_env(self, monkeypatch: MonkeyPatch) -> None:
        """LarkSettings.from_env 能从环境变量中正确读取 webhook 与 secret。"""
        env = {
            "TWIST_LARK_WEBHOOK": "https://example.com/webhook",
            "TWIST_LARK_SECRET": "secret",
        }
        monkeypatch.setattr(os, "environ", env)
        settings = LarkSettings.from_env()
        assert settings.webhook == env["TWIST_LARK_WEBHOOK"]
        assert settings.secret == env["TWIST_LARK_SECRET"]

    def test_lark_settings_missing_webhook_raises(
        self, monkeypatch: MonkeyPatch
    ) -> None:
        """缺少 TWIST_LARK_WEBHOOK 时，from_env 会抛出 RuntimeError。"""
        env = {"TWIST_LARK_SECRET": "secret"}
        monkeypatch.setattr(os, "environ", env)
        with pytest.raises(RuntimeError):
            LarkSettings.from_env()

    def test_lark_notifier_send_text_with_sign(self, monkeypatch: MonkeyPatch) -> None:
        """在配置了 secret 时，LarkNotifier 会在 payload 中添加签名字段并通过 HTTP POST 发送。"""
        settings = LarkSettings(
            webhook="https://example.com/webhook",
            secret="secret",
        )
        captured: dict[str, Any] = {}

        def fake_urlopen(req, timeout: float):  # type: ignore[no-untyped-def]
            captured["url"] = req.full_url
            captured["data"] = req.data
            captured["headers"] = dict(req.headers)
            captured["timeout"] = timeout

            class _Resp:
                def __enter__(self) -> "_Resp":
                    return self

                def __exit__(self, exc_type, exc, tb) -> None:
                    return None

                def read(self) -> bytes:
                    return b"ok"

            return _Resp()

        monkeypatch.setattr("twist_academic.lark_notify.request.urlopen", fake_urlopen)
        notifier = LarkNotifier(settings, timeout=1.0)
        notifier.send_text("hello")

        assert captured["url"] == settings.webhook
        headers = {k.lower(): v for k, v in captured["headers"].items()}
        assert headers["content-type"] == "application/json"
        payload = json.loads(captured["data"])
        assert payload["msg_type"] == "text"
        assert payload["content"]["text"] == "hello"
        assert "timestamp" in payload
        assert "sign" in payload


@pytest.mark.integration
class TestLarkNotifierIntegration:
    """飞书真实 webhook 的集成测试，需要联网且 webhook 可用时手动运行。"""

    def test_send_text_to_real_webhook(self) -> None:
        """使用给定的飞书 webhook 发送一条测试消息，便于人工确认接收情况。"""
        settings = LarkSettings(
            webhook="https://open.feishu.cn/open-apis/bot/v2/hook/171cb680-dff7-41fd-9826-15282d420821",
            secret=None,
        )
        notifier = LarkNotifier(settings, timeout=5.0)
        notifier.send_text(
            "实验: twist-academic notify integration test: hello from pytest."
        )


class TestNotifyDecoratorAndFunction:
    """测试统一 notify API 的装饰器与直接调用行为。"""

    def test_notify_decorator_success(self, monkeypatch: MonkeyPatch) -> None:
        """@notify 在函数成功执行时发送 success 消息。"""
        texts: list[str] = []

        def fake_send(text: str) -> None:
            texts.append(text)

        monkeypatch.setenv("TWIST_LARK_WEBHOOK", "https://example.com/webhook")

        def fake_send_text(self, text: str) -> None:  # type: ignore[no-untyped-def]
            fake_send(text)

        monkeypatch.setattr(
            "twist_academic.lark_notify.LarkNotifier.send_text", fake_send_text
        )

        @notify
        def add(a: int, b: int) -> int:
            return a + b

        result = add(1, 2)
        assert result == 3
        assert texts
        assert "Status: success" in texts[-1]

    def test_notify_decorator_failure(self, monkeypatch: MonkeyPatch) -> None:
        """@notify 在函数抛异常时发送 failure 消息并继续抛出异常。"""
        texts: list[str] = []

        def fake_send(text: str) -> None:
            texts.append(text)

        monkeypatch.setenv("TWIST_LARK_WEBHOOK", "https://example.com/webhook")
        monkeypatch.setattr(
            "twist_academic.lark_notify.LarkNotifier.send_text",
            lambda self, text: fake_send(text),  # type: ignore[no-untyped-def]
        )

        @notify
        def boom() -> None:
            raise ValueError("boom")

        with pytest.raises(ValueError):
            boom()

        assert texts
        assert "Status: failure" in texts[-1]
        assert "ValueError" in texts[-1]

    def test_notify_with_title_and_direct_text(self, monkeypatch: MonkeyPatch) -> None:
        """notify 可以作为函数直接发送文本，并支持 title 前缀。"""
        texts: list[str] = []

        monkeypatch.setenv("TWIST_LARK_WEBHOOK", "https://example.com/webhook")
        monkeypatch.setattr(
            "twist_academic.lark_notify.LarkNotifier.send_text",
            lambda self, text: texts.append(text),  # type: ignore[no-untyped-def]
        )

        notify("plain message")
        notify("body", title="Title")

        assert len(texts) == 2
        assert texts[0] == "plain message"
        assert "Title" in texts[1]
        assert "body" in texts[1]


class TestLoadDotenv:
    """测试极简 load_dotenv 的行为。"""

    def test_load_dotenv_assigns_missing_keys(
        self, tmp_path, monkeypatch: MonkeyPatch
    ) -> None:
        """.env 中的键会被加载为环境变量，但不会覆盖已有值。"""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "FOO=bar\n# comment\nBAZ=qux\nFOO=should_not_override\n",
            encoding="utf-8",
        )

        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("FOO", raising=False)
        monkeypatch.delenv("BAZ", raising=False)

        os.environ["FOO"] = "original"
        load_dotenv()

        assert os.getenv("FOO") == "original"
        assert os.getenv("BAZ") == "qux"
