import dataclasses
import enum
import re
import typing

import astroid.modutils
import astroid.node_classes
import astroid.nodes
import pylint.checkers
import pylint.config
import pylint.interfaces
import pylint.lint

__version__ = "0.1.0"

OPTION_NAME = "forbid-import"


class RuleFormatError(Exception):
    """Raised when the format of a rule in the options is invalid."""

    def __init__(self, rule: str, reason: str):
        msg = f"Option {OPTION_NAME}: invalid rule '{rule}'. {reason}"
        super().__init__(msg)


@dataclasses.dataclass
class Rule:
    """A single rule (may be 'include' or 'exclude')"""

    from_: re.Pattern
    to: re.Pattern


@dataclasses.dataclass
class RuleSet:
    """Compiled set of forbidden import rules."""

    include: typing.List[Rule]
    exclude: typing.List[Rule]


def compile_rules(value: str) -> RuleSet:
    """
    Validate and build rules.

    :param value: Raw option value.
    :return: Compiled rules.
    :raises RuleFormatError: If the format of any rule is invalid.
    """
    include = []
    exclude = []
    for rule_str in value.split(","):
        if rule_str.strip() == "":
            continue
        parts = rule_str.split(":")
        num_parts = len(parts)
        if num_parts != 3:
            raise RuleFormatError(
                rule_str,
                "Expected 3 colon-separated items (action:from:to). Got {num_parts}.",
            )
        action_str, from_str, to_str = map(str.strip, parts)
        invalid_re_tmpl = "'{}' is not a valid regular expression: {}"
        try:
            from_ = re.compile(from_str, re.IGNORECASE)
        except re.error as ex:
            raise RuleFormatError(
                rule_str, invalid_re_tmpl.format(from_str, ex)
            ) from None
        try:
            to = re.compile(to_str, re.IGNORECASE)
        except re.error as ex:
            raise RuleFormatError(
                rule_str, invalid_re_tmpl.format(to_str, ex)
            ) from None
        rule = Rule(from_=from_, to=to)
        if action_str == "include":
            include.append(rule)
        elif action_str == "exclude":
            exclude.append(rule)
        else:
            raise RuleFormatError(
                rule_str,
                f"Expected 'action' to be one of ('include', 'exclude'). Got '{action_str}'",
            )

    return RuleSet(include=include, exclude=exclude)


class ForbitImportChecker(pylint.checkers.BaseChecker):
    name = "forbid-import"
    msgs = {
        # It's over 9000!
        "E9001": (
            "Importing %(to)s from %(from)s is forbidden.",
            "forbidden-import",
            f"Forbidden import rules are listed in the forbidden-import option.",
        )
    }
    options = [
        (
            OPTION_NAME,
            {
                "default": "",
                "type": "string",
                "help": (
                    "Comma-separated list of import rules as 'action:from:to',"
                    + " where 'action' is either 'include' or 'exclude', and"
                    + " 'from' and 'to' are regular expressions matching module names."
                    + " Spaces surrounding each element are ignored."
                ),
            },
        )
    ]

    __implements__ = pylint.interfaces.IAstroidChecker

    def __init__(self, linter: pylint.lint.PyLinter) -> None:
        super().__init__(linter)
        self._ruleset = compile_rules(self.config.forbid_import)

    def open(self) -> None:
        self._ruleset = compile_rules(self.config.forbid_import)

    def visit_import(self, node: astroid.nodes.Import) -> None:
        for imported_module, _alias in node.names:
            self._check_import(node, imported_module)

    def visit_importfrom(self, node: astroid.nodes.ImportFrom) -> None:
        for name, _alias in node.names:
            dotted_name = ".".join((node.modname, name))
            try:
                imported_module = astroid.modutils.get_module_part(dotted_name)
            except ImportError:
                continue
            self._check_import(node, imported_module)

    def _check_import(
        self, node: astroid.node_classes.NodeNG, imported_module: str
    ) -> None:
        """
        Check the import is not forbidden. If it is, add a message.

        :param node: Node being visited. Used to obtain current module and report errors.
        :param imported_module: Module being imported.
        """
        curr_module: str = node.root().name
        for exclude in self._ruleset.exclude:
            if exclude.from_.match(curr_module) and exclude.to.match(imported_module):
                return
        for include in self._ruleset.include:
            if include.from_.match(curr_module) and include.to.match(imported_module):
                self.add_message(
                    "forbidden-import",
                    args={"from": curr_module, "to": imported_module},
                    node=node,
                )


def register(linter: pylint.lint.PyLinter) -> None:
    """Pylint entry-point for loading plugins."""
    linter.register_checker(ForbitImportChecker(linter))
