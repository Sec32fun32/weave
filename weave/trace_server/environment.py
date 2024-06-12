import os


def wf_clickhouse_host() -> str:
    """The host of the clickhouse server."""
    return os.environ.get("WF_CLICKHOUSE_HOST", "localhost")


def wf_clickhouse_port() -> int:
    """The port of the clickhouse server."""
    return int(os.environ.get("WF_CLICKHOUSE_PORT", 8123))


def wf_clickhouse_user() -> str:
    """The user of the clickhouse server."""
    return os.environ.get("WF_CLICKHOUSE_USER", "default")


def wf_clickhouse_pass() -> str:
    """The password of the clickhouse server."""
    return os.environ.get("WF_CLICKHOUSE_PASS", "")


def wf_clickhouse_database() -> str:
    """The name of the clickhouse database."""
    return os.environ.get("WF_CLICKHOUSE_DATABASE", "default")


def wf_trace_server_url() -> str:
    """The url of the web server exposing the trace interface endpoints"""
    return os.environ.get("WF_TRACE_SERVER_URL", "https://trace.wandb.ai")


# todo: move to a better place
def wandb_api_key() -> str:
    return os.getenv("WANDB_API_KEY", "")
