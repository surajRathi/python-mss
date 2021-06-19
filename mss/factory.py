"""
This is part of the MSS Python's module.
Source: https://github.com/BoboTiG/python-mss
"""

import platform
from typing import TYPE_CHECKING

from .exception import ScreenShotError

if TYPE_CHECKING:
    from typing import Any  # noqa

    from .base import MSSBase  # noqa


def mss(**kwargs):
    # type: (Any) -> MSSBase
    """ Factory returning a proper MSS class instance.

        It detects the plateform we are running on
        and choose the most adapted mss_class to take
        screenshots.

        It then proxies its arguments to the class for
        instantiation.
    """
    # pylint: disable=import-outside-toplevel

    os_ = platform.system().lower()

    if os_ == "darwin":
        from . import darwin

        return darwin.MSS(**kwargs)

    if os_ == "linux":
        from os import environ
        if 'wayland' in environ.get('WAYLAND_DISPLAY', ''):
            from . import linux_wayland
            return linux_wayland.MSS(**kwargs)
        if ':' in environ.get('DISPLAY', ''):
            from . import linux
            return linux.MSS(**kwargs)

        raise ScreenShotError('Could not detect the display server, is DISPLAY or WAYLAND_DISPLAY set?')

    if os_ == "windows":
        from . import windows

        return windows.MSS(**kwargs)

    raise ScreenShotError("System {!r} not (yet?) implemented.".format(os_))
