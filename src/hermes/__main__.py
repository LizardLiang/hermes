"""Main entry point for Hermes - supports both TUI and CLI modes."""

import sys


def main():
    """
    Main entry point that routes to TUI or CLI based on arguments.

    - No arguments: Launch interactive TUI
    - With arguments: Run CLI command
    """
    if len(sys.argv) == 1:
        # No arguments - launch TUI
        from hermes.tui.app import run_tui

        run_tui()
    else:
        # Has arguments - run CLI
        from hermes.cli import cli_main

        cli_main()


if __name__ == "__main__":
    main()
