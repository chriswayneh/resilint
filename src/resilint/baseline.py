"""Versioned, deterministic snapshots of finding identities."""

from __future__ import annotations

import hashlib
import json
import re
import stat
from pathlib import Path

from .loader import MAX_BYTES, InputError
from .rules import Finding


def fingerprint(finding: Finding) -> str:
    identity = json.dumps([finding.rule_id, finding.vendor, finding.field],
                          ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(identity.encode("ascii")).hexdigest()


def dump_baseline(findings: list[Finding]) -> str:
    text = json.dumps({"schema_version": 1,
                       "fingerprints": sorted({fingerprint(f) for f in findings})}, indent=2) + "\n"
    if len(text.encode("utf-8")) > MAX_BYTES:
        raise InputError("generated baseline larger than 5 MB")
    return text


def load_baseline(path: str | Path) -> set[str]:
    file = Path(path)
    try:
        info = file.stat()
        if not stat.S_ISREG(info.st_mode):
            raise InputError("baseline must be a regular file")
        if info.st_size > MAX_BYTES:
            raise InputError("baseline larger than 5 MB")
        data = json.loads(file.read_text(encoding="utf-8-sig"))
        if (not isinstance(data, dict) or set(data) != {"schema_version", "fingerprints"}
                or type(data["schema_version"]) is not int or data["schema_version"] != 1):
            raise InputError("baseline must contain schema_version 1 and fingerprints only")
        values = data["fingerprints"]
        if not isinstance(values, list) or any(
                not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value)
                for value in values):
            raise InputError("baseline fingerprints must be a list of SHA-256 hex strings")
        return set(values)
    except InputError as error:
        error.path = str(file)
        raise
    except json.JSONDecodeError as error:
        raise InputError("invalid baseline JSON", path=str(file), line=error.lineno) from None
    except (OSError, UnicodeError) as error:
        raise InputError(f"cannot read baseline ({error.__class__.__name__})",
                         path=str(file)) from None
    except (RecursionError, ValueError):
        raise InputError("invalid or excessively nested baseline", path=str(file)) from None


def new_findings(findings: list[Finding], known: set[str]) -> list[Finding]:
    return [finding for finding in findings if fingerprint(finding) not in known]
