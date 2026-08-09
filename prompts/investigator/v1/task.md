# Case to investigate

- **Customer:** {{customer_id}}
- **Signal family:** {{signal_type}}
- **Ledger score:** {{score}} (threshold {{threshold}})
- **As of day:** {{as_of_day}} (days since the corpus epoch; all dates below use the same clock)
- **Conversations on file:** {{conversation_ids}}

This customer's ledger score crossed the review threshold. It may have accumulated across several
conversations or been driven mainly by one — the evidence chain will tell you which, and either is a
legitimate reason to be here. Read the evidence chain first, then decide what else you need.

Investigate and return the decision JSON for **{{customer_id}}**.
