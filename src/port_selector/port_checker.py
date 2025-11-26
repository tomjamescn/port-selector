"""Check if ports are available."""

import subprocess
import socket
from typing import Set, List, Tuple


class PortChecker:
    """Check port availability using various methods."""

    @staticmethod
    def is_port_in_use(port: int) -> Tuple[bool, str]:
        """Check if a port is in use.

        Args:
            port: Port number to check

        Returns:
            Tuple of (is_in_use, description)
        """
        # Method 1: Try using lsof (Linux/Mac)
        lsof_result = PortChecker._check_with_lsof(port)
        if lsof_result[0]:
            return lsof_result

        # Method 2: Try to bind to the port
        socket_result = PortChecker._check_with_socket(port)
        return socket_result

    @staticmethod
    def _check_with_lsof(port: int) -> Tuple[bool, str]:
        """Check port using lsof command.

        Returns:
            Tuple of (is_in_use, description)
        """
        try:
            result = subprocess.run(
                ['lsof', f'-i:{port}', '-P', '-n'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0 and result.stdout.strip():
                # Parse lsof output to get process info
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    # First line is header, second line has process info
                    parts = lines[1].split()
                    if len(parts) >= 2:
                        process_name = parts[0]
                        pid = parts[1]
                        return True, f"Used by {process_name} (PID: {pid})"

                return True, "Port is in use (lsof)"

            return False, ""

        except FileNotFoundError:
            # lsof not available
            return False, ""
        except subprocess.TimeoutExpired:
            return False, ""
        except Exception:
            return False, ""

    @staticmethod
    def _check_with_socket(port: int) -> Tuple[bool, str]:
        """Check port by trying to bind to it.

        Returns:
            Tuple of (is_in_use, description)
        """
        # Check TCP
        tcp_in_use = PortChecker._try_bind(port, socket.SOCK_STREAM)

        # Check UDP
        udp_in_use = PortChecker._try_bind(port, socket.SOCK_DGRAM)

        if tcp_in_use and udp_in_use:
            return True, "TCP and UDP in use"
        elif tcp_in_use:
            return True, "TCP in use"
        elif udp_in_use:
            return True, "UDP in use"
        else:
            return False, "Available"

    @staticmethod
    def _try_bind(port: int, sock_type: int) -> bool:
        """Try to bind to a port.

        Returns:
            True if port is in use (bind failed), False if available
        """
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, sock_type)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('127.0.0.1', port))
            return False  # Successfully bound, port is available
        except OSError:
            return True  # Bind failed, port is in use
        finally:
            if sock:
                sock.close()

    @staticmethod
    def find_available_ports(
        start_port: int,
        end_port: int,
        excluded_ports: Set[int],
        count: int = 5
    ) -> List[Tuple[int, str]]:
        """Find available ports in range.

        Args:
            start_port: Start of port range
            end_port: End of port range
            excluded_ports: Ports to exclude from search
            count: Maximum number of ports to return

        Returns:
            List of tuples (port, status_description)
        """
        available = []

        for port in range(start_port, end_port + 1):
            if port in excluded_ports:
                continue

            in_use, description = PortChecker.is_port_in_use(port)
            if not in_use:
                available.append((port, "Available"))

                if len(available) >= count:
                    break

        return available

    @staticmethod
    def check_ports_status(ports: List[int]) -> List[Tuple[int, bool, str]]:
        """Check status of multiple ports.

        Args:
            ports: List of port numbers to check

        Returns:
            List of tuples (port, is_in_use, description)
        """
        results = []
        for port in ports:
            in_use, description = PortChecker.is_port_in_use(port)
            results.append((port, in_use, description))

        return results
