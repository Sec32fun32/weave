# TODO: split this into multiple files like we do in the JS version
import json
import typing

from wandb.apis import public as wandb_api

from ..api import op, weave_class
from .. import weave_types as types
from . import wbartifact
from .. import errors
from .. import artifacts_local
from ..wandb_api import wandb_public_api


class ProjectType(types.Type):
    name = "project"
    instance_classes = wandb_api.Project
    instance_class = wandb_api.Project

    def instance_to_dict(self, obj):
        return {"entity_name": obj.entity, "project_name": obj.name}

    def instance_from_dict(self, d):
        api = wandb_public_api()
        return api.project(name=d["project_name"], entity=d["entity_name"])


class RunType(types.Type):
    name = "run"

    instance_classes = wandb_api.Run
    instance_class = wandb_api.Run

    def instance_to_dict(self, obj):
        return {
            "entity_name": obj._entity,
            "project_name": obj.project,
            "run_id": obj.id,
        }

    def instance_from_dict(self, d):
        import time

        print("%s: RUN INSTANCE FROM DICT" % time.time())
        api = wandb_public_api()
        res = api.run("{entity_name}/{project_name}/{run_id}".format(**d))
        print("%s: DONE RUN INSTANCE FROM DICT" % time.time())
        return res


class ArtifactType(types.Type):
    name = "artifact"
    instance_classes = wandb_api.ArtifactCollection
    instance_class = wandb_api.ArtifactCollection

    def instance_to_dict(self, obj):
        # TODO: I'm here, trying to serialize/deserialize Artifact
        return {
            "entity_name": obj.entity,
            "project_name": obj.project,
            "artifact_type_name": obj.type,
            "artifact_name": obj.name,
        }

    def instance_from_dict(self, d):
        api = wandb_public_api()
        return api.artifact_type(
            d["artifact_type_name"], project=f"{d['entity_name']}/{d['project_name']}"
        ).collection(d["artifact_name"])


class ArtifactVersionsType(types.Type):
    name = "projectArtifactVersions"
    instance_classes = wandb_api.ArtifactVersions
    instance_class = wandb_api.ArtifactVersions

    def instance_to_dict(self, obj):
        # TODO: I'm here, trying to serialize/deserialize Artifact
        return {
            "entity_name": obj.entity,
            "project_name": obj.project,
            "artifact_type_name": obj.type,
            "artifact_name": obj.collection_name,
        }

    def instance_from_dict(self, d):
        api = wandb_public_api()
        return api.artifact_versions(
            d["artifact_type_name"],
            f"{d['entity_name']}/{d['project_name']}/{d['artifact_name']}",
        )


@weave_class(weave_type=RunType)
class Run:
    @op()
    # @staticmethod  # TODO: doesn't work
    def jobtype(run: wandb_api.Run) -> str:
        return run.jobType


class RunsType(types.Type):
    name = "runs"

    instance_classes = wandb_api.Runs
    instance_class = wandb_api.Runs

    @property
    def object_type(self):
        return RunType()

    def instance_to_dict(self, obj):
        return {
            "entity_name": obj.entity,
            "project_name": obj.project,
        }

    def instance_from_dict(self, d):
        api = wandb_public_api()
        return api.runs("{entity_name}/{project_name}".format(**d), per_page=500)


@weave_class(weave_type=RunsType)
class RunsOps:
    @op()
    def count(self: wandb_api.Runs) -> int:
        return len(self)


class ArtifactsType(types.Type):
    name = "artifacts"
    instance_classes = wandb_api.ProjectArtifactCollections
    instance_class = wandb_api.ProjectArtifactCollections

    @property
    def object_type(self):
        return ArtifactType()

    def instance_to_dict(self, obj):
        return {
            "entity_name": obj.entity,
            "project_name": obj.project,
            "artifact_type_name": obj.type_name,
        }

    def instance_from_dict(self, d):
        api = wandb_public_api()
        return api.artifact_type(
            d["artifact_type_name"], project=f"{d['entity_name']}/{d['project_name']}"
        ).collections()


@weave_class(weave_type=ArtifactsType)
class ArtifactsOps:
    @op()
    def count(self: wandb_api.ProjectArtifactCollections) -> int:
        return len(self)

    @op()
    def __getitem__(
        self: wandb_api.ProjectArtifactCollections, index: int
    ) -> wandb_api.ArtifactCollection:
        return self[index]


@weave_class(weave_type=ArtifactVersionsType)
class ArtifactVersionsOps:
    @op()
    def count(self: wandb_api.ArtifactVersions) -> int:
        return len(self)

    @op()
    def __getitem__(
        self: wandb_api.ArtifactVersions, index: int
    ) -> artifacts_local.WandbArtifact:
        wb_artifact = self[index]
        return artifacts_local.WandbArtifact.from_wb_artifact(wb_artifact)


class ArtifactTypeType(types.Type):
    name = "artifactType"
    instance_classes = wandb_api.ArtifactType
    instance_class = wandb_api.ArtifactType

    def instance_to_dict(self, obj):
        # TODO: I'm here, trying to serialize/deserialize Artifact
        return {
            "entity_name": obj.entity,
            "project_name": obj.project,
            "artifact_type_name": obj.type,
        }

    def instance_from_dict(self, d):
        api = wandb_public_api()
        return api.artifact_type(
            d["artifact_type_name"], project=f"{d['entity_name']}/{d['project_name']}"
        )


@weave_class(weave_type=ArtifactTypeType)
class ArtifactTypeOps:
    @op(name="artifactType-name")
    def name(artifactType: wandb_api.ArtifactType) -> str:
        # Hacking to support mapped call here. WeaveJS autosuggest uses it
        # TODO: True mapped call support
        if isinstance(artifactType, wandb_api.ProjectArtifactTypes):
            return [at.name for at in artifactType]  # type: ignore
        return artifactType.type

    @op(name="artifactType-artifacts")
    def artifacts(
        artifactType: wandb_api.ArtifactType,
    ) -> wandb_api.ProjectArtifactCollections:
        return artifactType.collections()


class ProjectArtifactTypesType(types.Type):
    name = "projectArtifactTypes"

    instance_classes = wandb_api.ProjectArtifactTypes
    instance_class = wandb_api.ProjectArtifactTypes

    @property
    def object_type(self):
        return RunType()

    def instance_to_dict(self, obj):
        return {
            "entity_name": obj.entity,
            "project_name": obj.project,
        }

    def instance_from_dict(self, d):
        api = wandb_public_api()
        return api.project("{entity_name}/{project_name}".format(**d)).artifacts_types()


@weave_class(weave_type=ArtifactType)
class ArtifactOps:
    @op(name="artifact-type")
    def type_(artifact: wandb_api.ArtifactCollection) -> wandb_api.ArtifactType:
        api = wandb_public_api()
        return api.artifact_type(
            artifact.type, project=f"{artifact.entity}/{artifact.project}"
        )

    # :( Since we mixin with nodes (include VarNode), name collides.
    # TODO: Fix this is no good.
    @op(name="artifact-name")
    def name_(artifact: wandb_api.ArtifactCollection) -> str:
        return artifact.name

    @op(name="artifact-versions")
    def versions(artifact: wandb_api.ArtifactCollection) -> wandb_api.ArtifactVersions:
        return artifact.versions()


@weave_class(weave_type=ProjectType)
class Project:
    @op()
    # @staticmethod  # TODO: doesn't work
    def name(project: wandb_api.Project) -> str:
        return project.name

    @op()
    def artifacts(
        project: wandb_api.Project,
    ) -> typing.List[wandb_api.ArtifactCollection]:
        api = wandb_public_api()
        return api.artifact_type(
            "test_results", project=f"{project.entity}/{project.name}"
        ).collections()

    @op(name="project-artifactTypes")
    def artifact_types(project: wandb_api.Project) -> wandb_api.ProjectArtifactTypes:
        return project.artifacts_types()

    @op(name="project-artifactType")
    def artifact_type(
        project: wandb_api.Project, artifactType: str
    ) -> wandb_api.ArtifactType:
        api = wandb_public_api()
        return api.artifact_type(
            artifactType, project=f"{project.entity}/{project.name}"
        )

    @op(name="project-artifactVersion")
    def artifact_version(
        project: wandb_api.Project, artifactName: str, artifactVersionAlias: str
    ) -> artifacts_local.WandbArtifact:
        wb_artifact = wandb_public_api().artifact(
            "%s/%s/%s:%s"
            % (project.entity, project.name, artifactName, artifactVersionAlias)
        )
        return artifacts_local.WandbArtifact.from_wb_artifact(wb_artifact)

    @op()
    def runs(project: wandb_api.Project) -> wandb_api.Runs:
        import wandb

        api = wandb.Api()
        return api.runs(path="%s/%s" % (project.entity, project.name), per_page=500)

    @op(name="project-filtered-runs")
    def filtered_runs(
        project: wandb_api.Project, filter: typing.Any, order: str
    ) -> wandb_api.Runs:
        import wandb

        api = wandb.Api()
        return api.runs(
            path="%s/%s" % (project.entity, project.name),  # type: ignore
            filters=json.loads(filter),
            order=order,
            per_page=500,
        )


@op(name="root-project")
def project(entityName: str, projectName: str) -> wandb_api.Project:
    return wandb_public_api().project(name=projectName, entity=entityName)
