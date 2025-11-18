import concurrent.futures
from typing import Any

import requests


class BatchRequest:
    def __init__(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ):
        self.method = method.upper()
        self.url = url
        self.params = params
        self.data = data
        self.json = json
        self.headers = headers
        self.kwargs = kwargs

    @classmethod
    def get(cls, url: str, **kwargs: Any) -> "BatchRequest":
        return cls("GET", url, **kwargs)

    @classmethod
    def post(cls, url: str, **kwargs: Any) -> "BatchRequest":
        return cls("POST", url, **kwargs)

    @classmethod
    def put(cls, url: str, **kwargs: Any) -> "BatchRequest":
        return cls("PUT", url, **kwargs)

    @classmethod
    def delete(cls, url: str, **kwargs: Any) -> "BatchRequest":
        return cls("DELETE", url, **kwargs)

    @classmethod
    def patch(cls, url: str, **kwargs: Any) -> "BatchRequest":
        return cls("PATCH", url, **kwargs)


class BatchExecutor:
    def __init__(self, session: requests.Session, *, max_workers: int = 10):
        self.session = session
        self.max_workers = max_workers

    def execute(
        self, *request_groups: BatchRequest | list[BatchRequest]
    ) -> list[requests.Response]:
        flattened_requests = self._flatten_request_groups(request_groups)

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(self._execute_single_request, request)
                for request in flattened_requests
            ]

            responses = [future.result() for future in futures]

        return responses

    def _flatten_request_groups(
        self, request_groups: tuple[BatchRequest | list[BatchRequest], ...]
    ) -> list[BatchRequest]:
        flattened = []

        for group in request_groups:
            if isinstance(group, list):
                flattened.extend(group)
            else:
                flattened.append(group)

        return flattened

    def _execute_single_request(self, batch_request: BatchRequest) -> requests.Response:
        request_kwargs = {
            "params": batch_request.params,
            "data": batch_request.data,
            "json": batch_request.json,
            "headers": batch_request.headers,
            **batch_request.kwargs,
        }

        request_kwargs = {key: value for key, value in request_kwargs.items() if value is not None}

        return self.session.request(batch_request.method, batch_request.url, **request_kwargs)
