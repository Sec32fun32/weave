from weave.flow.human_feedback import HumanAnnotationColumn
from weave.trace_server.trace_server_interface import ObjQueryReq


def test_human_feedback_basic(client):
    # create a human feedback spec

    col1 = HumanAnnotationColumn(
        name="Numerical field #1",
        description="A numerical field with a range of -1 to 1",
        json_schema={
            "type": "number",
            "min": -1,
            "max": 1,
        },
        unique_among_creators=True,
        op_scope=None,
    )
    ref1 = client.save(col1, "my numerical spec")
    assert ref1

    col2 = HumanAnnotationColumn(
        name="Text field #1",
        json_schema={"type": "string", "maxLength": 100},
        op_scope=["fake-op"],
    )
    ref2 = client.save(col2, "my text spec")
    assert ref2

    # query it by object type
    objects = client.server.objs_query(
        ObjQueryReq.model_validate(
            {
                "project_id": client._project_id(),
                "filter": {"base_object_classes": ["HumanAnnotationColumn"]},
            }
        )
    )

    assert len(objects.objs) == 2
    assert objects.objs[0].val["name"] == "Numerical field #1"
    assert objects.objs[1].val["name"] == "Text field #1"
    assert (
        objects.objs[0].val["description"]
        == "A numerical field with a range of -1 to 1"
    )
    assert not objects.objs[1].val["description"]
    assert not objects.objs[0].val["op_scope"]
    assert objects.objs[1].val["op_scope"] == ["fake-op"]
    assert objects.objs[0].val["json_schema"] == {
        "type": "number",
        "min": -1,
        "max": 1,
    }
    assert objects.objs[1].val["json_schema"] == {"type": "string", "maxLength": 100}
