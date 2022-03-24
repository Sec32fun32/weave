import analytics
import subprocess

analytics.write_key = "uJ8vZgKqTBVH6ZdhD4GZGZYsR7ucfJmb"


def whoami():
    return subprocess.check_output("whoami").decode().strip()


identify_called = False


def identify():
    global identify_called
    if not identify_called:
        who = whoami()
        analytics.identify(who, {"whoami": who})
    identify_called = True


def track(action: str, info=None):
    identify()
    if info is None:
        info = {}
    analytics.track(whoami(), action, info)


def use_called():
    track("called use")


def show_called():
    track("called show")
