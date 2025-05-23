"""REST client handling, including CanvasCareerStream base class."""

import requests
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable, Callable

from memoization import cached

from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream

from tap_canvas_career.auth import CanvasCareerAuthenticator

from http.client import RemoteDisconnected
from requests.exceptions import ConnectionError

from singer_sdk.exceptions import RetriableAPIError
import backoff


class CanvasCareerStream(RESTStream):
    """CanvasCareer stream class."""

    @property
    def url_base(self) -> str:
        return f"https://{self.config.get('base_url')}/api/v1/accounts/{self.config.get('account_id')}"

    records_jsonpath = "$[*]"  # Or override `parse_response`.

    @property
    def authenticator(self) -> CanvasCareerAuthenticator:
        oauth_url = f"https://{self.config.get('base_url')}/login/oauth2/token"
        return CanvasCareerAuthenticator(self, self.config, auth_endpoint=oauth_url)

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        return headers

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        return {}

    def request_decorator(self, func: Callable) -> Callable:
        decorator: Callable = backoff.on_exception(
            self.backoff_wait_generator,
            (
                RetriableAPIError,
                requests.exceptions.ReadTimeout,
                ConnectionError,
                RemoteDisconnected,
            ),
            max_tries=8,
            on_backoff=self.backoff_handler,
        )(func)
        return decorator
