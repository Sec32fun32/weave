import contextvars
import contextlib
import logging
import typing

from . import client
from . import server
from . import util


_weave_client: contextvars.ContextVar[
    typing.Optional[client.Client]
] = contextvars.ContextVar("weave_client", default=None)

_frontend_url: contextvars.ContextVar[typing.Optional[str]] = contextvars.ContextVar(
    "frontend_url", default=None
)


_analytics_enabled: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "analytics_enabled", default=True
)


@contextlib.contextmanager
def execution_client():
    """Returns a client for use by the execution engine and op resolvers."""
    # Force in process execution
    wc = client.Client(server.InProcessServer())
    client_token = _weave_client.set(wc)
    # Disable analytics
    analytics_token = _analytics_enabled.set(False)
    yield wc
    _weave_client.reset(client_token)
    _analytics_enabled.reset(analytics_token)


@contextlib.contextmanager
def local_http_client():
    s = server.HttpServer()
    s.start()
    client_token = _weave_client.set(server.HttpServerClient(s.url))
    yield _weave_client.get()
    _weave_client.reset(client_token)


def _make_default_client():
    if util.is_notebook():
        s = server.HttpServer()
        s.start()
        return server.HttpServerClient(s.url)
    else:
        return client.Client(server.InProcessServer())


def use_fixed_server_port():
    """Force Weave server to port 9994 so wandb frontend can talk to it."""
    s = server.HttpServer(port=9994)
    s.start()
    _weave_client.set(server.HttpServerClient(s.url))


def use_frontend_devmode():
    """Talk to external server running on 9994"""
    _weave_client.set(server.HttpServerClient("http://localhost:9994"))
    _frontend_url.set("https://app.wandb.test")


def capture_weave_server_logs(log_level=logging.INFO):
    from . import weave_server

    weave_server.enable_stream_logging(log_level)


def get_client():
    c = _weave_client.get()
    if c is None:
        c = _make_default_client()
        _weave_client.set(c)
    return c


def get_frontend_url():
    url = _frontend_url.get()
    if url is None:
        url = get_client().url
    return url


def analytics_enabled():
    return _analytics_enabled.get()


def disable_analytics():
    return _analytics_enabled.set(False)
