#!/usr/bin/env python 3.11.0
# -*-coding:utf-8 -*-
# @Author  : Shuang (Twist) Song
# @Contact   : SongshGeo@gmail.com
# GitHub   : https://github.com/SongshGeo
# Website: https://cv.songshgeo.com/

import logging
import re
from functools import wraps

from qcloudsms_py import SmsSingleSender
from qcloudsms_py.httpclient import HTTPError

logger = logging.getLogger(__name__)


def check_tel_number(tel_number: str | int) -> bool:
    """检查电话号码"""
    pattern = r"^(?:\+?86)?1(?:3\d{3}|5[^4\D]\d{2}|8\d{3}|7(?:[235-8]\d{2}|4(?:0\d|1[0-2]|9\d))|9[0-35-9]\d{2}|66\d{2})\d{6}$"
    is_matched = bool(re.search(pattern=pattern, string=str(f"{tel_number}")))
    return is_matched


def notify(param: str, tel_number: str | int) -> None:
    """Sends a notification message through the Tencent cloud service.

    Args:
        num (int): The number to be included in the message.

    Returns:
        dict: A dictionary containing the status of the message.

    Raises:
        HTTPError: If there is an error with the HTTP request.
        Exception: If there is any other error.

    """
    # 短信应用SDK AppID
    appid = 1400630042  # SDK AppID是1400开头
    # 短信应用SDK AppKey
    app_key = "ad30ec46aa617263813ca8996e1a0113"
    # 需要发送短信的手机号码
    phone_numbers = [f"{tel_number}"]
    # 短信模板ID，需要在短信应用中申请
    template_id = 1299444
    # 签名
    sms_sign = "隅地公众号"

    s_sender = SmsSingleSender(appid, app_key)
    params = [param]  # 当模板没有参数时，`params = []`
    try:
        return s_sender.send_with_param(
            86,
            phone_numbers[0],
            template_id,
            params,
            sign=sms_sign,
            extend="",
            ext="",
        )
    except (HTTPError, Exception) as e:
        logger.debug(f"Error sending: {e}")


def notify_me_finished(tel_number: int | str) -> callable:
    """A decorator.
    sends a notification message after the decorated function is called.

    Args:
        func: The function to be decorated.

    Returns:
        The decorated function.

    """
    is_matched = check_tel_number(tel_number=tel_number)
    if not is_matched:
        raise ValueError(f"'{tel_number}'不是有效的电话号码，请检查。")

    def decorated_notify(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            exit_code = 0
            try:
                return func(*args, **kwargs)
            except Exception as e:
                exit_code = 1
                raise e
            finally:
                notify(f"exit {exit_code}", tel_number=tel_number)

        return wrapper

    return decorated_notify
