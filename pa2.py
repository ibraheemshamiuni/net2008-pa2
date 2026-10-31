#name: Ibraheem Shami
#student id: 041164649

import sys
import xml.etree.ElementTree as ET
import json
import yaml

class AuditError(Exception):
    """Represent an error while reading audit input files."""
    pass

class AuditReport:
    """Store and save an audit report."""

    def __init__(self, data):
        self.data = data

    def save(self, filename):
        """Write the report data to a JSON file."""
        with open(filename, "w") as file:
            json.dump(self.data, file, indent=4)


def version_parts(version):
    """Convert an OS version into a tuple of numbers."""
    if not version:
        return (0,)

    try:
        return tuple(int(part) for part in str(version).split("."))
    except ValueError:
        raise AuditError(f"Invalid OS version: {version}")


def is_outdated(found, required):
    """Return True if an OS version is older than required."""
    found_parts = version_parts(found)
    required_parts = version_parts(required)

    length = max(len(found_parts), len(required_parts))

    found_parts += (0,) * (length - len(found_parts))
    required_parts += (0,) * (length - len(required_parts))

    return found_parts < required_parts


def main():
    if len(sys.argv) != 3:
        print("usage: python pa2.py DEVICES.xml POLICY.yaml")
        sys.exit(2)

    try:
        tree = ET.parse(sys.argv[1])
        root = tree.getroot()
        site = root.get("site")

        with open(sys.argv[2], "r") as file:
            policy = yaml.safe_load(file)

        if policy is None:
            policy = {}

        if not isinstance(policy, dict):
            raise AuditError("Policy must be a YAML mapping")

    except (OSError, ET.ParseError, yaml.YAMLError, AuditError) as error:
        print(f"Error reading {sys.argv[1]} or {sys.argv[2]}: {error}")
        sys.exit(1)


    skipped_devices = 0
    total_devices = 0
    roles = {}
    interfaces = {"up": 0, "down": 0, "other": 0}
    violations = []
    compliant = []

    for device in root.findall("device"):
        device_id = device.get("id")

        if device_id is None:
            skipped_devices += 1
            continue

        total_devices += 1
        violations_before = len(violations)
        role = device.get("role")

        if role in roles:
            roles[role] += 1
        else:
            roles[role] = 1

        min_os = policy.get("min_os", {})

        if min_os and role not in min_os:
            violations.append({
                "id": device_id,
                "type": "unknown_role",
                "role": role
            })

        if role in min_os:
            found = device.get("os", "")
            required = str(min_os[role])

            try:
                outdated = is_outdated(found, required)
            except AuditError as error:
                print(f"Error in {sys.argv[1]}: {error}")
                sys.exit(1)

            if outdated:
                violations.append({
                    "id": device_id,
                    "type": "os_outdated",
                    "found": found,
                    "required": required
                })


        if policy.get("require_owner", False):
            owner = device.findtext("owner")

            if owner is None or owner.strip() == "":
                violations.append({
                    "id": device_id,
                    "type": "missing_owner"
                })

        device_down = 0
        for interface in device.findall("interface"):
            status = interface.get("status")

            if status == "up":
                interfaces["up"] += 1
            elif status == "down":
                interfaces["down"] += 1
                device_down += 1
            else:
                interfaces["other"] += 1

        if "max_down_interfaces" in policy:
            max_down = policy["max_down_interfaces"]

            if device_down > max_down:
                violations.append({
                    "id": device_id,
                    "type": "too_many_down",
                    "down": device_down
                })

        if len(violations) == violations_before:
            compliant.append(device_id)


        print(device_id)

    print("Total devices:", total_devices)
    print("Skipped devices:", skipped_devices)
    print("Roles:", roles)
    print("Interfaces:", interfaces)

    report = {
        "site": site,
        "total_devices": total_devices,
        "skipped_devices": skipped_devices,
        "roles": roles,
        "interfaces": interfaces,
        "violations": violations,
        "compliant": sorted(compliant)
    }

    audit = AuditReport(report)
    audit.save("audit.json")

    print("Report saved to audit.json")


if __name__ == "__main__":
    main()