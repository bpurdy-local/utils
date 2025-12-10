"""Tests for template_tool.py."""

import argparse
import sys
from pathlib import Path

import pytest

# Import the script module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
import template_tool


class TestParseVariables:
    """Tests for parse_variables function."""

    def test_parse_single(self):
        """Test parsing single variable."""
        result = template_tool.parse_variables(["name=John"])
        assert result == {"name": "John"}

    def test_parse_multiple(self):
        """Test parsing multiple variables."""
        result = template_tool.parse_variables(["name=John", "age=30"])
        assert result == {"name": "John", "age": "30"}

    def test_parse_empty(self):
        """Test parsing empty list."""
        result = template_tool.parse_variables(None)
        assert result == {}


class TestRenderTemplate:
    """Tests for render_template function."""

    def test_dollar_style(self):
        """Test dollar variable style."""
        template = "Hello ${name}!"
        variables = {"name": "World"}
        result = template_tool.render_template(template, variables, "dollar")
        assert result == "Hello World!"

    def test_jinja_style(self):
        """Test jinja variable style."""
        template = "Hello {{ name }}!"
        variables = {"name": "World"}
        result = template_tool.render_template(template, variables, "jinja")
        assert result == "Hello World!"

    def test_mustache_style(self):
        """Test mustache variable style."""
        template = "Hello {{name}}!"
        variables = {"name": "World"}
        result = template_tool.render_template(template, variables, "mustache")
        assert result == "Hello World!"

    def test_missing_variable(self):
        """Test missing variable is not replaced."""
        template = "Hello ${name}!"
        variables = {}
        result = template_tool.render_template(template, variables, "dollar")
        assert "${name}" in result


class TestCmdRender:
    """Tests for cmd_render function."""

    def test_render_simple(self, temp_file, capsys):
        """Test simple template rendering."""
        template_path = temp_file("Hello ${name}!", name="template.txt")
        args = argparse.Namespace(
            template=str(template_path),
            var=["name=World"],
            vars_file=None,
            env=False,
            output=None,
            style="dollar",
        )
        result = template_tool.cmd_render(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Hello World!" in captured.out

    def test_render_with_vars_file(self, temp_dir, capsys):
        """Test rendering with variables file."""
        template_path = temp_dir / "template.txt"
        template_path.write_text("Hello ${name}!")

        vars_path = temp_dir / "vars.json"
        vars_path.write_text('{"name": "Universe"}')

        args = argparse.Namespace(
            template=str(template_path),
            var=None,
            vars_file=str(vars_path),
            env=False,
            output=None,
            style="dollar",
        )
        result = template_tool.cmd_render(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Hello Universe!" in captured.out


class TestCmdVariables:
    """Tests for cmd_variables function."""

    def test_list_variables(self, temp_file, capsys):
        """Test listing template variables."""
        template_path = temp_file("${name} is ${age} years old", name="template.txt")
        args = argparse.Namespace(template=str(template_path))
        result = template_tool.cmd_variables(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "name" in captured.out
        assert "age" in captured.out


class TestCmdValidate:
    """Tests for cmd_validate function."""

    def test_validate_all_provided(self, temp_file, capsys):
        """Test validation when all variables provided."""
        template_path = temp_file("${name}", name="template.txt")
        args = argparse.Namespace(
            template=str(template_path),
            var=["name=John"],
            vars_file=None,
            env=False,
        )
        result = template_tool.cmd_validate(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "All variables provided" in captured.out

    def test_validate_missing(self, temp_file, capsys):
        """Test validation when variables missing."""
        template_path = temp_file("${name} ${age}", name="template.txt")
        args = argparse.Namespace(
            template=str(template_path),
            var=["name=John"],
            vars_file=None,
            env=False,
        )
        result = template_tool.cmd_validate(args)
        assert result == 1
        captured = capsys.readouterr()
        assert "Missing" in captured.out
        assert "age" in captured.out


class TestCmdInline:
    """Tests for cmd_inline function."""

    def test_inline(self, capsys):
        """Test inline template rendering."""
        args = argparse.Namespace(
            template="Hello ${name}!",
            var=["name=World"],
            vars_file=None,
            env=False,
            style="dollar",
        )
        result = template_tool.cmd_inline(args)
        assert result == 0
        captured = capsys.readouterr()
        assert "Hello World!" in captured.out
