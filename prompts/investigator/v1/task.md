# Case to investigate

- **Customer:** {{customer_id}}
- **Signal family:** {{signal_type}}
- **Ledger score:** {{score}} (threshold {{threshold}})
- **As of day:** {{as_of_day}} (days since the corpus epoch; all dates below use the same clock)
- **Conversations on file:** {{conversation_ids}}

This customer crossed the threshold on the accumulation of the signals in the ledger, not on any
single conversation. Read the evidence chain first, then decide what else you need.

Investigate and return the decision JSON for **{{customer_id}}**.
