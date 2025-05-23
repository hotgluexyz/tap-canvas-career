"""CanvasCareer tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th
from tap_canvas_career.streams import (
    GradesStream,
)


STREAM_TYPES = [
    GradesStream,
]


class TapCanvasCareer(Tap):
    """CanvasCareer tap class."""

    def __init__(
        self,
        config=None,
        catalog=None,
        state=None,
        parse_env_config=False,
        validate_config=True,
    ) -> None:
        self.config_file = config[0]
        super().__init__(config, catalog, state, parse_env_config, validate_config)

    name = "tap-canvas-career"

    config_jsonschema = th.PropertiesList(
        th.Property("base_url", th.StringType, required=True),
        th.Property("client_id", th.StringType, required=True),
        th.Property("client_secret", th.StringType, required=True),
        th.Property("account_id", th.StringType, required=True),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


if __name__ == "__main__":
    TapCanvasCareer.cli()
