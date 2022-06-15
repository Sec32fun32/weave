import shutil

from . import api as weave
from . import artifacts_local
from . import test_helpers
from .show import _show_params


def test_print_save_val():
    data = [
        {"val": 1941, "label": "cat"},
        {"val": 2195, "label": "dog"},
    ]
    ref = weave.save(data, name="my-data")
    # converting to string should give us an expression
    assert (
        str(ref)
        == 'get("local-artifact://%s/my-data/d0bff26d12fc15741c0c2bbbb5e533e9")'
        % artifacts_local.local_artifact_dir()
    )

    # show should use the same expression
    assert (
        str(_show_params(ref)["weave_node"])
        == 'get("local-artifact://%s/my-data/d0bff26d12fc15741c0c2bbbb5e533e9")'
        % artifacts_local.local_artifact_dir()
    )

    versions = weave.versions(ref)
    assert len(versions) == 1
    assert str(versions[0].version) == "d0bff26d12fc15741c0c2bbbb5e533e9"

    data = [
        {"val": 1941, "label": "cat"},
        {"val": 2195, "label": "dog"},
        {"val": 19, "label": "dog"},
    ]
    ref = weave.save(data, name="my-data")

    assert (
        str(ref)
        == 'get("local-artifact://%s/my-data/d1b57c599f4114978e882cb4544b4b4c")'
        % artifacts_local.local_artifact_dir()
    )
    assert (
        str(_show_params(ref)["weave_node"])
        == 'get("local-artifact://%s/my-data/d1b57c599f4114978e882cb4544b4b4c")'
        % artifacts_local.local_artifact_dir()
    )

    versions = weave.versions(ref)
    assert len(versions) == 2

    version_strings = [str(v.version) for v in versions]
    assert version_strings[0] == "d0bff26d12fc15741c0c2bbbb5e533e9"
    assert version_strings[1] == "d1b57c599f4114978e882cb4544b4b4c"


def test_save_val_ops():
    ref = weave.save(5, "my-num")
    result = (ref + 2) * 3
    assert (
        (str(result))
        == 'get("local-artifact://%s/my-num/3af13035d6c49b15d283b6b1482a7341").add(2).mult(3)'
        % artifacts_local.local_artifact_dir()
    )
