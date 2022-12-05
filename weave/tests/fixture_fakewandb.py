import os
import pytest
import shutil
from unittest import mock

from .. import artifacts_local
from .. import ops_domain
from .. import wandb_api
from ..ops_domain import wandb_domain_gql

TEST_TABLE_ARTIFACT_PATH = "testdata/wb_artifacts/test_res_1fwmcd3q:v0"
ABS_TEST_TABLE_ARTIFACT_PATH = os.path.abspath(TEST_TABLE_ARTIFACT_PATH)


class FakeProject:
    entity = "stacey"
    name = "mendeleev"


class FakeEntry:
    pass


class FakeManifest:
    entries = {"fakePath": FakeEntry()}

    def get_entry_by_path(self, path):
        if path == "test_results.table.json":
            return FakeEntry()
        if path == "media/images/8f65e54dc684f7675aec.png":
            return FakeEntry()
        if path == "weird_table.table.json":
            return FakeEntry()
        # Otherwise, file is missing, return None.
        return None

    def get_entries_in_directory(self, cur_dir):
        return []


class FakePath:
    def __init__(self, path):
        self.path = path

    def download(self):
        return self.path


class FakeVersion:
    entity = "stacey"
    project = "mendeleev"
    _sequence_name = "test_res_1fwmcd3q"
    version = "v0"
    name = "test_res_1fwmcd3q:v0"

    manifest = FakeManifest()

    def get_path(self, path):
        full_artifact_dir = os.path.join(
            artifacts_local.wandb_artifact_dir(), TEST_TABLE_ARTIFACT_PATH
        )
        full_artifact_path = os.path.join(full_artifact_dir, path)
        os.makedirs(os.path.dirname(full_artifact_path), exist_ok=True)
        artifact_path = os.path.join(ABS_TEST_TABLE_ARTIFACT_PATH, path)
        shutil.copy2(artifact_path, full_artifact_path)
        return FakePath(artifact_path)

    def download(self):
        pass


class FakeVersions:
    __getitem__ = mock.Mock(return_value=FakeVersion())

    def __iter__(self):
        return iter([FakeVersion()])


class FakeArtifact:
    versions = mock.Mock(return_value=FakeVersions())
    entity = "stacey"
    project = "mendeleev"
    name = "test_res_1fwmcd3q"


class FakeArtifacts:
    __getitem__ = mock.Mock(return_value=FakeArtifact())

    def __iter__(self):
        return iter([FakeArtifact()])


class FakeArtifactType:
    # "collections" should be called "artifacts" in the wandb API
    collections = mock.Mock(return_value=FakeArtifacts())


class FakeSummary:
    _json_dict = {
        "table": {
            "_type": "table-file",
            "artifact_path": "wandb-client-artifact://1234567890/test_results.table.json",
        }
    }


class FakeRun:
    entity = "stacey"
    project = "mendeleev"
    id = "test_run_id"
    name = "test_run_name"
    summary = FakeSummary()


class FakeRuns:
    __getitem__ = mock.Mock(return_value=FakeRun())

    def __iter__(self):
        return iter([FakeRun()])


class FakeClient:
    def execute(self, gql, variable_values):
        if gql.definitions[0].operation == "query":
            if (
                gql.definitions[0].name.value
                == "artifact_collection_membership_for_alias"
            ):
                return {
                    "project": {
                        "artifactCollection": {
                            "artifactMembership": {
                                "commitHash": "xyz",
                                "versionIndex": "0",
                            }
                        }
                    }
                }
            elif (
                gql.definitions[0].name.value == "ArtifactCollection"
            ):  # this is for public.py::ArtifactCollection.load
                return {"project": {"artifactType": {"artifactSequence": {"id": 1001}}}}
            elif gql.definitions[0].name.value == "ArtifactVersionFromClientId":
                return {
                    "artifact": {
                        "versionIndex": 0,
                        "artifactType": {
                            "id": 1,
                            "name": "test_data",
                        },
                        "artifactSequence": {
                            "id": 1,
                            "name": "test_res_1fwmcd3q",
                            "project": {
                                "id": 1,
                                "name": "mendeleev",
                                "entity": {
                                    "id": 1,
                                    "name": "stacey",
                                },
                            },
                        },
                    }
                }

        raise Exception(
            "Query was not mocked - please fill out in fixture_fakewandb.py"
        )


class FakeApi:
    client = FakeClient()
    project = mock.Mock(return_value=FakeProject())
    artifact_type = mock.Mock(return_value=FakeArtifactType())
    artifact = mock.Mock(return_value=FakeVersion())
    runs = mock.Mock(return_value=FakeRuns())
    run = mock.Mock(return_value=FakeRun())


fake_api = FakeApi()


def wandb_public_api():
    return fake_api


def setup():
    old_wandb_api_wandb_public_api = wandb_api.wandb_public_api
    wandb_api.wandb_public_api = wandb_public_api
    old_wandb_domain_gql_wandb_public_api = wandb_domain_gql.wandb_public_api
    wandb_domain_gql.wandb_public_api = wandb_public_api
    return (
        old_wandb_api_wandb_public_api,
        old_wandb_domain_gql_wandb_public_api,
    )


def teardown(setup_response):
    wandb_api.wandb_public_api = setup_response[0]
    wandb_domain_gql.wandb_public_api = setup_response[1]
