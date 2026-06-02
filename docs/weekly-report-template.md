# Weekly AI Coding Metrics

- period: `weekly`
- generated_at: `{{ generated_at }}`

## KPI Snapshot

| KPI | Value |
| --- | ---: |
| Total issues | {{ total_issues }} |
| Success rate | {{ success_rate }}% |
| First-pass rate | {{ first_pass_rate }}% |
| Rework rate | {{ rework_rate }}% |
| Gate pass rate | {{ gate_pass_rate }}% |
| Avg lead time (ms) | {{ avg_lead_time_ms }} |

## Trend

- success_rate_delta_pp: `{{ success_rate_delta_pp }}`
- first_pass_rate_delta_pp: `{{ first_pass_rate_delta_pp }}`
- rework_rate_delta_pp: `{{ rework_rate_delta_pp }}`
- gate_pass_rate_delta_pp: `{{ gate_pass_rate_delta_pp }}`
- avg_lead_time_ms_delta: `{{ avg_lead_time_ms_delta }}`

## Top 3 Blockers

- `{{ blocker_1_category }}`: `{{ blocker_1_count }}` (`{{ blocker_1_share }}%`)
- `{{ blocker_2_category }}`: `{{ blocker_2_count }}` (`{{ blocker_2_share }}%`)
- `{{ blocker_3_category }}`: `{{ blocker_3_count }}` (`{{ blocker_3_share }}%`)

## Notes

- Data source: `.automation/execution-metrics.jsonl`
- Lead time is measured from GitHub issue creation to automation completion when timestamps are available.
