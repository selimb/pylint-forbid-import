# pylint: disable=no-self-use
import contextlib
import functools
import typing

import astroid
import astroid.node_classes
import pylint.testutils
import pytest

import pylint_forbid_import


@contextlib.contextmanager
def assert_raises_strings(
    exc_type: typing.Type[Exception], *patterns: str
) -> typing.Iterator[None]:
    with pytest.raises(exc_type) as ctx:
        yield
    msg = str(ctx.value)
    for pattern in patterns:
        assert pattern in msg


class TestOptionValidation:
    """Test 'forbid-import' option is validated."""

    @pytest.mark.parametrize(
        "option", ["just a string", "only : one", "way:too:many:colons"]
    )
    def test_missing_colons(self, option: str) -> None:
        with assert_raises_strings(
            pylint_forbid_import.RuleFormatError,
            "Expected 3 colon-separated items",
            option,
        ):
            pylint_forbid_import.compile_rules(option)

    def test_invalid_action(self) -> None:
        with assert_raises_strings(
            pylint_forbid_import.RuleFormatError, "'action'", "oops"
        ):
            pylint_forbid_import.compile_rules("oops:from:to")

    @pytest.mark.parametrize("option", ["include:***:to", "include:from:***"])
    def test_invalid_regex(self, option: str) -> None:
        with assert_raises_strings(
            pylint_forbid_import.RuleFormatError,
            "'***' is not a valid regular expression",
        ):
            pylint_forbid_import.compile_rules(option)


def with_rules(rules: str):  # type: ignore
    """Decorator for setting the 'forbid-import' rules option on a test."""
    # Can't use pylint.testutils.set_config when the test is parametrized :(
    def decorator(func):  # type: ignore
        @functools.wraps(func)
        def inner(self, *args, **kwargs):  # type: ignore
            self.checker.config.forbid_import = rules
            self.checker.open()
            func(self, *args, **kwargs)

        return inner

    return decorator


class TestForbidImportChecker(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = pylint_forbid_import.ForbitImportChecker

    @contextlib.contextmanager
    def assert_forbidden_import(
        self, node: astroid.node_classes.NodeNG, from_: str, to: str
    ) -> typing.Iterator[None]:
        with self.assertAddsMessages(
            pylint.testutils.Message(
                msg_id="forbidden-import", node=node, args={"from": from_, "to": to}
            )
        ):
            yield

    @with_rules("include : app.* : os.*")
    @pytest.mark.parametrize(
        "text, to",
        [
            ("import os", "os"),
            ("import os.path", "os.path"),
            ("import os as so", "os"),
            ("import sys, os", "os"),
        ],
    )
    def test_forbidden_import(self, text: str, to: str) -> None:
        node = astroid.extract_node(text, module_name="app")
        with self.assert_forbidden_import(node, "app", to):
            self.checker.visit_import(node)

    @with_rules(r"include : app.* : xml\.etree.*")
    @pytest.mark.parametrize(
        "text, to",
        [
            ("from xml import dom, etree", "xml.etree"),
            ("from xml.etree import ElementInclude", "xml.etree.ElementInclude"),
            ("from xml import etree as xmltree", "xml.etree"),
            (
                "from xml.etree.ElementTree import Element as XMLElement",
                "xml.etree.ElementTree",
            ),
        ],
    )
    def test_forbidden_importfrom(self, text: str, to: str) -> None:
        node = astroid.extract_node(text, module_name="app")
        with self.assert_forbidden_import(node, "app", to):
            self.checker.visit_importfrom(node)

    def test_importfrom_does_not_crash_on_import_error(self) -> None:
        node = astroid.extract_node("from oops import doesnotexist")
        with self.assertNoMessages():
            self.checker.visit_importfrom(node)

    @with_rules(
        r"include : app : xml\.etree.* , exclude : app : xml\.etree\.ElementTree"
    )
    def test_exclude_rules_have_precedence(self) -> None:
        node = astroid.extract_node("import xml.etree.ElementTree", module_name="app")
        with self.assertNoMessages():
            self.checker.visit_import(node)
