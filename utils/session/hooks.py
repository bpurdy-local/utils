from collections.abc import Callable

import requests

RequestHook = Callable[[requests.PreparedRequest], None]
ResponseHook = Callable[[requests.Response], None]


class HookManager:
    def __init__(self):
        self._request_hooks: list[RequestHook] = []
        self._response_hooks: list[ResponseHook] = []

    def add_request_hook(self, hook: RequestHook) -> None:
        self._request_hooks.append(hook)

    def add_response_hook(self, hook: ResponseHook) -> None:
        self._response_hooks.append(hook)

    def execute_request_hooks(self, request: requests.PreparedRequest) -> None:
        for hook in self._request_hooks:
            hook(request)

    def execute_response_hooks(self, response: requests.Response) -> None:
        for hook in self._response_hooks:
            hook(response)

    def clear_request_hooks(self) -> None:
        self._request_hooks.clear()

    def clear_response_hooks(self) -> None:
        self._response_hooks.clear()

    def clear_all_hooks(self) -> None:
        self.clear_request_hooks()
        self.clear_response_hooks()
