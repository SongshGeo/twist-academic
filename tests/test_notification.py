#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

import pytest

from twist.notify import notify, notify_me_finished


# @notify_me_finished(18906102996)
@notify_me_finished(18500685922)
def add(a: int, b: int) -> int:
    """用来测试的函数"""
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("Only int.")
    return a + b


class TestNotify:
    """测试短信通知功能"""

    def test_notify_me(self):
        """测试直接通知"""
        # act / assert
        notify("test", tel_number=18500685922)

    def test_notify_me_finished(self):
        """测试运行完了通知我"""
        # arrange / act
        result = add(2, 3)

        # assert
        assert result == 5

    def test_notify_me_failed(self):
        """测试失败了也会通知我"""
        # arrange / act / assert
        with pytest.raises(TypeError):
            add(2.0, 3)
