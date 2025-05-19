"""Stream type classes for tap-canvas-career."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_canvas_career.client import CanvasCareerStream
from requests_toolbelt.multipart.encoder import MultipartEncoder
import requests

from typing import cast
import time
import csv

class GradesStream(CanvasCareerStream):
    """Define custom stream."""
    name = "grades"
    path = "/reports/grade_export_csv"
    primary_keys = None
    replication_key = None
    rest_method = "POST"

    schema = th.PropertiesList(
        th.Property("student name", th.StringType),
        th.Property("student id", th.StringType),
        th.Property("student sis", th.StringType),
        th.Property("course", th.StringType),
        th.Property("course id", th.StringType),
        th.Property("course sis", th.StringType),
        th.Property("section", th.StringType),
        th.Property("section id", th.StringType),
        th.Property("section sis", th.StringType),
        th.Property("term", th.StringType),
        th.Property("term id", th.StringType),
        th.Property("term sis", th.StringType),
        th.Property("current score", th.StringType),
        th.Property("final score", th.StringType),
        th.Property("enrollment state", th.StringType),
        th.Property("unposted current score", th.StringType),
        th.Property("unposted final score", th.StringType),
        th.Property("current grade", th.StringType),
        th.Property("final grade", th.StringType),
        th.Property("unposted current grade", th.StringType),
        th.Property("unposted final grade", th.StringType),
    ).to_dict()

    def prepare_request_payload(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Optional[dict]:
        """Prepare the data payload for the REST API request.

        By default, no payload will be sent (return None).
        """
        multipart_data = MultipartEncoder(
            fields={
                'parameters[include_deleted]': "false",
                'parameters[skip_message]': "true",
            }
        )
        return multipart_data
    
    def prepare_request(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> requests.PreparedRequest:
        http_method = self.rest_method
        url: str = self.get_url(context)
        params: dict = self.get_url_params(context, next_page_token)
        request_data = self.prepare_request_payload(context, next_page_token)
        headers = self.http_headers

        authenticator = self.authenticator
        if authenticator:
            headers.update(authenticator.auth_headers or {})
            params.update(authenticator.auth_params or {})

        request = cast(
            requests.PreparedRequest,
            self.requests_session.prepare_request(
                requests.Request(
                    method=http_method,
                    url=url,
                    params=params,
                    headers=headers,
                    data=request_data,
                ),
            ),
        )
        return request
    
    def check_report_status(self, report_id: str) -> bool:
        headers = self.http_headers
        authenticator = self.authenticator
        if authenticator:
            headers.update(authenticator.auth_headers or {})


        request = cast(
            requests.PreparedRequest,
            self.requests_session.prepare_request(
                requests.Request(
                    method="GET",
                    url=f"{self.get_url({})}/{report_id}",
                    headers=headers,
                ),
            ),
        )

        self.logger.info(f"Checking report status for {report_id}")
        decorated_request = self.request_decorator(self._request)
        response = decorated_request(request, {})
        return response.json()
    
    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        res_json = response.json()

        # check if the report is ready
        status = self.check_report_status(res_json["id"])
        while status["status"] == "created":
            self.logger.info(f"Report {res_json['id']} isn't completed yet, waiting for 5 seconds...")
            time.sleep(5)
            status = self.check_report_status(res_json["id"])

        if status["status"] != "complete":
            raise Exception(f"Report {res_json['id']} failed to complete, response: {status}")

        # if report completed succesfully, download csv file and yield rows
        self.logger.info(f"Report {res_json['id']} completed successfully, processing data...")
        url = status["attachment"]["url"]
        response = requests.get(url)
        csv_content = response.content.decode('utf-8')
        reader = csv.DictReader(csv_content.splitlines())
        yield from reader