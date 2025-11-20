"""Terminal input and prompt utilities."""

import getpass
import sys
from collections.abc import Callable
from typing import Literal


class Terminal:
    """Static utility class for terminal input and prompt operations."""

    @staticmethod
    def prompt(
        message: str,
        *,
        default: str | None = None,
        validator: Callable[[str], tuple[bool, str | None]] | None = None,
    ) -> str:
        """Prompt user for text input with optional default value and validation.

        Args:
            message: The prompt message to display
            default: Default value if user presses Enter (keyword-only)
            validator: Optional function that takes input and returns (is_valid, error_message)
                      (keyword-only)

        Returns:
            User input string or default value

        Examples:
            >>> Terminal.prompt("Enter your name")
            # Terminal: Enter your name: █
            'John'

            >>> Terminal.prompt("Enter port", default="8080")
            # Terminal: Enter port [8080]: █
            '8080'

            >>> Terminal.prompt("Enter email", validator=lambda x: (("@" in x), "Must contain @"))
            # Terminal: Enter email: invalid
            #           Must contain @
            #           Enter email: user@example.com
            'user@example.com'
        """
        prompt_msg = f"{message} [{default}]: " if default is not None else f"{message}: "

        while True:
            result = input(prompt_msg).strip()

            # Use default if no input provided
            if not result and default is not None:
                return default

            # If no input and no default, require input (unless no validator)
            if not result and validator is None:
                return ""

            # Validate input if validator provided
            if validator:
                is_valid, error_msg = validator(result if result else "")
                if is_valid:
                    return result if result else (default or "")
                if error_msg:
                    print(error_msg)
            else:
                return result if result else (default or "")

    @staticmethod
    def confirm(message: str, *, default: bool | None = None) -> bool:
        """Prompt user for yes/no confirmation.

        Args:
            message: The confirmation message to display
            default: Default value (True for yes, False for no, None for no default)

        Returns:
            True if user confirms, False otherwise

        Examples:
            >>> Terminal.confirm("Continue?")
            # Terminal: Continue? [y/n]: y
            True

            >>> Terminal.confirm("Delete file?", default=False)
            # Terminal: Delete file? [y/N]: █
            False
        """
        suffix = ""
        if default is True:
            suffix = " [Y/n]: "
        elif default is False:
            suffix = " [y/N]: "
        else:
            suffix = " [y/n]: "

        while True:
            response = input(f"{message}{suffix}").strip().lower()

            if not response and default is not None:
                return default

            if response in ("y", "yes"):
                return True
            if response in ("n", "no"):
                return False

            print("Please answer 'y' or 'n'")

    @staticmethod
    def password(message: str = "Password") -> str:
        """Prompt user for password input (hidden).

        Args:
            message: The prompt message to display

        Returns:
            Password string entered by user

        Examples:
            >>> Terminal.password()
            # Terminal: Password: ******** (hidden input)
            'secret123'

            >>> Terminal.password("Enter API key")
            # Terminal: Enter API key: ******** (hidden input)
            'abc123xyz'
        """
        return getpass.getpass(f"{message}: ")

    @staticmethod
    def choice(
        message: str,
        *,
        choices: list[str],
        default: str | None = None,
        case_sensitive: bool = False,
    ) -> str:
        """Prompt user to select from a list of choices.

        Args:
            message: The prompt message to display
            choices: List of valid choices (keyword-only)
            default: Default choice if user presses Enter (keyword-only)
            case_sensitive: Whether choices are case-sensitive (keyword-only)

        Returns:
            Selected choice string

        Raises:
            ValueError: If choices list is empty or default not in choices

        Examples:
            >>> Terminal.choice("Select env", choices=["dev", "prod"])
            # Terminal: Select env (dev, prod): dev
            'dev'

            >>> Terminal.choice("Color?", choices=["red", "blue"], default="red")
            # Terminal: Color? (red, blue) [red]: █
            'red'
        """
        if not choices:
            raise ValueError("choices list cannot be empty")

        if default is not None and default not in choices:
            raise ValueError(f"default '{default}' not in choices")

        choices_display = ", ".join(choices)
        if default:
            message = f"{message} ({choices_display}) [{default}]: "
        else:
            message = f"{message} ({choices_display}): "

        while True:
            response = input(message).strip()

            if not response and default is not None:
                return default

            # Check if response matches any choice
            for choice in choices:
                if case_sensitive:
                    if response == choice:
                        return choice
                else:
                    if response.lower() == choice.lower():
                        return choice

            print(f"Invalid choice. Please select from: {choices_display}")

    @staticmethod
    def select(
        message: str, *, options: list[str], default_index: int | None = None
    ) -> tuple[int, str]:
        """Prompt user to select from numbered list of options.

        Args:
            message: The prompt message to display
            options: List of options to display (keyword-only)
            default_index: Default option index (0-based) (keyword-only)

        Returns:
            Tuple of (selected_index, selected_option)

        Raises:
            ValueError: If options list is empty or default_index out of range

        Examples:
            >>> Terminal.select("Choose:", options=["Apple", "Banana"])
            # Terminal: Choose:
            #             1. Apple
            #             2. Banana
            #           Select (number): 1
            (0, 'Apple')

            >>> Terminal.select("Pick:", options=["A", "B"], default_index=1)
            # Terminal: Pick:
            #             1. A
            #             2. B (default)
            #           Select (number) [2]: █
            (1, 'B')
        """
        if not options:
            raise ValueError("options list cannot be empty")

        if default_index is not None and not (0 <= default_index < len(options)):
            raise ValueError(f"default_index {default_index} out of range")

        print(message)
        for idx, option in enumerate(options, 1):
            default_marker = " (default)" if default_index == idx - 1 else ""
            print(f"  {idx}. {option}{default_marker}")

        while True:
            prompt = "Select (number)"
            if default_index is not None:
                prompt = f"{prompt} [{default_index + 1}]"
            prompt = f"{prompt}: "

            response = input(prompt).strip()

            if not response and default_index is not None:
                return (default_index, options[default_index])

            try:
                num = int(response)
                if 1 <= num <= len(options):
                    return (num - 1, options[num - 1])
            except ValueError:
                pass

            print(f"Please enter a number between 1 and {len(options)}")

    @staticmethod
    def multiline(message: str, *, terminator: str = "") -> str:
        """Prompt user for multi-line input until terminator line.

        Args:
            message: The prompt message to display
            terminator: Line that signals end of input (keyword-only, default empty line)

        Returns:
            Multi-line string input

        Examples:
            >>> Terminal.multiline("Enter text:")
            # Terminal: Enter text: (end with 'empty line')
            #           line1
            #           line2
            #           line3
            #
            'line1\\nline2\\nline3'

            >>> Terminal.multiline("SQL query:", terminator="GO")
            # Terminal: SQL query: (end with 'GO')
            #           SELECT *
            #           FROM users
            #           GO
            'SELECT *\\nFROM users'
        """
        print(f"{message} (end with '{terminator or 'empty line'}')")
        lines = []

        while True:
            line = input()
            if line == terminator:
                break
            lines.append(line)

        return "\n".join(lines)

    @staticmethod
    def prompt_int(
        message: str,
        *,
        default: int | None = None,
        min_val: int | None = None,
        max_val: int | None = None,
    ) -> int:
        """Prompt user for integer input with validation.

        Args:
            message: The prompt message to display
            default: Default value if user presses Enter (keyword-only)
            min_val: Minimum allowed value (keyword-only)
            max_val: Maximum allowed value (keyword-only)

        Returns:
            Integer value entered by user

        Raises:
            ValueError: If min_val > max_val

        Examples:
            >>> Terminal.prompt_int("Enter age", min_val=0, max_val=120)
            # Terminal: Enter age (0-120): 25
            25

            >>> Terminal.prompt_int("Port", default=8080, min_val=1, max_val=65535)
            # Terminal: Port [8080] (1-65535): █
            8080
        """
        if min_val is not None and max_val is not None and min_val > max_val:
            raise ValueError("min_val cannot be greater than max_val")

        # Build message with range info
        prompt_msg = message
        if min_val is not None or max_val is not None:
            range_str = ""
            if min_val is not None and max_val is not None:
                range_str = f" ({min_val}-{max_val})"
            elif min_val is not None:
                range_str = f" (min: {min_val})"
            elif max_val is not None:
                range_str = f" (max: {max_val})"
            prompt_msg = f"{prompt_msg}{range_str}"

        # Create validator function
        def int_validator(value: str) -> tuple[bool, str | None]:
            try:
                int_val = int(value)
                if min_val is not None and int_val < min_val:
                    return (False, f"Value must be >= {min_val}")
                if max_val is not None and int_val > max_val:
                    return (False, f"Value must be <= {max_val}")
                return (True, None)
            except ValueError:
                return (False, "Please enter a valid integer")

        # Use base prompt with validator
        result = Terminal.prompt(
            prompt_msg,
            default=str(default) if default is not None else None,
            validator=int_validator,
        )
        return int(result)

    @staticmethod
    def prompt_float(
        message: str,
        *,
        default: float | None = None,
        min_val: float | None = None,
        max_val: float | None = None,
    ) -> float:
        """Prompt user for float input with validation.

        Args:
            message: The prompt message to display
            default: Default value if user presses Enter (keyword-only)
            min_val: Minimum allowed value (keyword-only)
            max_val: Maximum allowed value (keyword-only)

        Returns:
            Float value entered by user

        Raises:
            ValueError: If min_val > max_val

        Examples:
            >>> Terminal.prompt_float("Enter price")
            # Terminal: Enter price: 19.99
            19.99

            >>> Terminal.prompt_float("Rate", default=0.5, min_val=0.0, max_val=1.0)
            # Terminal: Rate [0.5] (0.0-1.0): █
            0.75
        """
        if min_val is not None and max_val is not None and min_val > max_val:
            raise ValueError("min_val cannot be greater than max_val")

        # Build message with range info
        prompt_msg = message
        if min_val is not None or max_val is not None:
            range_str = ""
            if min_val is not None and max_val is not None:
                range_str = f" ({min_val}-{max_val})"
            elif min_val is not None:
                range_str = f" (min: {min_val})"
            elif max_val is not None:
                range_str = f" (max: {max_val})"
            prompt_msg = f"{prompt_msg}{range_str}"

        # Create validator function
        def float_validator(value: str) -> tuple[bool, str | None]:
            try:
                float_val = float(value)
                if min_val is not None and float_val < min_val:
                    return (False, f"Value must be >= {min_val}")
                if max_val is not None and float_val > max_val:
                    return (False, f"Value must be <= {max_val}")
                return (True, None)
            except ValueError:
                return (False, "Please enter a valid number")

        # Use base prompt with validator
        result = Terminal.prompt(
            prompt_msg,
            default=str(default) if default is not None else None,
            validator=float_validator,
        )
        return float(result)

    @staticmethod
    def clear() -> None:
        """Clear the terminal screen.

        Examples:
            >>> Terminal.clear()
        """
        # ANSI escape code for clearing screen
        print("\033[2J\033[H", end="")
        sys.stdout.flush()

    @staticmethod
    def print_line(char: str = "-", *, width: int = 80) -> None:
        """Print a horizontal line separator.

        Args:
            char: Character to use for line (default "-")
            width: Width of line in characters (keyword-only, default 80)

        Examples:
            >>> Terminal.print_line()
            >>> Terminal.print_line("=", width=40)
        """
        if len(char) != 1:
            raise ValueError("char must be a single character")
        print(char * width)

    @staticmethod
    def print_box(text: str, *, width: int | None = None, padding: int = 1) -> None:
        """Print text in a box border.

        Args:
            text: Text to display in box
            width: Box width (keyword-only, None for auto)
            padding: Padding around text (keyword-only, default 1)

        Examples:
            >>> Terminal.print_box("Hello World")
            # Terminal: ┌─────────────┐
            #           │             │
            #           │ Hello World │
            #           │             │
            #           └─────────────┘

            >>> Terminal.print_box("Status: OK", width=30, padding=2)
            # Terminal: ┌────────────────────────────┐
            #           │                            │
            #           │                            │
            #           │  Status: OK                │
            #           │                            │
            #           │                            │
            #           └────────────────────────────┘
        """
        lines = text.split("\n")
        max_len = max(len(line) for line in lines) if lines else 0

        if width is None:
            width = max_len + (padding * 2) + 2
        else:
            width = max(width, max_len + (padding * 2) + 2)

        # Top border
        print("┌" + "─" * (width - 2) + "┐")

        # Padding rows
        for _ in range(padding):
            print("│" + " " * (width - 2) + "│")

        # Content
        for line in lines:
            padded = line.ljust(max_len)
            side_padding = " " * padding
            content = f"{side_padding}{padded}{side_padding}"
            content = content.ljust(width - 2)
            print(f"│{content}│")

        # Padding rows
        for _ in range(padding):
            print("│" + " " * (width - 2) + "│")

        # Bottom border
        print("└" + "─" * (width - 2) + "┘")

    @staticmethod
    def colorize(
        text: str,
        *,
        color: Literal["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
        | None = None,
        bg_color: Literal["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
        | None = None,
        bold: bool = False,
        underline: bool = False,
    ) -> str:
        """Apply ANSI color codes to text.

        Args:
            text: Text to colorize
            color: Text color (keyword-only)
            bg_color: Background color (keyword-only)
            bold: Make text bold (keyword-only)
            underline: Underline text (keyword-only)

        Returns:
            Text with ANSI escape codes

        Examples:
            >>> Terminal.colorize("Error", color="red", bold=True)
            # Terminal: Error (displayed in bold red text)
            '\\033[1;31mError\\033[0m'

            >>> Terminal.colorize("Success", color="green")
            # Terminal: Success (displayed in green text)
            '\\033[32mSuccess\\033[0m'
        """
        colors = {
            "black": "30",
            "red": "31",
            "green": "32",
            "yellow": "33",
            "blue": "34",
            "magenta": "35",
            "cyan": "36",
            "white": "37",
        }

        bg_colors = {
            "black": "40",
            "red": "41",
            "green": "42",
            "yellow": "43",
            "blue": "44",
            "magenta": "45",
            "cyan": "46",
            "white": "47",
        }

        codes = []

        if bold:
            codes.append("1")
        if underline:
            codes.append("4")
        if color:
            codes.append(colors[color])
        if bg_color:
            codes.append(bg_colors[bg_color])

        if not codes:
            return text

        start_code = "\033[" + ";".join(codes) + "m"
        end_code = "\033[0m"

        return f"{start_code}{text}{end_code}"

    @staticmethod
    def progress_bar(
        current: int,
        total: int,
        *,
        width: int = 50,
        prefix: str = "",
        suffix: str = "",
        fill: str = "█",
        empty: str = "░",
    ) -> str:
        """Generate a text-based progress bar.

        Args:
            current: Current progress value
            total: Total/maximum value
            width: Width of progress bar (keyword-only, default 50)
            prefix: Text before progress bar (keyword-only)
            suffix: Text after progress bar (keyword-only)
            fill: Character for filled portion (keyword-only)
            empty: Character for empty portion (keyword-only)

        Returns:
            Formatted progress bar string

        Examples:
            >>> Terminal.progress_bar(50, 100)
            # Terminal: 50%|█████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░| 50/100
            '50%|█████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░| 50/100'

            >>> Terminal.progress_bar(3, 10, prefix="Downloading:", width=20)
            # Terminal: Downloading: 30%|██████░░░░░░░░░░░░░░| 3/10
            'Downloading: 30%|██████░░░░░░░░░░░░░░| 3/10'
        """
        percent = 100.0 if total == 0 else min(100.0, (current / total) * 100)
        filled_width = int(width * current // total) if total > 0 else width
        bar = fill * filled_width + empty * (width - filled_width)

        result = f"{percent:.0f}%|{bar}| {current}/{total}"

        if prefix:
            result = f"{prefix} {result}"
        if suffix:
            result = f"{result} {suffix}"

        return result

    @staticmethod
    def validate_input(
        message: str, *, validator: Callable[[str], bool], error_message: str | None = None
    ) -> str:
        """Prompt for input with custom validation.

        Args:
            message: The prompt message to display
            validator: Function that returns True if input is valid (keyword-only)
            error_message: Custom error message (keyword-only)

        Returns:
            Validated input string

        Examples:
            >>> Terminal.validate_input("Email", validator=lambda x: "@" in x)
            # Terminal: Email: invalid
            #           Invalid input. Please try again.
            #           Email: user@example.com
            'user@example.com'

            >>> Terminal.validate_input("Code", validator=lambda x: x.isdigit())
            # Terminal: Code: abc
            #           Invalid input. Please try again.
            #           Code: 12345
            '12345'
        """
        # Wrap the simple bool validator into the tuple format expected by prompt()
        def wrapped_validator(value: str) -> tuple[bool, str | None]:
            is_valid = validator(value)
            if is_valid:
                return (True, None)
            return (False, error_message or "Invalid input. Please try again.")

        return Terminal.prompt(message, validator=wrapped_validator)
