# Build guide

How to rebuild `UKI_Coverage_Audit.pbix` from the data in this repository, or
open the file and trace how it was made. Power BI Desktop, free, no sign-in
needed.

## 1. Data

Clone the repository. The six sources are already in `data/`. To regenerate the
four coverage tables with the same seed:

```
python scripts/generate_data.py
```

Keep `data/forecast/late_submission/FC_W08_Benelux.csv` out of
`ForecastSubmissions/` until the refresh demo in step 6.

## 2. Load through Power Query

Home > Get data > Text/CSV for `coverage_accounts.csv`, `rep_impact.csv`,
`case_flow.csv`, `tam_movements.csv` and `forecast/Plan/plan_revenue.csv`.
Choose Transform Data, not Load, and check the column types match
`docs/DATA_DICTIONARY.md`. Rename the queries Accounts, Reps, Cases, Movements,
Plan.

On Accounts add two columns: a conditional column `at_risk_flag` from
`issue_severity`, and a custom column `tam_clean = [estimated_tam] - [tam_at_risk]`.

For the forecast: Home > Get data > Folder > `forecast/ForecastSubmissions` >
Combine & Transform Data > sample file "First file". Power BI generates the
helper queries; leave them. Rename the result Forecast. On both Forecast and
Plan add a custom column `key = [market] & "|" & [fiscal_week]`.

Full M for every query is in `powerquery/queries.m`. Close & Apply.

## 3. Model

Six tables in two subject areas that share no key, so they are kept apart.

```
Reps 1 ──< Accounts 1 ──< Cases          Plan 1 ──< Forecast
Reps 1 ──< Movements                       (on key = market|fiscal_week)
```

All single direction. Accounts joins Reps on `rep_name` and Cases on
`account_id`; Movements joins Reps on `rep_name`.

## 4. Measures

Paste each measure from `dax/measures.dax` on the table named in its heading.
Expected values are given so every measure can be checked as it lands. Format
money as whole number with thousands separator, percentages to one decimal.

## 5. Pages

**Account health.** Six cards (Defect rate, Total accounts, Defect accounts,
Total TAM, TAM at risk, % TAM at risk). Stacked bar: Total accounts by vertical
and health. Donut: Defect accounts by issue_type. Table: account_name,
parent_company, vertical, segment, health, issue_type, issue_severity, TAM at
risk, sorted by TAM at risk descending.

**TAM reconciliation.** Five cards (Opening TAM, Corrections, Reforecast,
Closing TAM, Tie-out). Table: rep_name, Opening TAM, Corrections, Reforecast,
Closing TAM, Variance to closing, Tie-out. Waterfall: amount by movement_type,
titled "TAM movement, corrections held apart from reforecast".

**Forecast consolidation.** Six cards (Forecast revenue, Plan revenue, Gap to
plan, % of plan, Completeness W08, Validation status). Line chart: Forecast
revenue and Plan revenue by Plan[fiscal_week], sorted W01 to W08. Table:
Plan[market], Forecast revenue, Plan revenue, Gap to plan, % of plan. Matrix:
rows Plan[market], columns Plan[fiscal_week], values Forecast revenue, with
Benelux W08 blank. Table of exceptions: Source.Name, market, fiscal_week,
product_line, forecast_units, forecast_revenue, filtered to forecast_units
less than 0.

Dimension fields on this page come from Plan, not Forecast, so a missing
submission shows as a gap rather than disappearing.

## 6. The refresh demo

Copy `FC_W08_Benelux.csv` from `late_submission/` into `ForecastSubmissions/`
and press Refresh. Completeness W08 moves from 5 of 6 to 6 of 6, Forecast
revenue from 22,843,250 to 23,151,850, Gap to plan from -922,350 to -613,750.
Validation status stays HOLD because the France negative line is still there.
Move the file back out and Refresh to reset.

## What is not built

Desktop only. Not published to the Power BI service; no scheduled refresh,
no row-level security, no dataflows. Those are the next steps, listed in the
README.
