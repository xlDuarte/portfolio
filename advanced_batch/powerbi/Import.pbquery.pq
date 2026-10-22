// Power Query M example only, not executed by any Tabular engine.
// Set DataFile Power BI Text parameter to exported synthetic_bi.csv.
let
    Source = Csv.Document(File.Contents(DataFile),[Delimiter=",",Encoding=65001,QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source,[PromoteAllScalars=true]),
    Columns = Table.TransformColumnTypes(Headers,
        {{"line", type text},{"planned_min", Int64.Type},{"good_units", Int64.Type},
         {"good_ideal_min", type number},{"revenue_brl", type number}})
in
    Columns
