class Auth:

    def __init__(self, on_cookie: str, xsrf_cookie: str):
        self._on_cookie = on_cookie
        self._xsrf_cookie = xsrf_cookie

    @property
    def on_cookie(self) -> str:
        return self._on_cookie

    @property
    def xsrf_cookie(self) -> str:
        return self._xsrf_cookie
