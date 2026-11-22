import importlib
import json
from pathlib import Path


def load_plugins():
    entries = json.loads(Path("plugins.json").read_text())
    return [importlib.import_module(entry["handler"]) for entry in entries]


def main():
    return [plugin.render() for plugin in load_plugins()]


def _debug_dump_plugins(plugins):
    print("loaded plugins:", plugins)


# def old_main():
#     return ["legacy report"]


if __name__ == "__main__":
    print(main())
