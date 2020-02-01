import os.path
import pathlib
import subprocess

PYLINTRC = r"""
[MASTER]
load-plugins=pylint_forbid_import

[MESSAGES CONTROL]
disable=all
enable=forbidden-import

[IMPORTS]
forbid-import= include : app.* : xml\.etree,
               exclude : app.* : xml\.etree\.ElementTree,
               include : .* : os.*

[REPORTS]
score=no
"""

# NOTE: Paths are POSIX-style, and the actual output is normalized in the test
EXPECTED = """
************* Module app
app/__init__.py:1:0: E9001: Importing xml.etree.ElementInclude from app is forbidden. (forbidden-import)
app/__init__.py:1:0: E9001: Importing xml.etree.ElementPath from app is forbidden. (forbidden-import)
app/__init__.py:2:0: E9001: Importing os from app is forbidden. (forbidden-import)
************* Module app.one
app/one.py:1:0: E9001: Importing xml.etree from app.one is forbidden. (forbidden-import)
************* Module app.two
app/two.py:1:0: E9001: Importing xml.etree from app.two is forbidden. (forbidden-import)
app/two.py:2:0: E9001: Importing os.path from app.two is forbidden. (forbidden-import)
""".strip()


def normalize_paths(pylint_output: str) -> str:
    # Assume path separator characters are only used in paths
    return pylint_output.replace(os.path.sep, "/")


def write(path: pathlib.Path, *lines: str) -> None:
    path.write_text("\n".join(lines))


def test_checker_from_cli(tmp_path: pathlib.Path) -> None:
    package = tmp_path / "app"
    package.mkdir()
    write(
        package / "__init__.py",
        "from xml.etree import ElementInclude, ElementPath",
        "import os",
    )
    write(
        package / "one.py", "from xml import etree", "from xml.etree import ElementTree"
    )
    write(package / "two.py", "import xml.etree", "import os.path")
    write(tmp_path / "pylintrc", PYLINTRC)
    completed = subprocess.run(
        ["pylint", "app"], cwd=tmp_path, text=True, capture_output=True, check=False
    )
    output = normalize_paths(completed.stdout.strip())
    assert output == EXPECTED
