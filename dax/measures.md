# DAX Measures Reference

All measures used across the 3 Power BI dashboard pages, grouped by page.
Table name used below: `final_dashboard_data`

---

## Page 1 — Overview

```dax
Total Revenue = SUM(final_dashboard_data[revenue])

Total Sessions = DISTINCTCOUNT(final_dashboard_data[session_id])

Total Customers = DISTINCTCOUNT(final_dashboard_data[user_id])

Conversion Rate =
DIVIDE(
    CALCULATE(COUNTROWS(final_dashboard_data), final_dashboard_data[purchase_completed] = TRUE),
    COUNTROWS(final_dashboard_data)
)

Avg Session Duration = AVERAGE(final_dashboard_data[session_duration_min])
```

---

## Page 2 — Segmentation

```dax
VIP Revenue Share =
DIVIDE(
    CALCULATE(SUM(final_dashboard_data[revenue]), final_dashboard_data[Segment_Name] = "VIP"),
    SUM(final_dashboard_data[revenue])
)

At Risk Count =
CALCULATE(DISTINCTCOUNT(final_dashboard_data[user_id]), final_dashboard_data[Segment_Name] = "At Risk")

Avg VIP Spend =
CALCULATE(AVERAGE(final_dashboard_data[Monetary]), final_dashboard_data[Segment_Name] = "VIP")

At Risk Avg Recency =
CALCULATE(AVERAGE(final_dashboard_data[Recency]), final_dashboard_data[Segment_Name] = "At Risk")
```

---

## Page 3 — Funnel & Marketing Performance

```dax
Cart Drop-off =
DIVIDE(
    CALCULATE(COUNTROWS(final_dashboard_data),
        final_dashboard_data[added_to_cart] = TRUE,
        final_dashboard_data[purchase_completed] = FALSE),
    CALCULATE(COUNTROWS(final_dashboard_data), final_dashboard_data[added_to_cart] = TRUE)
)

Total Cities = DISTINCTCOUNT(final_dashboard_data[city])

Total Discount Value =
SUMX(final_dashboard_data, final_dashboard_data[order_value] * final_dashboard_data[discount_pct])

Total Marketing Sessions =
CALCULATE(COUNTROWS(final_dashboard_data), final_dashboard_data[campaign_type] <> "No Campaign")

Checkout Completion Rate =
DIVIDE(
    CALCULATE(COUNTROWS(final_dashboard_data), final_dashboard_data[purchase_completed] = TRUE),
    CALCULATE(COUNTROWS(final_dashboard_data), final_dashboard_data[checkout_started] = TRUE)
)

Discount Success Rate =
DIVIDE(
    CALCULATE(COUNTROWS(final_dashboard_data),
        final_dashboard_data[campaign_type] = "Discount",
        final_dashboard_data[purchase_completed] = TRUE),
    CALCULATE(COUNTROWS(final_dashboard_data), final_dashboard_data[campaign_type] = "Discount")
)

Returning Purchase Share =
DIVIDE(
    CALCULATE(COUNTROWS(final_dashboard_data), final_dashboard_data[user_type] = "Returning", final_dashboard_data[purchase_completed] = TRUE),
    CALCULATE(COUNTROWS(final_dashboard_data), final_dashboard_data[purchase_completed] = TRUE)
)

Stage 1 - Visited = COUNTROWS(final_dashboard_data)

Stage 2 - Viewed =
CALCULATE(COUNTROWS(final_dashboard_data), final_dashboard_data[viewed_product] = TRUE)

Stage 3 - Cart =
CALCULATE(COUNTROWS(final_dashboard_data), final_dashboard_data[added_to_cart] = TRUE)

Stage 4 - Checkout =
CALCULATE(COUNTROWS(final_dashboard_data), final_dashboard_data[checkout_started] = TRUE)

Stage 5 - Purchase =
CALCULATE(COUNTROWS(final_dashboard_data), final_dashboard_data[purchase_completed] = TRUE)
```
