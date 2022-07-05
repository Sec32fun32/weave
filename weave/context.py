import contextvars
import os
import contextlib
import logging
import typing
from urllib.parse import urljoin

from . import client
from . import server
from . import util
from . import uris


# Set to the op uri if we're in the process of loading
# an op from an artifact.
_loading_op_location: contextvars.ContextVar[
    typing.Optional[uris.WeaveURI]
] = contextvars.ContextVar("loading_op_location", default=None)


# Set to true if we're in the process of loading builtin functions
# this prevents us from storing the op as an artifact
_loading_built_ins: contextvars.ContextVar[
    typing.Optional[bool]
] = contextvars.ContextVar("loading_builtins", default=False)


@contextlib.contextmanager
def loading_op_location(location):
    token = _loading_op_location.set(location)
    yield _loading_op_location.get()
    _loading_op_location.reset(token)


def get_loading_op_location():
    return _loading_op_location.get()


def set_loading_built_ins():
    return _loading_built_ins.set(True)


def clear_loading_built_ins(token):
    _loading_built_ins.reset(token)


def get_loading_built_ins():
    return _loading_built_ins.get()


_weave_client: contextvars.ContextVar[
    typing.Optional[client.Client]
] = contextvars.ContextVar("weave_client", default=None)

_http_server: contextvars.ContextVar[
    typing.Optional[server.HttpServer]
] = contextvars.ContextVar("http_server", default=None)

_frontend_url: contextvars.ContextVar[typing.Optional[str]] = contextvars.ContextVar(
    "frontend_url", default=None
)

_analytics_enabled: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "analytics_enabled", default=True
)

_eager_mode: contextvars.ContextVar[bool] = contextvars.ContextVar(
    "_eager_mode", default=False
)

_wandb_api_key: contextvars.ContextVar[typing.Optional[str]] = contextvars.ContextVar(
    "_wandb_api_key", default=None
)

_cache_namespace_token: contextvars.ContextVar[
    typing.Optional[str]
] = contextvars.ContextVar("_cache_namespace_token", default=None)


@contextlib.contextmanager
def execution_client():
    """Returns a client for use by the execution engine and op resolvers."""
    # Force in process execution
    wc = client.Client(server.InProcessServer())
    client_token = _weave_client.set(wc)
    # eager_token = _eager_mode.set(True)
    # Disable analytics
    analytics_token = _analytics_enabled.set(False)
    try:
        yield wc
    finally:
        _analytics_enabled.reset(analytics_token)
        # _eager_mode.reset(eager_token)
        _weave_client.reset(client_token)


@contextlib.contextmanager
def local_http_client():
    s = server.HttpServer()
    s.start()
    server_token = _http_server.set(s)
    client_token = _weave_client.set(server.HttpServerClient(s.url))
    try:
        yield _weave_client.get()
    finally:
        _weave_client.reset(client_token)
        _http_server.reset(server_token)


@contextlib.contextmanager
def weavejs_client():
    s = server.HttpServer()
    s.start()
    server_token = _http_server.set(s)
    client_token = _weave_client.set(
        server.HttpServerClient(s.url, emulate_weavejs=True)
    )
    try:
        yield _weave_client.get()
    finally:
        _weave_client.reset(client_token)
        _http_server.reset(server_token)


@contextlib.contextmanager
def eager_execution():
    eager_token = _eager_mode.set(True)
    try:
        yield
    finally:
        _eager_mode.reset(eager_token)


@contextlib.contextmanager
def lazy_execution():
    eager_token = _eager_mode.set(False)
    try:
        yield
    finally:
        _eager_mode.reset(eager_token)


def _make_default_client():
    if util.is_notebook():
        serv = _http_server.get()
        if serv is None:
            serv = server.HttpServer()
            serv.start()
            _http_server.set(serv)

    # we are returning a client that does not talk to the http server we just created because
    # the http server only communicates with the frontend. we create it above so that there is
    # a running server for the frontend to talk to as soon as we call use() or show().
    # python code can use the in process server by default.
    return client.Client(server.InProcessServer())


def use_fixed_server_port():
    """Force Weave server to port 9994 so wandb frontend can talk to it."""
    # s = server.HttpServer(port=9994)
    # s.start()
    # _weave_client.set(server.HttpServerClient(s.url))
    _weave_client.set(server.HttpServerClient("http://localhost:9994"))


def use_frontend_devmode():
    """Talk to external server running on 9994"""
    use_fixed_server_port()

    # point frontend to vite server
    _frontend_url.set("http://localhost:3000")


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
        client = get_client()
        if isinstance(client, server.HttpServerClient):
            url = client.url
        else:
            s = _http_server.get()
            if s is not None:
                url = s.url
            else:
                raise RuntimeError("Frontend server is not running")
        url += "/__frontend/weave_jupyter"
    return url


def eager_mode():
    return _eager_mode.get()


def analytics_enabled():
    return _analytics_enabled.get()


def disable_analytics():
    return _analytics_enabled.set(False)
