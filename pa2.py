#name: Ibraheem Shami
#student id: 041164649

import xml.etree.ElementTree as ET
import json

tree = ET.parse("PA2_sample1.xml")
root = tree.getroot()
site = root.get("site")

skipped_devices = 0
total_devices = 0
roles = {}
interfaces = {"up": 0, "down": 0, "other": 0}


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
    
    for interface in device.findall("interface"):
        status = interface.get("status")

        if status == "up":
            interfaces["up"] += 1
        elif status == "down":
            interfaces["down"] += 1
        else:
            interfaces["other"] += 1

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
    "violations": [],
    "compliant": []
}

with open("audit.json", "w") as file:
    json.dump(report, file, indent=4)

print("Report saved to audit.json")