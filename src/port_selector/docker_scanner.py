"""Scan docker-compose files for used ports."""

import os
import re
from pathlib import Path
from typing import Set
import yaml


class DockerComposeScanner:
    """Scanner for docker-compose files to extract used ports."""

    COMPOSE_FILES = ['docker-compose.yml', 'docker-compose.yaml']

    def __init__(self, root_dir: str = '.'):
        self.root_dir = Path(root_dir).resolve()

    def scan_directory(self) -> Set[int]:
        """Recursively scan directory for docker-compose files and extract ports.

        Returns:
            Set of port numbers found in docker-compose files.
        """
        ports = set()

        for compose_file in self._find_compose_files():
            ports.update(self._extract_ports_from_file(compose_file))

        return ports

    def _find_compose_files(self):
        """Find all docker-compose files recursively."""
        for root, _, files in os.walk(self.root_dir):
            for filename in files:
                if filename in self.COMPOSE_FILES:
                    yield Path(root) / filename

    def _extract_ports_from_file(self, file_path: Path) -> Set[int]:
        """Extract port numbers from a docker-compose file.

        Args:
            file_path: Path to docker-compose file

        Returns:
            Set of port numbers found in the file
        """
        ports = set()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Try to parse as YAML
            try:
                data = yaml.safe_load(content)
                if data:
                    ports.update(self._extract_ports_from_yaml(data))
            except yaml.YAMLError:
                pass

            # Also use regex to catch ports in various formats
            ports.update(self._extract_ports_with_regex(content))

        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")

        return ports

    def _extract_ports_from_yaml(self, data: dict) -> Set[int]:
        """Extract ports from parsed YAML data."""
        ports = set()

        if not isinstance(data, dict):
            return ports

        # Check services section
        services = data.get('services', {})
        if isinstance(services, dict):
            for service_name, service_config in services.items():
                if isinstance(service_config, dict):
                    # Check ports array
                    service_ports = service_config.get('ports', [])
                    if isinstance(service_ports, list):
                        for port_mapping in service_ports:
                            ports.update(self._parse_port_mapping(port_mapping))

                    # Check expose array
                    exposed_ports = service_config.get('expose', [])
                    if isinstance(exposed_ports, list):
                        for port in exposed_ports:
                            ports.update(self._parse_port_value(port))

        return ports

    def _parse_port_mapping(self, mapping) -> Set[int]:
        """Parse port mapping like '8080:80' or '8080'."""
        ports = set()

        if isinstance(mapping, int):
            ports.add(mapping)
        elif isinstance(mapping, str):
            # Handle formats like "8080:80", "127.0.0.1:8080:80", "8080"
            parts = mapping.split(':')
            for part in parts:
                # Try to extract numbers
                numbers = re.findall(r'\d+', part)
                for num_str in numbers:
                    try:
                        port = int(num_str)
                        if 1 <= port <= 65535:
                            ports.add(port)
                    except ValueError:
                        pass

        return ports

    def _parse_port_value(self, value) -> Set[int]:
        """Parse a port value (int or string)."""
        ports = set()

        if isinstance(value, int):
            if 1 <= value <= 65535:
                ports.add(value)
        elif isinstance(value, str):
            numbers = re.findall(r'\d+', value)
            for num_str in numbers:
                try:
                    port = int(num_str)
                    if 1 <= port <= 65535:
                        ports.add(port)
                except ValueError:
                    pass

        return ports

    def _extract_ports_with_regex(self, content: str) -> Set[int]:
        """Extract ports using regex patterns as fallback."""
        ports = set()

        # Pattern for port mappings like "8080:80" or "- 8080"
        patterns = [
            r'[\"\']?(\d{1,5}):(\d{1,5})[\"\']?',  # "8080:80"
            r'-\s+[\"\']?(\d{1,5})[\"\']?',         # - "8080"
            r'expose:\s*\n\s*-\s*(\d{1,5})',        # expose: - 8080
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                for group in match.groups():
                    if group:
                        try:
                            port = int(group)
                            if 1 <= port <= 65535:
                                ports.add(port)
                        except ValueError:
                            pass

        return ports
