"""Regenerate the deterministic fictional register; no real vendor data or network."""

from pathlib import Path

import yaml


def register() -> dict:
    processes = [{"id": f"fictional-process-{i}", "name": f"Fictional shared process {i}",
                  "criticality": "critical", "rto_hours": 4} for i in range(4)]
    vendors = []
    for i in range(500):
        vendors.append({
            "id": f"fictional-vendor-{i:04d}", "name": f"Fictional Vendor {i:04d}",
            "criticality": ("critical", "high", "medium", "low")[i % 4],
            "notification_sla_hours": None if i % 8 == 0 else 24,
            "recovery_time_hours": None if i % 8 == 1 else 8,
            "contacts": [] if i % 8 == 0 else [{"email": f"incidents-{i}@example.test"}],
            "exit_plan": False, "last_tested": None, "contacts_verified": None,
            "country": ("GB", "IE", "US")[i % 3],
            "supports_processes": [p["id"] for p in processes] if i % 8 == 0 else [
                processes[i % 4]["id"]],
        })
    return {"schema_version": 1, "processes": processes, "vendors": vendors}


def main() -> None:
    data = register()
    lines = ["# FICTIONAL validation data: no actual vendors, people or drill events.",
             "schema_version: 1", "processes:"]
    for process in data["processes"]:
        lines.append("  - " + yaml.safe_dump(process, default_flow_style=True,
                                          sort_keys=False, width=1000).strip())
    lines.append("vendors:")
    for vendor in data["vendors"]:
        lines.append("  - " + yaml.safe_dump(vendor, default_flow_style=True,
                                          sort_keys=False, width=1000).strip())
    Path(__file__).with_name("vendors.yaml").write_text("\n".join(lines) + "\n",
                                                       encoding="utf-8")


if __name__ == "__main__":
    main()
