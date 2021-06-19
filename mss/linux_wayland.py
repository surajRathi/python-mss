"""
This is part of the MSS Python's module.
Source: https://github.com/BoboTiG/python-mss
"""

import dataclasses
from random import random
from typing import TYPE_CHECKING

import cv2
from gi.repository import GLib
from pydbus import SessionBus, Variant

from .base import MSSBase
from .exception import ScreenShotError

if TYPE_CHECKING:
    from typing import Any, Dict, List, Optional, Tuple, Union  # noqa

    from .models import Monitor, Monitors  # noqa
    from .screenshot import ScreenShot  # noqa

__all__ = ("MSS",)


class MSS(MSSBase):
    """
    Multiple ScreenShots implementation for Wayland on GNU/Linux.
    It uses the xdg-desktop-portal interface via dbus.
    """

    __slots__ = {"_monitors", "cls_image", "compression_level", "_bus", "_screenshot_handle"}

    def __init__(self, **_):
        # type: (Any) -> None
        super().__init__()

        self._bus = SessionBus()
        self._screenshot_handle = self._bus.get(
            "org.freedesktop.portal.Desktop",  # Bus Service Name ".portal.Desktop"
            "/org/freedesktop/portal/desktop"  # object path "portal/desktop"
        )['org.freedesktop.portal.Screenshot']

    def _grab_impl(self, monitor):
        # type: (Monitor) -> ScreenShot
        token = str(int(100000 * random()))
        request_handle = self._screenshot_handle.Screenshot(
            "",  # Window id: s :if xdg-desktop-portal
            {  # Options: a{sv}
                'handle_token': Variant('s', token)  # todo create
                # Args regarding the
                # 'modal': Variant('b', True)
                # 'interactive': Variant('b', False)
            },
        )
        request = self._bus.get(
            "org.freedesktop.portal.Desktop",
            request_handle,
        )['org.freedesktop.portal.Request']

        loop = GLib.MainLoop()

        @dataclasses.dataclass
        class Response:
            """Store the signal response on 'org.freedesktop.portal.Request'"""
            code: int = 3
            """
            0: Success, the request is carried out
            1: The user cancelled the interaction
            2: The user interaction was ended in some other way
            """

            uri: str = ''

        resp = Response()

        def process_response(response_code, results, main_loop=loop, response=resp):
            response.code = response_code
            if response_code == 0:
                response.uri = results['uri']
            main_loop.quit()

        request.onResponse = process_response

        loop.run()

        if resp.code == 0:
            if resp.uri.startswith('file:///'):
                arr = cv2.imread(resp.uri[len('file://'):])
                arr = cv2.cvtColor(arr, cv2.COLOR_BGR2BGRA)
                mon = {"left": 0, "top": 0, "width": arr.shape[1], "height": arr.shape[0]}
                return self.cls_image(arr.tobytes(), mon)
            raise ScreenShotError(f"Cannot open URI {resp.uri}")

        raise ScreenShotError(
            f"Screenshot Interaction ended unexpectedly with code {resp.code}"
        )

    def _monitors_impl(self):
        # type: () -> None
        # Wayland can only see one monitor?
        raise NotImplementedError()
