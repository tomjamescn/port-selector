"""Interactive CLI for port selection."""

import sys
import click
from pathlib import Path
from typing import Optional

from .docker_scanner import DockerComposeScanner
from .port_checker import PortChecker


def print_header(text: str):
    """Print a formatted header."""
    click.echo()
    click.echo(click.style(f"{'=' * 60}", fg='cyan'))
    click.echo(click.style(f"  {text}", fg='cyan', bold=True))
    click.echo(click.style(f"{'=' * 60}", fg='cyan'))
    click.echo()


def print_section(text: str):
    """Print a formatted section header."""
    click.echo()
    click.echo(click.style(f"--- {text} ---", fg='yellow', bold=True))


def print_success(text: str):
    """Print success message."""
    click.echo(click.style(f"✓ {text}", fg='green'))


def print_warning(text: str):
    """Print warning message."""
    click.echo(click.style(f"⚠ {text}", fg='yellow'))


def print_info(text: str):
    """Print info message."""
    click.echo(click.style(f"ℹ {text}", fg='blue'))


def print_error(text: str):
    """Print error message."""
    click.echo(click.style(f"✗ {text}", fg='red'))


@click.command()
@click.option(
    '--start-port',
    type=int,
    help='Start of port range (will prompt if not provided)'
)
@click.option(
    '--end-port',
    type=int,
    help='End of port range (will prompt if not provided)'
)
@click.option(
    '--scan-dir',
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help='Directory to scan for docker-compose files (will prompt if not provided)'
)
@click.option(
    '--count',
    type=int,
    default=5,
    help='Number of available ports to find (default: 5)'
)
@click.option(
    '--non-interactive',
    is_flag=True,
    help='Run in non-interactive mode with default values'
)
def main(
    start_port: Optional[int],
    end_port: Optional[int],
    scan_dir: Optional[str],
    count: int,
    non_interactive: bool
):
    """Interactive CLI tool to find available ports.

    This tool helps you find available ports by:
    1. Scanning docker-compose files for used ports
    2. Checking port availability with lsof
    3. Presenting available ports in your specified range
    """
    print_header("Port Selector - Find Available Ports")

    # Interactive mode for getting parameters
    if not non_interactive:
        # Get port range
        if start_port is None:
            start_port = click.prompt(
                click.style('\nEnter start port', fg='cyan'),
                type=int,
                default=8000
            )

        if end_port is None:
            end_port = click.prompt(
                click.style('Enter end port', fg='cyan'),
                type=int,
                default=9000
            )

        # Validate port range
        if start_port > end_port:
            print_error("Start port must be less than or equal to end port!")
            sys.exit(1)

        if start_port < 1 or end_port > 65535:
            print_error("Ports must be in range 1-65535!")
            sys.exit(1)

        # Get scan directory
        if scan_dir is None:
            default_dir = '.'
            scan_dir_input = click.prompt(
                click.style('\nEnter directory to scan for docker-compose files', fg='cyan'),
                type=str,
                default=default_dir
            )
            scan_dir = scan_dir_input

        # Get number of ports to find
        count = click.prompt(
            click.style('\nHow many available ports do you want to find?', fg='cyan'),
            type=int,
            default=count
        )

    else:
        # Non-interactive mode with defaults
        start_port = start_port or 8000
        end_port = end_port or 9000
        scan_dir = scan_dir or '.'

    # Display configuration
    print_section("Configuration")
    print_info(f"Port range: {start_port} - {end_port}")
    print_info(f"Scan directory: {Path(scan_dir).resolve()}")
    print_info(f"Ports to find: {count}")

    # Step 1: Scan docker-compose files
    print_section("Step 1: Scanning docker-compose files")
    scanner = DockerComposeScanner(scan_dir)

    try:
        excluded_ports = scanner.scan_directory()

        if excluded_ports:
            print_success(f"Found {len(excluded_ports)} ports in docker-compose files")

            # Filter to only show ports in our range
            excluded_in_range = [p for p in sorted(excluded_ports) if start_port <= p <= end_port]

            if excluded_in_range:
                print_warning(f"Excluded ports in range {start_port}-{end_port}:")
                for port in excluded_in_range:
                    click.echo(f"  - {port}")
            else:
                print_info("No excluded ports in the specified range")
        else:
            print_info("No docker-compose files found or no ports defined")

    except Exception as e:
        print_error(f"Error scanning docker-compose files: {e}")
        excluded_ports = set()

    # Step 2: Find available ports
    print_section("Step 2: Finding available ports")
    print_info("Checking port availability...")

    checker = PortChecker()
    available_ports = checker.find_available_ports(
        start_port,
        end_port,
        excluded_ports,
        count
    )

    # Step 3: Verify and display results
    print_section("Step 3: Available Ports")

    if not available_ports:
        print_warning(f"No available ports found in range {start_port}-{end_port}")
        sys.exit(0)

    print_success(f"Found {len(available_ports)} available port(s):")
    click.echo()

    for port, status in available_ports:
        # Double-check with lsof
        in_use, description = checker.is_port_in_use(port)

        if in_use:
            click.echo(
                f"  Port {click.style(str(port), fg='red', bold=True)}: "
                f"{click.style('IN USE', fg='red')} - {description}"
            )
        else:
            click.echo(
                f"  Port {click.style(str(port), fg='green', bold=True)}: "
                f"{click.style('AVAILABLE', fg='green')} ✓"
            )

    # Summary
    print_section("Summary")
    available_count = sum(1 for _, status in available_ports)
    print_success(f"Total available ports: {available_count}")

    if available_ports:
        first_port = available_ports[0][0]
        print_info(f"First available port: {click.style(str(first_port), fg='green', bold=True)}")

    click.echo()


if __name__ == '__main__':
    main()
