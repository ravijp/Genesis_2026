# Retail — The Agentic Commerce Wave (as of 2026-07-14)

> **Scope note:** This brief covers agentic-commerce protocols (ACP/AP2/UCP) and the retailer threat/opportunity picture. Retailer-internal deployments, merchandising/pricing agents, the Kohl's situation, and the vendor map live in the companion brief, `retail-internal-ops.md`.

## 1. ChatGPT Shopping / Instant Checkout + Agentic Commerce Protocol (ACP)

OpenAI launched Instant Checkout inside ChatGPT on **Sept 29, 2025** (US Etsy sellers; Shopify merchants "coming soon"; Etsy stock +16%) and open-sourced the **Agentic Commerce Protocol (ACP)**, co-developed with Stripe, Apache 2.0, spec maintained on GitHub ([OpenAI](https://openai.com/index/buy-it-in-chatgpt/); [Stripe](https://stripe.com/newsroom/news/stripe-openai-instant-checkout); [CNBC 2025-09-29](https://www.cnbc.com/2025/09/29/chatgpt-instant-checkout-etsy-shopify.html)). Walmart joined Nov 2025 with ~200,000 products. A separate non-transactional **"shopping research"** feature shipped Nov 24-25, 2025 (GPT-5-mini variant; excludes Amazon products) ([OpenAI](https://openai.com/index/chatgpt-shopping-research/); [CNBC](https://www.cnbc.com/2025/11/24/openai-announces-shopping-research-tool-in-latest-e-commerce-push.html)).

**The reversal (March 2026):** OpenAI deprioritized in-chat Instant Checkout, shifting to merchant-built "Apps" (ChatGPT Apps SDK) that hand off to the retailer's own checkout ([Digital Commerce 360, 2026-03-06](https://www.digitalcommerce360.com/2026/03/06/openai-shifts-checkout-plans-agentic-commerce-strategy/); [Forrester](https://www.forrester.com/blogs/what-it-means-that-the-leader-in-agentic-commerce-just-pulled-back/); [CNBC 2026-03-20](https://www.cnbc.com/2026/03/20/open-ai-agentic-shopping-etsy-shopify-walmart-amazon.html)). Merchants needed control over inventory, tax, shipping, subscriptions (Shopify's Harley Finkelstein, same source).

**Why it failed — numbers:** Walmart's in-chat checkout converted at ~**1/3** the rate of walmart.com — **1.18% conversion, 77.45% cart abandonment** vs 2.5-3.0% industry average ([officechai citing Business Insider](https://officechai.com/ai/walmart-found-chatgpts-instant-checkout-unsatisfying-saw-conversion-rates-1-3rd-of-its-own-website-report/); [Search Engine Land](https://searchengineland.com/walmart-chatgpt-checkout-converted-worse-472071)). Top 5 categories (vitamins, auto parts, beauty, hardware, tools) = >50% of orders. Only **~30 Shopify merchants** were actually live by Feb 2026 despite "1M merchants" framing — flag the eligible-vs-active discrepancy. Walmart's replacement "Sparky" agent inside ChatGPT (Apps model, own checkout) converts at ~**70%** of walmart.com's rate.

**ACP status July 2026:** remains the discovery/handoff layer; Target, Sephora, Nordstrom, Lowe's, Best Buy, Home Depot, Wayfair integrated for discovery; Target shipped a dedicated ChatGPT app for holiday 2025; PayPal built an ACP server to onboard SMBs through 2026.

## 2. Perplexity Shopping

- "Buy with Pro" launched Nov 18, 2024 [background] + free Merchant Program ([Perplexity](https://www.perplexity.ai/hub/blog/shop-like-a-pro)).
- **"Instant Buy"** via PayPal-powered in-chat checkout, **5,000+ merchants** (Abercrombie, Fabletics, Ashley Furniture), live Nov 25, 2025 ([CNBC 2025-11-19](https://www.cnbc.com/2025/11/19/perplexity-ai-online-shopping-paypal.html)). Expanded to all US users Feb 2026; all Shopify merchants Jan 2026.
- July-2026 read: Perplexity runs the deepest actual in-chat checkout because it borrowed PayPal's merchant rails instead of rebuilding commerce. ~45M MAU, affluent-skewed base.
- Distinct from its **Comet** browser fight with Amazon (below) — two separate commerce plays.

## 3. Amazon Rufus + Buy For Me → Alexa for Shopping

- Rufus [background: Feb 2024]: 250M customers, monthly users +140% YoY, users 60% likelier to purchase, ~$10B+ incremental annualized sales ([Modern Retail, Nov 2025](https://www.modernretail.co/technology/marketplace-briefing-amazons-shopping-bot-rufus-can-now-automatically-buy-products-for-you-when-prices-drop/)).
- "Buy For Me" (Feb 2025): agentic purchase from third-party retailer sites inside the Amazon app — retailer backlash: "never opted in."
- **Auto-Buy** (Nov 13, 2025): Rufus monitors prices every 30 min, auto-purchases at user-set threshold, 24h cancellation window.
- **Amazon hardens against external agents while pushing its own:** robots.txt blocks ~47-50 AI crawlers incl. all three OpenAI crawlers; Amazon subsidiaries (Zappos, Shopbop, Woot) NOT similarly blocked. Logic: ~$56B/yr ad business depends on on-site browsing.
- **Amazon v. Perplexity:** suit filed Nov 4, 2025 (Comet disguised as Chrome, CFAA/CDAFA claims); **preliminary injunction granted March 10, 2026** blocking Comet purchases on Amazon ([CNBC](https://www.cnbc.com/2026/03/10/amazon-wins-court-order-to-block-perplexitys-ai-shopping-agent.html)) — the bellwether case for agent-vs-platform access rights.
- **May 13, 2026: Rufus merged into "Alexa for Shopping"** — unified assistant across app/web/Echo, cross-device memory, auto-buy and scheduled restocking carried forward ([CNBC](https://www.cnbc.com/2026/05/13/amazon-ditches-rufus-ai-chatbot-in-favor-of-alexa-shopping-agent.html); [GeekWire](https://www.geekwire.com/2026/amazon-unifies-alexa-and-rufus-as-ai-rivals-move-into-online-shopping/)).

## 4. Google AI Mode Shopping + AP2 + UCP

- **AP2 (Agent Payments Protocol)**, Sept 16-17, 2025 [foundational]: 60+ partners (Mastercard, PayPal, Coinbase, Amex, Salesforce); "Mandates" = cryptographically signed Intent → Cart → Payment chain; human-present and human-not-present flows ([Google Cloud](https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol)).
- **AP2 v0.2.0** (April 2026): human-not-present autonomous pre-authorized purchases. **April 2026: Google donated AP2 to the FIDO Alliance** for neutral governance ([FIDO](https://fidoalliance.org/google-donates-agent-payments-protocol-to-fido-alliance/)).
- **UCP (Universal Commerce Protocol)**, announced NRF Jan 11-12, 2026: umbrella discovery/checkout layer compatible with A2A/AP2/MCP; co-developed with Shopify, Etsy, Wayfair, Target, Walmart; endorsed by Adyen, Amex, Best Buy, Macy's, Mastercard, Stripe, Home Depot, Visa, Zalando ([TechCrunch](https://techcrunch.com/2026/01/11/google-announces-a-new-protocol-to-facilitate-commerce-using-ai-agents/); [Google](https://blog.google/products/ads-commerce/agentic-commerce-ai-tools-protocol-retailers-platforms/)).
- Agentic checkout live in Search/AI Mode/Gemini via Google Pay (Wayfair, Chewy, Quince, select Shopify); **"Universal Cart"** (I/O 2026) = persistent cross-surface cart; **"Business Agent"** = brand's own agent inside Search. Expanding US → Canada/Australia → UK.
- **Key divergence: OpenAI retreated from in-chat checkout (Mar 2026) while Google is expanding it** — the most important strategic read for where retailers should invest integration effort.

## 5. Visa Intelligent Commerce / Mastercard Agent Pay

**Visa:** 100+ partners, 30+ in sandbox, 20+ agents integrating (Dec 2025, [Visa IR](https://investor.visa.com/news/news-details/2025/Visa-and-Partners-Complete-Secure-AI-Transactions-Setting-the-Stage-for-Mainstream-Adoption-in-2026/default.aspx)); prediction: millions of consumers using agent purchases by holiday 2026. **Intelligent Commerce Connect** = single merchant integration point supporting FOUR protocols (Trusted Agent Protocol, Machine Payments Protocol, ACP, UCP) — pilot with Aldar, AWS, Diddo, Highnote, Mesh, Payabli, Sumvin ([Visa](https://usa.visa.com/about-visa/newsroom/press-releases.releaseId.21961.html)). Trusted Agent Protocol (Oct 2025) separates legit agents from malicious bots; Akamai joined. July 2, 2026 Paris Payments Forum: 30 European issuers enabling agent transactions; merchants lastminute.com, Frasers, BrickDepot, Cleverbridge ([FinTech Magazine](https://fintechmagazine.com/news/visa-payments-forum-in-paris-agentic-commerce-is-coming)).

**Mastercard Agent Pay** (unveiled Apr 29, 2025): "Agentic Tokens" extending MDES — tokenized credential bound to specific agent + merchant scope + consent policy. Piloted with Citi and US Bank Sept 2025; all US cardholders Nov 2025; LatAm/Caribbean Dec 2025; **"Agent Pay for Machines"** (June 2026) for M2M payments ([Mastercard](https://www.mastercard.com/us/en/news-and-trends/press/2026/june/mastercard-launches-agent-pay-for-machines.html)). Both networks hedge across ALL protocols.

## 6. What a mid-size retailer must do to be "agent-ready"

- **12 core product attributes** baseline (title, description, brand, GTIN, MPN, category, price, sale price, availability, condition, image URL, product URL) + 20-30 enrichment attributes for detail-sensitive categories.
- Schema.org/JSON-LD: `Product`, `Offer`, `AggregateRating`, `MerchantReturnPolicy`, `ShippingRateSettings`.
- **Three-layer stack:** (1) JSON-LD on PDPs, (2) Merchant Center feeds, (3) **an MCP server / agent-facing API for live inventory+pricing** — the layer UCP/ACP/AP2 all build on.
- AEO/GEO: extractable policy pages, review-program authority signals, question-shaped content, granular attribute schema ("LLMs use structured data as a primary source of truth").
- **Digital Commerce 360 × ReFiBuy quarterly "agentic readiness" benchmark** of Top 1000 retailers launched 2026; early leaders (Online Labels, Nixon, Fashionphile, Everlane, Brooklinen) are mid-size — readiness correlates with clean SKU data, not size ([Newswire](https://www.newswire.com/news/digital-commerce-360-and-refibuy-launch-first-of-its-kind-ai-commerce-rankings)).

## 7. Traffic & margin threat numbers

| Metric | Figure | Source/date |
|---|---|---|
| AI-referred traffic growth, holiday 2025 | +670% to +758% YoY (range across windows; Adobe/DC360/Retail Dive) | Jan 2026 |
| Holiday 2025 online spend | $257.8B record (Adobe) | Jan 2026 |
| Share of holiday retail sales AI-influenced | 20% / $262B (Salesforce) | 2026 |
| Q1 2026 AI-referral growth | +393% YoY (Adobe via CX Network) | 2026 |
| Agentic-browser traffic growth | +7,851% YoY (Similarweb) | 2026 |
| AI-referral conversion vs social | 8-9x (Salesforce) | 2025-26 |
| AI referrals convert vs other traffic | +31% (reversal from -23% in July 2025) — key inflection | Adobe |
| Revenue/visit from AI referrals | +254% YoY (holidays) | Adobe |
| Retailers running own shopper agents | sales growing 59% faster than sideline retailers | Jul 2026 |
| OpenAI take rate on completed checkout | **4% transaction fee** (vs ~2.9%+30¢ standard processing) | Jan 2026 |

**Margin/power analysis:** Wharton's Hosanagar: "Whoever controls the agents now has the power." Aptos's Nikki Baird: "The retailer loses so much context because it's outside of their realm." **81% of retail execs** (Deloitte) expect GenAI to weaken brand loyalty by 2027; ~50% expect collapse of multi-step shopping journeys into single AI interactions by 2027 ([Retail Dive](https://www.retaildive.com/news/retails-ai-bet-risks-data-market-share/810202/)). Mechanism: agents optimize on price/spec → hurts storytelling brands, threatens to disintermediate multibrand retailers. Market forecasts (directional only): agentic commerce ~$5-7B (2025) → $15B+ (2026); McKinsey $3-5T annually by 2030.

**Caveats to carry forward:** eligible-vs-active merchant counts conflate; holiday traffic growth is a range not a number; "25% of transactions AI-mediated by 2026" and "Baymard 30% CTR" claims are untraceable to primary sources — exclude or caveat.

## Implications for Genesis Track A (initial, from this sub-brief)

1. The retailer-side pain is **agent-readiness**: structured data, MCP endpoints, and policy surfaces — a concrete, buildable consulting product ("make client X agent-ready, measurably").
2. **Agentic-commerce fraud/abuse and agent-vs-bot discrimination** (Visa Trusted Agent Protocol territory) crosses retail into Visa/AmEx/Capital One — a strong Zenon crossover seed.
3. The Amazon v. Perplexity injunction + protocol fragmentation (ACP/AP2/UCP/TAP) = enterprises need a **protocol-abstraction / governance layer** — white space matching a consulting build.
4. Loyalty (ampliFI) is directly threatened by agent-mediated purchasing disintermediating offers — "loyalty in the agentic era" is an underexplored, client-fundable theme.
