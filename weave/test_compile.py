from .ecosystem import async_demo
from . import compile
from . import artifacts_local


def test_automatic_await_compile():
    twelve = async_demo.slowmult(3, 4, 0.01)
    twenty_four = async_demo.slowmult(2, twelve, 0.01)
    result = compile.compile([twenty_four])
    assert str(result[0]) == "2.slowmult(slowmult(3, 4, 0.01).await(), 0.01)"
