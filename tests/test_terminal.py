"""Tests for Terminal utility class."""

from unittest.mock import patch

import pytest

from utils.terminal import Terminal


class TestPrompt:
    """Tests for Terminal.prompt()"""

    def test_basic_prompt(self):
        """Test basic prompt with user input."""
        with patch("builtins.input", return_value="John"):
            result = Terminal.prompt("Enter name")
            assert result == "John"

    def test_prompt_with_default(self):
        """Test prompt with default value when user presses enter."""
        with patch("builtins.input", return_value=""):
            result = Terminal.prompt("Enter port", default="8080")
            assert result == "8080"

    def test_prompt_override_default(self):
        """Test prompt overriding default value."""
        with patch("builtins.input", return_value="9000"):
            result = Terminal.prompt("Enter port", default="8080")
            assert result == "9000"

    def test_prompt_strips_whitespace(self):
        """Test prompt strips leading/trailing whitespace."""
        with patch("builtins.input", return_value="  test  "):
            result = Terminal.prompt("Enter text")
            assert result == "test"

    @patch("builtins.input")
    @patch("builtins.print")
    def test_prompt_with_validator_valid(self, mock_print, mock_input):
        """Test prompt with validator that passes on first try."""
        mock_input.return_value = "user@example.com"

        def validator(x: str) -> tuple[bool, str | None]:
            return (True, None) if "@" in x else (False, "Must contain @")

        result = Terminal.prompt("Enter email", validator=validator)
        assert result == "user@example.com"
        mock_print.assert_not_called()

    @patch("builtins.input")
    @patch("builtins.print")
    def test_prompt_with_validator_retry(self, mock_print, mock_input):
        """Test prompt with validator that fails then passes."""
        mock_input.side_effect = ["invalid", "user@example.com"]

        def validator(x: str) -> tuple[bool, str | None]:
            return (True, None) if "@" in x else (False, "Must contain @")

        result = Terminal.prompt("Enter email", validator=validator)
        assert result == "user@example.com"
        mock_print.assert_called_once_with("Must contain @")

    @patch("builtins.input")
    @patch("builtins.print")
    def test_prompt_with_validator_and_default(self, mock_print, mock_input):
        """Test prompt with validator and default value."""
        mock_input.return_value = ""

        def validator(x: str) -> tuple[bool, str | None]:
            return (True, None) if "@" in x else (False, "Must contain @")

        result = Terminal.prompt("Enter email", default="default@example.com", validator=validator)
        assert result == "default@example.com"


class TestConfirm:
    """Tests for Terminal.confirm()"""

    def test_confirm_yes(self):
        """Test confirmation with 'yes' input."""
        with patch("builtins.input", return_value="y"):
            assert Terminal.confirm("Continue?") is True

    def test_confirm_yes_full(self):
        """Test confirmation with 'yes' full word."""
        with patch("builtins.input", return_value="yes"):
            assert Terminal.confirm("Continue?") is True

    def test_confirm_no(self):
        """Test confirmation with 'no' input."""
        with patch("builtins.input", return_value="n"):
            assert Terminal.confirm("Continue?") is False

    def test_confirm_no_full(self):
        """Test confirmation with 'no' full word."""
        with patch("builtins.input", return_value="no"):
            assert Terminal.confirm("Continue?") is False

    def test_confirm_default_yes(self):
        """Test confirmation with default True."""
        with patch("builtins.input", return_value=""):
            assert Terminal.confirm("Continue?", default=True) is True

    def test_confirm_default_no(self):
        """Test confirmation with default False."""
        with patch("builtins.input", return_value=""):
            assert Terminal.confirm("Delete?", default=False) is False

    def test_confirm_case_insensitive(self):
        """Test confirmation is case insensitive."""
        with patch("builtins.input", return_value="Y"):
            assert Terminal.confirm("Continue?") is True
        with patch("builtins.input", return_value="YES"):
            assert Terminal.confirm("Continue?") is True
        with patch("builtins.input", return_value="No"):
            assert Terminal.confirm("Continue?") is False

    @patch("builtins.input")
    @patch("builtins.print")
    def test_confirm_invalid_then_valid(self, mock_print, mock_input):
        """Test confirmation with invalid input then valid."""
        mock_input.side_effect = ["maybe", "invalid", "y"]
        result = Terminal.confirm("Continue?")
        assert result is True
        # Should print error message twice
        assert mock_print.call_count == 2


class TestPassword:
    """Tests for Terminal.password()"""

    @patch("getpass.getpass", return_value="secret123")
    def test_password_default_message(self, mock_getpass):
        """Test password with default message."""
        result = Terminal.password()
        assert result == "secret123"
        mock_getpass.assert_called_once_with("Password: ")

    @patch("getpass.getpass", return_value="api-key-xyz")
    def test_password_custom_message(self, mock_getpass):
        """Test password with custom message."""
        result = Terminal.password("Enter API key")
        assert result == "api-key-xyz"
        mock_getpass.assert_called_once_with("Enter API key: ")


class TestChoice:
    """Tests for Terminal.choice()"""

    def test_choice_valid(self):
        """Test choice with valid selection."""
        with patch("builtins.input", return_value="dev"):
            result = Terminal.choice("Select env", choices=["dev", "prod"])
            assert result == "dev"

    def test_choice_case_insensitive(self):
        """Test choice is case insensitive by default."""
        with patch("builtins.input", return_value="DEV"):
            result = Terminal.choice("Select env", choices=["dev", "prod"])
            assert result == "dev"

    def test_choice_case_sensitive(self):
        """Test choice with case sensitivity enabled."""
        with patch("builtins.input", side_effect=["DEV", "dev"]):
            result = Terminal.choice("Select env", choices=["dev", "prod"], case_sensitive=True)
            assert result == "dev"

    def test_choice_with_default(self):
        """Test choice with default value."""
        with patch("builtins.input", return_value=""):
            result = Terminal.choice("Select env", choices=["dev", "prod"], default="dev")
            assert result == "dev"

    def test_choice_empty_list_raises(self):
        """Test choice with empty list raises ValueError."""
        with pytest.raises(ValueError, match="choices list cannot be empty"):
            Terminal.choice("Select", choices=[])

    def test_choice_invalid_default_raises(self):
        """Test choice with invalid default raises ValueError."""
        with pytest.raises(ValueError, match=r"default .* not in choices"):
            Terminal.choice("Select", choices=["a", "b"], default="c")

    @patch("builtins.input")
    @patch("builtins.print")
    def test_choice_invalid_then_valid(self, mock_print, mock_input):
        """Test choice with invalid input then valid."""
        mock_input.side_effect = ["invalid", "staging", "dev"]
        result = Terminal.choice("Select", choices=["dev", "prod"])
        assert result == "dev"
        assert mock_print.call_count == 2


class TestSelect:
    """Tests for Terminal.select()"""

    @patch("builtins.input", return_value="1")
    @patch("builtins.print")
    def test_select_first_option(self, mock_print, mock_input):
        """Test selecting first option."""
        idx, value = Terminal.select("Choose", options=["Apple", "Banana"])
        assert idx == 0
        assert value == "Apple"

    @patch("builtins.input", return_value="2")
    @patch("builtins.print")
    def test_select_second_option(self, mock_print, mock_input):
        """Test selecting second option."""
        idx, value = Terminal.select("Choose", options=["Apple", "Banana", "Cherry"])
        assert idx == 1
        assert value == "Banana"

    @patch("builtins.input", return_value="")
    @patch("builtins.print")
    def test_select_with_default(self, mock_print, mock_input):
        """Test select with default index."""
        idx, value = Terminal.select("Choose", options=["A", "B", "C"], default_index=1)
        assert idx == 1
        assert value == "B"

    def test_select_empty_list_raises(self):
        """Test select with empty list raises ValueError."""
        with pytest.raises(ValueError, match="options list cannot be empty"):
            Terminal.select("Choose", options=[])

    def test_select_invalid_default_raises(self):
        """Test select with invalid default index raises ValueError."""
        with pytest.raises(ValueError, match=r"default_index .* out of range"):
            Terminal.select("Choose", options=["A", "B"], default_index=5)

    @patch("builtins.input")
    @patch("builtins.print")
    def test_select_invalid_then_valid(self, mock_print, mock_input):
        """Test select with invalid input then valid."""
        mock_input.side_effect = ["0", "99", "abc", "2"]
        idx, value = Terminal.select("Choose", options=["A", "B", "C"])
        assert idx == 1
        assert value == "B"


class TestMultiline:
    """Tests for Terminal.multiline()"""

    @patch("builtins.input")
    @patch("builtins.print")
    def test_multiline_default_terminator(self, mock_print, mock_input):
        """Test multiline with default empty line terminator."""
        mock_input.side_effect = ["line1", "line2", ""]
        result = Terminal.multiline("Enter text")
        assert result == "line1\nline2"

    @patch("builtins.input")
    @patch("builtins.print")
    def test_multiline_custom_terminator(self, mock_print, mock_input):
        """Test multiline with custom terminator."""
        mock_input.side_effect = ["SELECT *", "FROM users", "GO"]
        result = Terminal.multiline("Enter SQL", terminator="GO")
        assert result == "SELECT *\nFROM users"

    @patch("builtins.input")
    @patch("builtins.print")
    def test_multiline_single_line(self, mock_print, mock_input):
        """Test multiline with single line."""
        mock_input.side_effect = ["only line", ""]
        result = Terminal.multiline("Enter text")
        assert result == "only line"


class TestPromptInt:
    """Tests for Terminal.prompt_int()"""

    def test_prompt_int_valid(self):
        """Test prompt_int with valid integer."""
        with patch("builtins.input", return_value="42"):
            result = Terminal.prompt_int("Enter number")
            assert result == 42

    def test_prompt_int_with_default(self):
        """Test prompt_int with default value."""
        with patch("builtins.input", return_value=""):
            result = Terminal.prompt_int("Enter port", default=8080)
            assert result == 8080

    def test_prompt_int_with_range(self):
        """Test prompt_int with min/max range."""
        with patch("builtins.input", return_value="50"):
            result = Terminal.prompt_int("Enter age", min_val=0, max_val=120)
            assert result == 50

    @patch("builtins.input")
    @patch("builtins.print")
    def test_prompt_int_below_min(self, mock_print, mock_input):
        """Test prompt_int with value below minimum."""
        mock_input.side_effect = ["-5", "10"]
        result = Terminal.prompt_int("Enter", min_val=0)
        assert result == 10

    @patch("builtins.input")
    @patch("builtins.print")
    def test_prompt_int_above_max(self, mock_print, mock_input):
        """Test prompt_int with value above maximum."""
        mock_input.side_effect = ["100", "50"]
        result = Terminal.prompt_int("Enter", max_val=50)
        assert result == 50

    @patch("builtins.input")
    @patch("builtins.print")
    def test_prompt_int_invalid_then_valid(self, mock_print, mock_input):
        """Test prompt_int with invalid input then valid."""
        mock_input.side_effect = ["abc", "12.5", "42"]
        result = Terminal.prompt_int("Enter number")
        assert result == 42

    def test_prompt_int_invalid_range_raises(self):
        """Test prompt_int with invalid range raises ValueError."""
        with (
            pytest.raises(ValueError, match="min_val cannot be greater than max_val"),
            patch("builtins.input", return_value="50"),
        ):
            Terminal.prompt_int("Enter", min_val=100, max_val=50)


class TestPromptFloat:
    """Tests for Terminal.prompt_float()"""

    def test_prompt_float_valid(self):
        """Test prompt_float with valid float."""
        with patch("builtins.input", return_value="3.14"):
            result = Terminal.prompt_float("Enter number")
            assert result == 3.14

    def test_prompt_float_integer_input(self):
        """Test prompt_float with integer input."""
        with patch("builtins.input", return_value="42"):
            result = Terminal.prompt_float("Enter number")
            assert result == 42.0

    def test_prompt_float_with_default(self):
        """Test prompt_float with default value."""
        with patch("builtins.input", return_value=""):
            result = Terminal.prompt_float("Enter rate", default=0.5)
            assert result == 0.5

    def test_prompt_float_with_range(self):
        """Test prompt_float with min/max range."""
        with patch("builtins.input", return_value="0.75"):
            result = Terminal.prompt_float("Enter rate", min_val=0.0, max_val=1.0)
            assert result == 0.75

    @patch("builtins.input")
    @patch("builtins.print")
    def test_prompt_float_below_min(self, mock_print, mock_input):
        """Test prompt_float with value below minimum."""
        mock_input.side_effect = ["-0.5", "0.5"]
        result = Terminal.prompt_float("Enter", min_val=0.0)
        assert result == 0.5

    @patch("builtins.input")
    @patch("builtins.print")
    def test_prompt_float_above_max(self, mock_print, mock_input):
        """Test prompt_float with value above maximum."""
        mock_input.side_effect = ["1.5", "0.9"]
        result = Terminal.prompt_float("Enter", max_val=1.0)
        assert result == 0.9

    @patch("builtins.input")
    @patch("builtins.print")
    def test_prompt_float_invalid_then_valid(self, mock_print, mock_input):
        """Test prompt_float with invalid input then valid."""
        mock_input.side_effect = ["abc", "3.14"]
        result = Terminal.prompt_float("Enter number")
        assert result == 3.14

    def test_prompt_float_invalid_range_raises(self):
        """Test prompt_float with invalid range raises ValueError."""
        with (
            pytest.raises(ValueError, match="min_val cannot be greater than max_val"),
            patch("builtins.input", return_value="0.5"),
        ):
            Terminal.prompt_float("Enter", min_val=1.0, max_val=0.0)


class TestClear:
    """Tests for Terminal.clear()"""

    @patch("sys.stdout")
    @patch("builtins.print")
    def test_clear(self, mock_print, mock_stdout):
        """Test clear screen."""
        Terminal.clear()
        mock_print.assert_called_once_with("\033[2J\033[H", end="")
        mock_stdout.flush.assert_called_once()


class TestPrintLine:
    """Tests for Terminal.print_line()"""

    @patch("builtins.print")
    def test_print_line_default(self, mock_print):
        """Test print_line with default settings."""
        Terminal.print_line()
        mock_print.assert_called_once_with("-" * 80)

    @patch("builtins.print")
    def test_print_line_custom_char(self, mock_print):
        """Test print_line with custom character."""
        Terminal.print_line("=")
        mock_print.assert_called_once_with("=" * 80)

    @patch("builtins.print")
    def test_print_line_custom_width(self, mock_print):
        """Test print_line with custom width."""
        Terminal.print_line(width=40)
        mock_print.assert_called_once_with("-" * 40)

    def test_print_line_invalid_char_raises(self):
        """Test print_line with multi-character string raises ValueError."""
        with pytest.raises(ValueError, match="char must be a single character"):
            Terminal.print_line("==")


class TestPrintBox:
    """Tests for Terminal.print_box()"""

    @patch("builtins.print")
    def test_print_box_single_line(self, mock_print):
        """Test print_box with single line."""
        Terminal.print_box("Hello")
        calls = mock_print.call_args_list
        assert len(calls) == 5  # top, padding, content, padding, bottom
        assert "┌" in str(calls[0])
        assert "└" in str(calls[-1])

    @patch("builtins.print")
    def test_print_box_multiline(self, mock_print):
        """Test print_box with multiple lines."""
        Terminal.print_box("Line 1\nLine 2")
        calls = mock_print.call_args_list
        # top border + padding + 2 content lines + padding + bottom border
        assert len(calls) == 6

    @patch("builtins.print")
    def test_print_box_custom_padding(self, mock_print):
        """Test print_box with custom padding."""
        Terminal.print_box("Text", padding=2)
        calls = mock_print.call_args_list
        # top + 2 padding + content + 2 padding + bottom
        assert len(calls) == 7

    @patch("builtins.print")
    def test_print_box_custom_width(self, mock_print):
        """Test print_box with custom width."""
        Terminal.print_box("Hi", width=30)
        calls = mock_print.call_args_list
        # Check that width is respected
        top_border = str(calls[0])
        assert "─" * 28 in top_border  # width - 2 for corners


class TestColorize:
    """Tests for Terminal.colorize()"""

    def test_colorize_no_formatting(self):
        """Test colorize with no formatting returns original text."""
        result = Terminal.colorize("text")
        assert result == "text"

    def test_colorize_with_color(self):
        """Test colorize with color."""
        result = Terminal.colorize("Error", color="red")
        assert result == "\033[31mError\033[0m"

    def test_colorize_with_bold(self):
        """Test colorize with bold."""
        result = Terminal.colorize("Important", bold=True)
        assert result == "\033[1mImportant\033[0m"

    def test_colorize_with_underline(self):
        """Test colorize with underline."""
        result = Terminal.colorize("Link", underline=True)
        assert result == "\033[4mLink\033[0m"

    def test_colorize_with_bg_color(self):
        """Test colorize with background color."""
        result = Terminal.colorize("Highlight", bg_color="yellow")
        assert result == "\033[43mHighlight\033[0m"

    def test_colorize_combined(self):
        """Test colorize with multiple formatting options."""
        result = Terminal.colorize("Error", color="red", bold=True, underline=True)
        assert result == "\033[1;4;31mError\033[0m"

    def test_colorize_all_colors(self):
        """Test colorize with all color options."""
        colors = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
        for color in colors:
            result = Terminal.colorize("text", color=color)
            assert result.startswith("\033[")
            assert result.endswith("\033[0m")


class TestProgressBar:
    """Tests for Terminal.progress_bar()"""

    def test_progress_bar_zero_percent(self):
        """Test progress bar at 0%."""
        result = Terminal.progress_bar(0, 100, width=10)
        assert "0%" in result
        assert "0/100" in result
        assert "░" in result

    def test_progress_bar_fifty_percent(self):
        """Test progress bar at 50%."""
        result = Terminal.progress_bar(50, 100, width=10)
        assert "50%" in result
        assert "50/100" in result
        assert "█" in result
        assert "░" in result

    def test_progress_bar_hundred_percent(self):
        """Test progress bar at 100%."""
        result = Terminal.progress_bar(100, 100, width=10)
        assert "100%" in result
        assert "100/100" in result
        assert "█" in result

    def test_progress_bar_zero_total(self):
        """Test progress bar with zero total."""
        result = Terminal.progress_bar(0, 0, width=10)
        assert "100%" in result

    def test_progress_bar_with_prefix(self):
        """Test progress bar with prefix."""
        result = Terminal.progress_bar(50, 100, prefix="Downloading:")
        assert "Downloading:" in result

    def test_progress_bar_with_suffix(self):
        """Test progress bar with suffix."""
        result = Terminal.progress_bar(50, 100, suffix="complete")
        assert "complete" in result

    def test_progress_bar_custom_chars(self):
        """Test progress bar with custom fill/empty characters."""
        result = Terminal.progress_bar(50, 100, width=10, fill="#", empty="-")
        assert "#" in result
        assert "-" in result


class TestValidateInput:
    """Tests for Terminal.validate_input()"""

    def test_validate_input_valid_first_try(self):
        """Test validate_input with valid input on first try."""
        with patch("builtins.input", return_value="test@example.com"):
            result = Terminal.validate_input("Email", validator=lambda x: "@" in x)
            assert result == "test@example.com"

    @patch("builtins.input")
    @patch("builtins.print")
    def test_validate_input_invalid_then_valid(self, mock_print, mock_input):
        """Test validate_input with invalid then valid input."""
        mock_input.side_effect = ["invalid", "valid@test.com"]
        result = Terminal.validate_input("Email", validator=lambda x: "@" in x)
        assert result == "valid@test.com"
        mock_print.assert_called()

    @patch("builtins.input")
    @patch("builtins.print")
    def test_validate_input_custom_error(self, mock_print, mock_input):
        """Test validate_input with custom error message."""
        mock_input.side_effect = ["abc", "123"]
        result = Terminal.validate_input(
            "Code",
            validator=lambda x: x.isdigit(),
            error_message="Must be digits only!",
        )
        assert result == "123"
        mock_print.assert_called_with("Must be digits only!")

    def test_validate_input_complex_validator(self):
        """Test validate_input with complex validator."""

        def validator(x: str) -> bool:
            return len(x) >= 8 and any(c.isdigit() for c in x)

        with patch("builtins.input", return_value="Python123"):
            result = Terminal.validate_input("Password", validator=validator)
            assert result == "Python123"
