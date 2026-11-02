# Rule guide

All rules evaluate critical/high vendors. Thresholds and suppressions are described in [configuration](config.md); drill evidence is described in [drills](drills.md). Use `resilint explain RL004` for the same offline guidance. Examples illustrate evidence to record after a real change or verification.

Draft, not legal advice. Regulation references are a draft mapping and do not establish compliance.

## RL001: missing-notification-sla

Severity: **high**.

A critical/high vendor has no incident-notification commitment recorded. Record the hours agreed in the contract.

```yaml
notification_sla_hours: 24
```

Draft references: DORA Art. 30(3)(b), 30(2)(f); NIS2 Art. 21(2)(d); PRA SS2/21 ch. 6.

## RL002: missing-recovery-time

Severity: **high**.

A critical/high vendor has no recovery-time commitment recorded. Record the agreed recovery time in hours.

```yaml
recovery_time_hours: 4
```

Draft references: DORA Art. 30(2)(e), 30(3)(a); NIS2 Art. 21(2)(c); PRA SS2/21 ch. 6.

## RL003: no-contact

Severity: **high**.

A critical/high vendor has no email or phone contact. Record a verified incident contact.

```yaml
contacts:
  - email: incidents@example.test
```

Draft references: DORA Art. 30(2); NIS2 Art. 21(2)(d); PRA SS2/21 ch. 6.

## RL004: no-exit-plan

Severity: **high**.

A critical/high vendor has no documented exit plan. Create or locate the plan and record its reference.

```yaml
exit_plan: docs/exit/example-vendor.md
```

Draft references: DORA Art. 28(8), Art. 30(3)(f); NIS2 Art. 21(2)(d); PRA SS2/21 ch. 10.

## RL005: stale-or-missing-test

Severity: **medium**.

A critical/high vendor has no test date, or its test is older than stale_days. Complete a resilience test and record its actual date; replace YYYY-MM-DD below.

```yaml
last_tested: YYYY-MM-DD
```

Draft references: DORA Art. 30(3)(c)-(d); NIS2 Art. 21(2)(f); PRA SS2/21 ch. 10.

## RL006: recovery-exceeds-rto

Severity: **high**.

A critical/high vendor's recovery time exceeds a supported process's RTO. Resolve the mismatch and record the agreed commitment; the example assumes a 4h RTO.

```yaml
recovery_time_hours: 4
```

Draft references: DORA Art. 30(2)(e), 30(3)(a); NIS2 Art. 21(2)(c); PRA SS2/21 ch. 10.

## RL007: concentration-risk

Severity: **medium**.

A critical/high vendor supports more critical processes than max_critical. Review concentration and recovery options, keeping all actual dependencies recorded. Update this list only after a real dependency change.

```yaml
supports_processes: [example-process]
```

Draft references: DORA Art. 28(4)(c), Art. 29; NIS2 Art. 21(2)(d); PRA SS2/21 ch. 5.

## RL008: stale-or-missing-contact-verification

Severity: **medium**.

A critical/high vendor's contacts lack verification or are older than contact_days. Verify the contacts and record the actual date; replace YYYY-MM-DD below.

```yaml
contacts_verified: YYYY-MM-DD
```

Draft references: DORA Art. 30(2), 28(3); NIS2 Art. 21(2)(d); PRA SS2/21 ch. 6.

## RL009: last-drill-failed

Severity: **medium**.

The latest applied drill for a critical/high vendor failed. Address the failure, rerun the drill, then record the actual result and date. The example is for a completed successful retest; replace the vendor and date.

```bash
resilint drill record vendors.yaml --vendor example-vendor --kind test --result pass --date YYYY-MM-DD
```

Draft references: DORA Art. 30(3)(c), Art. 11(6); NIS2 Art. 21(2)(c), 21(2)(f); PRA SS2/21 ch. 10.
