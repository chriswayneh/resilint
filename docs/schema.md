# Register schema v1

[`schema/register.v1.json`](../schema/register.v1.json) is the repository-published JSON Schema for hierarchical vendor registers, using Draft 2020-12. It describes JSON objects and the equivalent YAML structure. It is available from a checkout; it is not a new CLI validation mode or a promise that schema files are installed in the Python package.

For an editor with YAML schema support, associate your register with the local schema file. From a register in `examples/`, a compatible YAML editor can use:

```yaml
# yaml-language-server: $schema=../schema/register.v1.json
schema_version: 1
vendors:
  - id: example-cloud
    criticality: high
```

All schema references are local fragments. The `$id` is an identifier; validation of a locally loaded copy does not need to download it. Editor integrations may have their own network settings. The application remains offline and does not load this schema at runtime.

## Fields

Only top-level `vendors`, each vendor's `id` and `criticality`, and each process's `id` are required. Other fields may be omitted; missing commitments are inputs to resilience rules rather than schema errors. Additional properties are allowed, matching the loader's treatment of unknown fields; this also means the schema does not catch misspelled optional keys.

| Top-level field | Type | Example and meaning |
| --- | --- | --- |
| `schema_version` | integer, exactly `1` | `1`; omission defaults to version 1 |
| `vendors` | array of vendor objects | `[{"id":"example-cloud","criticality":"high"}]`; may be empty |
| `processes` | array of process objects or null | `[{"id":"payroll","rto_hours":48}]`; omission/null means none |

| Vendor field | Type | Example and meaning |
| --- | --- | --- |
| `id` | nonblank string | `example-cloud`; unique vendor identity |
| `name` | string | `Example Cloud Ltd`; display name, defaults to id |
| `criticality` | `critical`, `high`, `medium` or `low` | `high`; only critical/high vendors receive rule checks |
| `notification_sla_hours` | nonnegative number or null | `4`; notification commitment in hours |
| `recovery_time_hours` | nonnegative number or null | `8`; recovery commitment in hours |
| `contacts` | array, semicolon-separated string or null | `[{"email":"incidents@example.com"}]`, `["+1-555-0100"]` or `a@example.com;b@example.com` |
| `exit_plan` | boolean, string or null | `true` or `docs/exit/example.md`; recorded existence/reference, no referenced file is opened |
| `last_tested` | ISO date string or null | `2026-06-01`; last resilience test |
| `contacts_verified` | ISO date string or null | `2026-09-01`; last contact verification |
| `lei` | uppercase 20-character string or null | `9845000EXAMPLE000048`; fictional example, runtime checks check digits |
| `country` | assigned uppercase two-letter code or null | `IE`; enum matches the loader's country-code snapshot |
| `supports_processes` | array of nonblank strings, semicolon-separated string or null | `["payroll","orders"]` or `payroll;orders` |

Contact array entries can be nonempty strings or objects containing at least one of the following fields. Contact details are recorded, not verified or contacted.

| Contact field | Type | Example |
| --- | --- | --- |
| `email` | nonempty string | `incidents@example.com` |
| `phone` | nonempty string | `+1-555-0100` |

| Process field | Type | Example and meaning |
| --- | --- | --- |
| `id` | nonblank string | `payroll` |
| `name` | string | `Payroll`; defaults to id |
| `criticality` | `critical`, `high`, `medium` or `low` | `critical`; omission defaults to critical |
| `rto_hours` | nonnegative number or null | `48`; recovery-time objective |

`exit_plan` follows existing loader semantics: false, null, an empty string, and case-insensitive `false`, `no`, `n`, `0`, `none`, `null` strings mean no plan; other nonblank strings mean a recorded plan.

## Validation and boundaries

Install development dependencies with `pip install -e ".[dev]"`, then run `pytest -q tests/test_schema.py`. The tests validate the schema itself, the YAML register example and a hierarchical projection of the loaded CSV register example, plus invalid and optional-field cases. The separate `examples/drills.yaml` is a drill log, not a register, and has a different format.

For a JSON document, validation from the repository root can use:

```python
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

schema = json.loads(Path("schema/register.v1.json").read_text(encoding="utf-8"))
document = json.loads(Path("register.json").read_text(encoding="utf-8"))
Draft202012Validator.check_schema(schema)
Draft202012Validator(schema, format_checker=FormatChecker()).validate(document)
```

Enable format checking to reject impossible dates. Some editors treat `format` as an annotation only; see the [JSON Schema validation specification](https://json-schema.org/draft/2020-12/json-schema-validation) and [jsonschema validation documentation](https://python-jsonschema.readthedocs.io/en/stable/validate/). YAML parsers may construct native date objects; convert those to ISO strings before JSON Schema validation.

The schema describes documented authoring forms and is intentionally stricter than some loader coercions: use numeric hours and schema version, lowercase criticalities, uppercase country/LEI values and ISO date strings. The CLI can also accept numeric strings, trim/case-normalize values and treat blank CSV fields as missing. Raw CSV is not a hierarchical JSON document: load it first, convert the normalized process mapping to an array, and serialize dates to ISO strings before schema validation. This projection checks parsed values, not CSV syntax; the CSV loader remains responsible for quoting, headers and row lengths.

Continue to run `resilint check` after schema validation. The schema does not enforce vendor-id uniqueness, LEI check digits, file size/encoding, YAML alias refusal, finite numeric conversion or business resilience rules. Process references are not foreign-key constraints: the current rule engine skips unknown process ids. Schema defaults document loader behavior and do not insert values into the document. Neither schema validity nor a clean report establishes regulatory compliance.
