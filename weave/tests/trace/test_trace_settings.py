import io
import os
import sys
import timeit

import weave
from weave.trace.constants import TRACE_CALL_EMOJI
from weave.trace.settings import UserSettings, parse_and_apply_settings


@weave.op
def func():
    return 1


def test_disabled_setting(client):
    parse_and_apply_settings(UserSettings(disabled=True))
    disabled_time = timeit.timeit(func, number=10)

    parse_and_apply_settings(UserSettings(disabled=False))
    enabled_time = timeit.timeit(func, number=10)

    assert (
        disabled_time * 10 < enabled_time
    ), "Disabled weave should be faster than enabled weave"


def test_disabled_env(client):
    os.environ["WEAVE_DISABLED"] = "true"
    disabled_time = timeit.timeit(func, number=10)

    os.environ["WEAVE_DISABLED"] = "false"
    enabled_time = timeit.timeit(func, number=10)

    assert (
        disabled_time * 10 < enabled_time
    ), "Disabled weave should be faster than enabled weave"


def test_print_call_link_setting(client):
    captured_stdout = io.StringIO()
    sys.stdout = captured_stdout

    parse_and_apply_settings(UserSettings(print_call_link=False))
    func()

    output = captured_stdout.getvalue()
    assert TRACE_CALL_EMOJI not in output

    parse_and_apply_settings(UserSettings(print_call_link=True))
    func()

    output = captured_stdout.getvalue()
    assert TRACE_CALL_EMOJI in output


def test_print_call_link_env(client):
    captured_stdout = io.StringIO()
    sys.stdout = captured_stdout

    os.environ["WEAVE_PRINT_CALL_LINK"] = "false"
    func()

    output = captured_stdout.getvalue()
    assert TRACE_CALL_EMOJI not in output

    os.environ["WEAVE_PRINT_CALL_LINK"] = "true"
    func()

    output = captured_stdout.getvalue()
    assert TRACE_CALL_EMOJI in output


def test_save_code_setting(client):
    @weave.op
    def func():
        return 1

    parse_and_apply_settings(UserSettings(save_code=False))
    ref = client._save_object(func, "func")
    func2 = ref.get()
    print(f"{func2=}")
    print(f"{func2()=}")
    assert func2() is None  # no code saved

    # TODO: Should be able to turn code saving on/off at any time, not need to redef
    @weave.op
    def func():
        return 1

    parse_and_apply_settings(UserSettings(save_code=True))
    ref = client._save_object(func, "func")
    func3 = ref.get()
    print(f"{func3=}")
    print(f"{func3()=}")
    assert func3() == 1
