"""Local rule settings and explicit, expiring finding suppressions."""

from __future__ import annotations

import stat
from dataclasses import dataclass, replace
from datetime import date, datetime
from pathlib import Path

import yaml

from .loader import MAX_BYTES, InputError, _NoAliasLoader
from .rules import RULES, SEVERITIES, Finding


@dataclass(frozen=True)
class Ignore:
    rule: str
    vendor: str
    reason: str
    expires: date


@dataclass(frozen=True)
class Settings:
    fail_on: str = "high"
    stale_days: int = 365
    contact_days: int = 180
    max_critical: int = 3
    ignore: tuple[Ignore, ...] = ()
    source: str | None = None


def load_config(path: str | Path | None = None) -> Settings:
    """Use cwd/.resilint.yaml if present; an explicitly named file must exist."""
    file = Path(path) if path is not None else Path(".resilint.yaml")
    try:
        try:
            info = file.stat()
        except FileNotFoundError:
            if path is None and not file.is_symlink():
                return Settings()
            raise
        if not stat.S_ISREG(info.st_mode):
            raise InputError("config must be a regular file")
        if info.st_size > MAX_BYTES:
            raise InputError("config file larger than 5 MB")
        data = yaml.load(file.read_text(encoding="utf-8-sig"), Loader=_NoAliasLoader)
        return replace(_settings(data), source=str(file))
    except InputError as error:
        error.path = str(file)
        raise
    except (OSError, UnicodeError) as error:
        raise InputError(f"cannot read config ({error.__class__.__name__})",
                         path=str(file)) from None
    except yaml.YAMLError as error:
        mark = getattr(error, "problem_mark", None)
        line = mark.line + 1 if mark is not None else getattr(error, "line", 0)
        raise InputError("invalid config YAML", path=str(file), line=line) from None
    except RecursionError:
        raise InputError("config nested too deeply", path=str(file)) from None


def _settings(data) -> Settings:
    if data is None:
        return Settings()
    keys = {"fail_on", "stale_days", "contact_days", "max_critical", "ignore"}
    if not isinstance(data, dict) or any(key not in keys for key in data):
        raise InputError("config must be a mapping containing only supported settings")
    values = {key: getattr(Settings(), key) for key in keys - {"ignore"}}
    values.update({key: value for key, value in data.items() if key != "ignore"})
    if values["fail_on"] not in SEVERITIES:
        raise InputError("fail_on must be low, medium, high or critical")
    for key in ("stale_days", "contact_days", "max_critical"):
        if type(values[key]) is not int or values[key] < 0:
            raise InputError(f"{key} must be a non-negative integer")
    rows = data.get("ignore", [])
    if not isinstance(rows, list):
        raise InputError("ignore must be a list")
    ignores = []
    for index, row in enumerate(rows):
        context = f"ignore[{index}]"
        if not isinstance(row, dict) or set(row) != {"rule", "vendor", "reason", "expires"}:
            raise InputError(f"{context}: require rule, vendor, reason and expires only")
        for key in ("rule", "vendor", "reason"):
            if not isinstance(row[key], str) or not row[key].strip():
                raise InputError(f"{context}: {key} must be nonblank text")
        rule, vendor, reason = (row[key].strip() for key in ("rule", "vendor", "reason"))
        if rule not in RULES:
            raise InputError(f"{context}: unknown rule {rule!r}")
        expiry = row["expires"]
        if isinstance(expiry, str):
            try:
                parsed = date.fromisoformat(expiry)
                if parsed.isoformat() != expiry:
                    raise ValueError
                expiry = parsed
            except ValueError:
                raise InputError(f"{context}: expires must be an ISO date (YYYY-MM-DD)") from None
        if not isinstance(expiry, date) or isinstance(expiry, datetime):
            raise InputError(f"{context}: expires must be an ISO date (YYYY-MM-DD)")
        ignores.append(Ignore(rule, vendor, reason, expiry))
    return Settings(**values, ignore=tuple(ignores))


def apply_ignores(findings: list[Finding], settings: Settings,
                  today: date | None = None) -> list[Finding]:
    today = today or date.today()
    active = {(item.rule, item.vendor) for item in settings.ignore if item.expires >= today}
    return [finding for finding in findings if (finding.rule_id, finding.vendor) not in active]
