#name: Ibraheem Shami
#student id: 041164649

import xml.etree.ElementTree as ET
import json
import yaml

tree = ET.parse("PA2_sample1.xml")
root = tree.getroot()
site = root.get("site")

with open("PA2_policy.yaml", "r") as file:
    policy = yaml.safe_load(file)

print("Policy:", policy)

skipped_devices = 0
total_devices = 0
roles = {}
interfaces = {"up": 0, "down": 0, "other": 0}
violations = []


for device in root.findall("device"):
    device_id = device.get("id")

    if device_id is None:
        skipped_devices += 1
        continue

    total_devices += 1
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
    "compliant": []
}

with open("audit.json", "w") as file:
    json.dump(report, file, indent=4)

print("Report saved to audit.json")