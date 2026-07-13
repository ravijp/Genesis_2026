# Dow Jones Knowledge Base

> This document consolidates historical knowledge reconstructed from prior discussions.

## Client Overview
Dow Jones operates multiple subscription products including WSJ, Barron's, MarketWatch and IBD.

## Business Context
The engagement focused on forecasting subscriber acquisition, revenue, circulation and financial planning.

## Major Projects
### FAST Tool
- Purpose: Forecast subscription performance.
- Used business rules to estimate new orders.
- Supported downstream financial planning.
- Included validation and QC workflows.

### New Order Forecasting
- Forecasted subscription starts.
- Considered campaign behaviour, seasonality and historical trends.
- Integrated with FAST outputs.

### Financial Forecast
- Produced management level revenue forecasts.
- Connected operational forecasts to finance.
- Supported planning cycles.

### Curve Library
- Managed renewal, save and stick rate curves.
- Reused by multiple forecasting modules.

### Revenue Forecasting
- Estimated future revenue from subscription behaviour.
- Considered lifecycle transitions.
- Distinguished operational reporting from finance reporting.

### Subscription Lifecycle
- Acquisition
- Introductory period
- Renewal
- Save offers
- Churn

## Important Business Concepts
- Renewal Rate
- Save Rate
- Stick Rate
- Same Day Stop Start
- Marketing Programs
- Delivery Calendar
- Revenue Balance Liability
- GAAP vs Management reporting

## Technology
- Athena
- BigQuery
- Tableau
- SQL
- Python

## Validation
- QC against historical outputs
- Trend comparisons
- Business sanity checks
- Finance reconciliation

## Lessons Learned
- Business context is as important as model accuracy.
- Forecast assumptions should always be documented.
- Validation should exist at every stage.

## Claude Notes
Treat this as generalized documentation rather than implementation details.
