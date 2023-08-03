import atexit
import json
import queue
import threading
import typing
import uuid

from wandb import errors
from wandb.sdk.artifacts.artifact import Artifact

from .lib.ipython import _get_python_type
from .lib.printer import get_printer
from .wandb_lite_run import InMemoryLazyLiteRun, wandb_public_api

ROW_TYPE = typing.Union[dict, typing.List[dict]]


class _StreamTableSync:
    _lite_run: InMemoryLazyLiteRun
    _table_name: str
    _project_name: str
    _entity_name: str

    _artifact: typing.Optional["Artifact"]

    _weave_stream_table: typing.Any
    _weave_stream_table_ref: typing.Any

    _client_id: str

    def __init__(
        self,
        table_name: str,
        *,
        config: typing.Optional[dict] = None,
        project_name: typing.Optional[str] = None,
        entity_name: typing.Optional[str] = None,
        hidden: bool = True,
    ):
        self._client_id = str(uuid.uuid1())
        self._lock = threading.Lock()
        self._artifact = None
        splits = table_name.split("/")
        if len(splits) == 1:
            pass
        elif len(splits) == 2:
            if project_name is not None:
                raise ValueError(
                    f"Cannot specify project_name and table_name with '/' in it: {table_name}"
                )
            project_name = splits[0]
            table_name = splits[1]
        elif len(splits) == 3:
            if project_name is not None or entity_name is not None:
                raise ValueError(
                    f"Cannot specify project_name or entity_name and table_name with 2 '/'s in it: {table_name}"
                )
            entity_name = splits[0]
            project_name = splits[1]
            table_name = splits[2]

        # For now, we force the user to specify the entity and project
        # technically, we could infer the entity from the API key, but
        # that tends to confuse users.
        if entity_name is None or entity_name == "":
            raise ValueError("Must specify entity_name")
        elif project_name is None or project_name == "":
            raise ValueError("Must specify project_name")
        elif table_name is None or table_name == "":
            raise ValueError("Must specify table_name")

        self._lite_run = InMemoryLazyLiteRun(
            entity_name,
            project_name,
            table_name,
            config=config,
            group="weave_stream_tables",
            _hide_in_wb=hidden,
        )
        if not wandb_public_api().supports_streamtable:
            raise errors.Error(
                "Streamtable isn't supported in this version of wandb.  Contact your adminstrator to upgrade."
            )
        self._table_name = self._lite_run._run_name
        self._project_name = self._lite_run._project_name
        self._entity_name = self._lite_run._entity_name
        self._ensure_remote_initialized()
        atexit.register(self._at_exit)

    def _ensure_remote_initialized(self) -> None:
        with self._lock:
            self._lite_run.ensure_run()
            print_url = False
            self._artifact = self._stream_table_artifact()
            if print_url:
                base_url = wandb_public_api().settings["base_url"]
                if base_url.endswith("api.wandb.ai"):
                    base_url = base_url.replace("api", "weave.")
                url = f"{base_url}/?exp=get%28%0A++++%22wandb-artifact%3A%2F%2F%2F{self._entity_name}%2F{self._project_name}%2F{self._table_name}%3Alatest%2Fobj%22%29%0A++.rows"
                printer = get_printer(_get_python_type() != "python")
                printer.display(
                    f'{printer.emoji("star")} View data at {printer.link(url)}'
                )

    def _stream_table_artifact(self) -> "Artifact":
        if self._artifact is None:
            self._artifact = Artifact(
                self._table_name,
                type="stream_table",
                metadata={
                    "_weave_meta": {
                        "is_panel": False,
                        "is_weave_obj": True,
                        "type_name": "stream_table",
                    },
                },
            )
            with self._artifact.new_file("obj.object.json") as f:
                payload = {
                    "_type": "stream_table",
                    "table_name": self._table_name,
                    "project_name": self._project_name,
                    "entity_name": self._entity_name,
                }
                f.write(json.dumps(payload))
            with self._artifact.new_file("obj.type.json") as f:
                payload = {
                    "type": "stream_table",
                    "_base_type": {"type": "Object"},  # type: ignore[dict-item]
                    "_is_object": True,  # type: ignore[dict-item]
                    "table_name": "string",
                    "project_name": "string",
                    "entity_name": "string",
                }
                f.write(json.dumps(payload))
            self._lite_run.log_artifact(self._artifact)
        return self._artifact

    def log(self, row_or_rows: ROW_TYPE) -> None:
        if isinstance(row_or_rows, dict):
            row_or_rows = [row_or_rows]

        for row in row_or_rows:
            self._log_row(row)

    def rows(self) -> None:
        raise errors.Error(
            "reading stream tables is not supported in wandb, use weave.StreamTable"
        )

    def _log_row(self, row: dict) -> None:
        row_copy = {**row}
        row_copy["_client_id"] = self._client_id
        self._lite_run.log(row_copy)

    def finish(self) -> None:
        with self._lock:
            if self._artifact:
                self._artifact.cleanup()
            if self._lite_run:
                self._lite_run.finish()

    def __del__(self) -> None:
        try:
            self.finish()
        except Exception:
            # I was seeing exceptions in yea tests, this prevents
            # ignored exception warnings
            pass

    def _at_exit(self) -> None:
        self.finish()


class StreamTable(_StreamTableSync):
    MAX_UNSAVED_SECONDS = 2

    def __init__(
        self,
        table_name: str,
        *,
        config: typing.Optional[dict] = None,
        project_name: typing.Optional[str] = None,
        entity_name: typing.Optional[str] = None,
        hidden: bool = True,
    ):
        super().__init__(
            table_name=table_name,
            project_name=project_name,
            entity_name=entity_name,
            config=config,
            hidden=hidden,
        )

        self.queue: queue.Queue = queue.Queue()
        self._join_event = threading.Event()
        self._thread = threading.Thread(target=self._thread_body)
        self._thread.daemon = True
        self._thread.start()

    def log(self, row_or_rows: ROW_TYPE) -> None:
        self.queue.put(row_or_rows)

    def _flush(self) -> None:
        with self._lock:
            for log_payload in self._iterate_queue():
                super().log(log_payload)

    def _iterate_queue(
        self,
    ) -> typing.Generator[ROW_TYPE, None, None]:
        while True:
            try:
                record = self.queue.get_nowait()
            except queue.Empty:
                break
            else:
                yield record
                self.queue.task_done()

    def _thread_body(self) -> None:
        join_requested = False
        while not join_requested:
            join_requested = self._join_event.wait(self.MAX_UNSAVED_SECONDS)
            self._flush()

    # Override methods of _StreamTableSync
    def finish(self) -> None:
        if hasattr(self, "_thread"):
            self._join_event.set()
            self._thread.join()
            super().finish()
