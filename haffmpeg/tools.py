"""For HA varios tools."""
import asyncio
import logging

import async_timeout

from .core import HAFFmpeg

_LOGGER = logging.getLogger(__name__)

IMAGE_JPEG = 'mjpeg'
IMAGE_PNG = 'png'


class ImageFrame(HAFFmpeg):
    """Implement a single image caputre from a stream."""

    async def get_image(self, input_source, output_format=IMAGE_JPEG,
                        extra_cmd=None, timeout=15):
        """Open FFmpeg process as capture 1 frame."""
        command = [
            "-an",
            "-frames:v",
            "1",
            "-c:v",
            output_format,
        ]

        # open input for capture 1 frame
        is_open = await self.open(
            cmd=command, input_source=input_source, output="-f image2pipe -",
            extra_cmd=extra_cmd)

        # error after open?
        if not is_open:
            _LOGGER.warning("Error starting FFmpeg.")
            return None

        # read image
        try:
            with async_timeout.timeout(timeout, loop=self._loop):
                image, _ = await self._proc.communicate()

            return image

        except (asyncio.TimeoutError, ValueError):
            _LOGGER.warning("Timeout reading image.")
            self._proc.kill()
            return None
