// Power Query (M) for the six queries in UKI_Coverage_Audit.pbix.
// Paths are relative to the data folder in this repository. In Power BI
// Desktop, point each Source step at your local copy of that folder.
// The folder combine for Forecast is the one worth reading: 47 weekly
// files become one table, and a file dropped into the folder is picked
// up on Refresh with no change to the query.

// ===================================================== Accounts
let
    Source = Csv.Document(File.Contents("data\coverage_accounts.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {
        {"account_id", type text}, {"account_name", type text}, {"parent_company", type text},
        {"vertical", type text}, {"segment", type text}, {"country", type text}, {"region", type text},
        {"territory_id", type text}, {"territory_name", type text}, {"rep_name", type text},
        {"employee_band", type text}, {"estimated_tam", Int64.Type}, {"health", type text},
        {"issue_type", type text}, {"issue_severity", type text}, {"severity_rank", Int64.Type},
        {"tam_at_risk", Int64.Type}, {"active_bid", type text}, {"hierarchy_status", type text},
        {"resolution_status", type text}}),
    AtRiskFlag = Table.AddColumn(Typed, "at_risk_flag", each
        if [issue_severity] = "High" then "High"
        else if [issue_severity] = "Medium" then "Medium"
        else "Low or none", type text),
    CleanTam = Table.AddColumn(AtRiskFlag, "tam_clean", each [estimated_tam] - [tam_at_risk], Int64.Type)
in
    CleanTam

// ===================================================== Reps
let
    Source = Csv.Document(File.Contents("data\rep_impact.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {
        {"rep_id", type text}, {"rep_name", type text}, {"team", type text}, {"role_type", type text},
        {"current_tam", Int64.Type}, {"corrected_tam", Int64.Type}, {"tam_delta", Int64.Type},
        {"tam_delta_pct", type number}, {"current_quota", Int64.Type}, {"corrected_quota", Int64.Type},
        {"quota_delta", Int64.Type}, {"direction", type text}})
in
    Typed

// ===================================================== Movements
let
    Source = Csv.Document(File.Contents("data\tam_movements.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {
        {"rep_name", type text}, {"movement_type", type text}, {"movement_reason", type text},
        {"amount", Int64.Type}})
in
    Typed

// ===================================================== Cases
let
    Source = Csv.Document(File.Contents("data\case_flow.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {
        {"case_id", type text}, {"account_id", type text}, {"vertical", type text}, {"issue_type", type text},
        {"owning_team", type text}, {"implementation_status", type text}, {"is_stalled", type text},
        {"days_open", Int64.Type}, {"date_opened", type date}, {"month_opened", type date}})
in
    Typed

// ===================================================== Forecast  (folder combine)
// Built with Get data > Folder > Combine & Transform Data. Power BI generates
// the helper queries (Sample File, Transform Sample File, Transform File,
// Parameter1); this is the resulting main query with the two added steps.
let
    Source = Folder.Files("data\forecast\ForecastSubmissions"),
    FilteredHidden = Table.SelectRows(Source, each [Attributes]?[Hidden]? <> true),
    Invoked = Table.AddColumn(FilteredHidden, "Transform File", each #"Transform File"([Content])),
    Renamed = Table.RenameColumns(Invoked, {"Name", "Source.Name"}),
    Kept = Table.SelectColumns(Renamed, {"Source.Name", "Transform File"}),
    Expanded = Table.ExpandTableColumn(Kept, "Transform File", Table.ColumnNames(#"Transform File"(#"Sample File"))),
    Typed = Table.TransformColumnTypes(Expanded, {
        {"Source.Name", type text}, {"market", type text}, {"fiscal_week", type text},
        {"week_number", Int64.Type}, {"week_ending", type date}, {"product_line", type text},
        {"forecast_units", Int64.Type}, {"forecast_revenue", Int64.Type}}),
    Key = Table.AddColumn(Typed, "key", each [market] & "|" & [fiscal_week], type text)
in
    Key

// ===================================================== Plan
let
    Source = Csv.Document(File.Contents("data\forecast\Plan\plan_revenue.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {
        {"market", type text}, {"fiscal_week", type text}, {"week_number", Int64.Type},
        {"week_ending", type date}, {"plan_revenue", Int64.Type}}),
    Key = Table.AddColumn(Typed, "key", each [market] & "|" & [fiscal_week], type text)
in
    Key
