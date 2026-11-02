# Vendor resilience gap report

- Vendors in register: **2**
- Critical/high vendors checked: **2**
- Vendors with gaps: **2**
- Findings: **6** high, **4** medium

| Severity | Vendor | Gap | Rule | Maps to |
|---|---|---|---|---|
| high | example-vendor-b | recovery time 8h exceeds process-a RTO 4h | RL006 | DORA Art. 30(2)(e), 30(3)(a); NIS2 Art. 21(2)(c); PRA SS2/21 ch. 10 |
| high | example-vendor-b | recovery time 8h exceeds process-b RTO 4h | RL006 | DORA Art. 30(2)(e), 30(3)(a); NIS2 Art. 21(2)(c); PRA SS2/21 ch. 10 |
| high | example&lt;vendor&gt;&#124;a | no incident notification SLA recorded | RL001 | DORA Art. 30(3)(b), 30(2)(f); NIS2 Art. 21(2)(d); PRA SS2/21 ch. 6 |
| high | example&lt;vendor&gt;&#124;a | no recovery time commitment recorded | RL002 | DORA Art. 30(2)(e), 30(3)(a); NIS2 Art. 21(2)(c); PRA SS2/21 ch. 6 |
| high | example&lt;vendor&gt;&#124;a | no email or phone contact recorded | RL003 | DORA Art. 30(2); NIS2 Art. 21(2)(d); PRA SS2/21 ch. 6 |
| high | example&lt;vendor&gt;&#124;a | no documented exit plan | RL004 | DORA Art. 28(8), Art. 30(3)(f); NIS2 Art. 21(2)(d); PRA SS2/21 ch. 10 |
| medium | example-vendor-b | no contact verification date recorded | RL008 | DORA Art. 30(2), 28(3); NIS2 Art. 21(2)(d); PRA SS2/21 ch. 6 |
| medium | example-vendor-b | most recent test on 2026-10-01 failed | RL009 | DORA Art. 30(3)(c), Art. 11(6); NIS2 Art. 21(2)(c), 21(2)(f); PRA SS2/21 ch. 10 |
| medium | example&lt;vendor&gt;&#124;a | no resilience test date recorded | RL005 | DORA Art. 30(3)(c)-(d); NIS2 Art. 21(2)(f); PRA SS2/21 ch. 10 |
| medium | example&lt;vendor&gt;&#124;a | supports 4 critical processes (threshold 3) | RL007 | DORA Art. 28(4)(c), Art. 29; NIS2 Art. 21(2)(d); PRA SS2/21 ch. 5 |

_Draft, not legal advice. References use a draft mapping. Generated offline by resilint 0.0.0._
