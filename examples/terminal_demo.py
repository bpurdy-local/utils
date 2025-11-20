"""Example demonstrating Terminal utility class functionality."""

from utils import Terminal


def main():
    """Demonstrate Terminal utility features."""
    Terminal.print_box("Terminal Utilities Demo", width=50)
    Terminal.print_line("=", width=50)
    print()

    # 1. Basic prompts
    print("1. Basic Text Input:")
    name = Terminal.prompt("Enter your name", default="User")
    print(f"   Hello, {name}!\n")

    # 2. Confirmation
    print("2. Yes/No Confirmation:")
    if Terminal.confirm("Continue with demo?", default=True):
        print("   Great! Continuing...\n")
    else:
        print("   Exiting...\n")
        return

    # 3. Choice selection
    print("3. Multiple Choice:")
    env = Terminal.choice("Select environment", choices=["dev", "staging", "prod"], default="dev")
    print(f"   Selected: {env}\n")

    # 4. Numbered selection
    print("4. Numbered Selection:")
    idx, fruit = Terminal.select("Choose a fruit", options=["Apple", "Banana", "Cherry"])
    print(f"   You selected #{idx + 1}: {fruit}\n")

    # 5. Integer input with validation
    print("5. Integer Input with Validation:")
    age = Terminal.prompt_int("Enter your age", min_val=0, max_val=120, default=25)
    print(f"   Age: {age}\n")

    # 6. Float input with validation
    print("6. Float Input with Validation:")
    rate = Terminal.prompt_float("Enter rate (0-1)", min_val=0.0, max_val=1.0, default=0.5)
    print(f"   Rate: {rate}\n")

    # 7. Custom validation
    print("7. Custom Validation:")
    email = Terminal.validate_input(
        "Enter email",
        validator=lambda x: "@" in x and "." in x,
        error_message="Invalid email format",
    )
    print(f"   Email: {email}\n")

    # 8. Formatting examples
    print("8. Terminal Formatting:")
    Terminal.print_line("-", width=50)

    # Colorized output
    success = Terminal.colorize("✓ Success!", color="green", bold=True)
    error = Terminal.colorize("✗ Error!", color="red", bold=True)
    warning = Terminal.colorize("⚠ Warning!", color="yellow")
    info = Terminal.colorize("i Info", color="blue")

    print(f"   {success}")
    print(f"   {error}")
    print(f"   {warning}")
    print(f"   {info}\n")

    # Progress bar
    print("9. Progress Bar:")
    for i in range(0, 101, 25):
        progress = Terminal.progress_bar(i, 100, prefix="Progress:", width=30)
        print(f"   {progress}")
    print()

    # Box formatting
    Terminal.print_box("Demo Complete!\nThank you for trying the Terminal utility.", padding=1)


if __name__ == "__main__":
    main()
