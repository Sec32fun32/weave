import os

from ..api import op, mutation, weave_class
from .. import weave_types as types
from .. import wandb_util
from . import arrow


_py_open = open


def path_ext(path):
    return os.path.splitext(path)[1].strip(".")


##### These are actually path ops, but they are called file for legacy reason


@op(
    name="file-dir",
    input_type={"file": types.DirType()},
    output_type=types.DirType(),
)
def file_dir(file):
    return file


##### End path ops


#### TODO: Table does not belong here!


class TableType(types.ObjectType):
    def property_types(self):
        return {"_rows": arrow.ArrowWeaveListType(types.TypedDict({}))}


@weave_class(weave_type=TableType)
class Table:
    def __init__(self, _rows):
        self._rows = _rows

    @op(
        name="table-rowsType",
        input_type={"table": TableType()},
        output_type=types.Type(),
    )
    def rows_type(table):
        ttype = types.TypeRegistry.type_of(table._rows)
        return ttype

    @op(
        name="table-rows",
        input_type={"table": types.WBTable()},
        output_type=arrow.ArrowWeaveListType(types.TypedDict({})),
    )
    def rows(table):
        return table._rows


@weave_class(weave_type=types.FileType)
class File:
    @op(
        name="file-table",
        input_type={"file": types.FileType()},
        output_type=TableType(),
    )
    def table(file):
        print("TABLE FILE", file)
        local_path = file.get_local_path()
        import json

        import time

        start_time = time.time()
        data = json.loads(_py_open(local_path).read())
        print("data columns", data["columns"])
        if len(data) > 0:
            print("data row0", data["data"][0])

        object_type = wandb_util.weave0_type_json_to_weave1_type(data["column_types"])
        print("Json parse time: %s" % (time.time() - start_time))
        start_time = time.time()
        # cols = zip(*data["data"])
        # named_cols = {col_name: col for col_name, col in zip(data["columns"], cols)}
        # print("Transpose time: %s" % (time.time() - start_time))
        # start_time = time.time()

        # TODO: this will need to recursively convert dicts to Objects in some
        # cases.
        rows = []
        for data_row in data["data"]:
            row = {}
            for col_name, val in zip(data["columns"], data_row):
                row[col_name] = val
                # if isinstance(val, dict) and val.get("_type") == "image-file":
                #     row[col_name] = imagefile.ImageFile(**val)
                # else:
                #     row[col_name] = val
            # row = {col_name: val for col_name, val in zip(data["columns"], data_row)}
            rows.append(row)
        from .. import storage

        print("Dicts time: %s" % (time.time() - start_time))
        start_time = time.time()

        print("Weave type:", object_type)
        print("PASSING ARTIFACT", file.artifact)
        res = storage.to_arrow_from_list_and_artifact(rows, object_type, file.artifact)
        print("Arrow time: %s" % (time.time() - start_time))
        start_time = time.time()
        # I Don't think I need Table now. We won't parse again
        return Table(res)

    @op(
        name="file-directUrlAsOf",
        input_type={"file": types.FileType(), "asOf": types.Int()},
        output_type=types.String(),
    )
    def direct_url_as_of(file, asOf):
        # TODO: This should depend on whether its local or an artifact
        #    etc
        local_path = os.path.abspath(file.get_local_path())
        return "http://localhost:9994/__weave/file/%s" % local_path

    @op(
        name="file-size", input_type={"file": types.FileType()}, output_type=types.Int()
    )
    def file_size(file):
        # file is an artifact manifest entry for now.
        return 10
        return file.size

    @mutation
    def file_contents_set(self, val):
        return self._file_contents_set(val)

    @op(
        setter=file_contents_set,
        name="file-contents",
        input_type={"file": types.FileType()},
        output_type=types.String(),
    )
    def file_contents(file):
        return file._contents()


types.FileType.instance_class = File
types.FileType.instance_classes = File


# Question, should all tables be lazy? That would mean we can serialize
#     and hand them between processes.... How would the user choose to
#     save a serialized version of a given table?


@op(name="file-type", input_type={"file": types.FileType()}, output_type=types.Type())
def file_type(file):
    # file is an artifact manifest entry for now.
    path = file.path
    parts = path.split(".")
    extension = None
    if len(parts) > 1:
        extension = parts[-1]
    result_type = {"type": "file", "extension": extension}
    if len(parts) > 2 and extension == "json":
        # TODO: validate. I'm sure there is existing logic for this in wandb
        result_type["wbObjectType"] = {
            "type": parts[-2],
        }
    return result_type


@weave_class(weave_type=types.SubDirType)
class SubDir(object):
    def __init__(self, fullPath, size, dirs, files):
        self.fullPath = fullPath
        self.size = size
        self.dirs = dirs
        self.files = files


types.SubDirType.instance_classes = SubDir
types.SubDirType.instance_class = SubDir


@weave_class(weave_type=types.DirType)
class Dir(object):
    def __init__(self, fullPath, size, dirs, files):
        self.fullPath = fullPath
        self.size = size
        self.dirs = dirs
        self.files = files

    def get_local_path(self):
        return self.path

    @op(name="dir-size", input_type={"dir": types.DirType()}, output_type=types.Int())
    def size(dir):
        return dir.size

    @op(
        name="dir-pathReturnType",
        input_type={"dir": types.DirType(), "path": types.String()},
        output_type=types.Type(),
    )
    def path_return_type(dir, path):
        return dir._path_return_type(path)

    @op(
        name="dir-path",
        input_type={"dir": types.DirType(), "path": types.String()},
        output_type=types.UnionType(types.FileType(), types.DirType(), types.none_type),
    )
    def open(dir, path):
        return dir._path(path)


types.DirType.instance_classes = Dir
types.DirType.instance_class = Dir
