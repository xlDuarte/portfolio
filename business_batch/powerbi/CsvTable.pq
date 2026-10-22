// Power Query M — function for local CSV imports, no SAP or Power BI API connection.
// In Power BI Desktop: Manage Parameters > create DataFolder (Text)
// pointing to absolute path of business_batch/exports/raw.
// Create a blank query named CsvTable, paste this code in Advanced Editor.
(name as text) as table =>
let
    Source = Csv.Document(
        File.Contents(DataFolder & "/" & name & ".csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    Headers
