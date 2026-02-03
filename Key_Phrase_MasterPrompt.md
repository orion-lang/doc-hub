transactions

{
  "total_keyphrases": 300,
  "distribution": {
    "common_sections": 0.10,
    "api_reference": 0.40,
    "guides": 0.20,
    "solutions": 0.13,
    "product_overview": 0.17
  },
  "file_counts": {
    "api_reference": 70,
    "guides": 10,
    "solutions": 5,
    "product_overview": 28
  }
}
```

### Dynamic Calculation

| Category | % | For 300 | For 500 | For 200 | Per File |
|----------|---|---------|---------|---------|----------|
| Common Sections | 10% | 30 | 50 | 20 | N/A (one-time) |
| API Reference | 40% | 120 | 200 | 80 | ~1-2 each |
| Guides | 20% | 60 | 100 | 40 | ~6 each |
| Solutions | 13% | 40 | 65 | 26 | ~8 each |
| Product Overview | 17% | 50 | 85 | 34 | ~2 each |

---

## Master Prompt Template (With Variables)
```
You are extracting search keyphrases for a developer documentation site's autocomplete feature.

=== CONFIGURATION ===
Total target keyphrases: {{TOTAL_TARGET}}
This category allocation: {{CATEGORY_TARGET}}
Number of files in category: {{FILE_COUNT}}
Phrases per file: {{PER_FILE_TARGET}}

=== CATEGORY: {{CATEGORY_NAME}} ===

{{CATEGORY_SPECIFIC_INSTRUCTIONS}}

=== RULES (ALL CATEGORIES) ===
- Lowercase only
- 1-4 words per phrase
- No duplicates within this file
- Return exactly {{PER_FILE_TARGET}} phrases (or fewer if content is limited)
- Exclude generic terms: "api", "documentation", "guide", "overview", "page"
- Prioritize terms users would actually type in a search box

=== OUTPUT FORMAT ===
Return ONLY a JSON array of strings. No explanation.

Example: ["create payment", "refund api", "webhook setup"]

=== CONTENT ===
{{FILE_CONTENT}}
```

---

## Category-Specific Instructions (Plug into Master Template)

### Common Sections
```
{{CATEGORY_SPECIFIC_INSTRUCTIONS}}:

Extract from COMMON sections (authentication, error handling, appendix/definitions).

Focus on:
- Authentication methods (e.g., "api key", "oauth", "mutual tls", "client certificate")
- Error codes and troubleshooting (e.g., "401 error", "invalid token", "rate limit")
- Glossary terms from appendix (e.g., "idempotency key", "webhook signature")

This runs ONCE - these terms will be excluded from other extractions.
```

### API Reference
```
{{CATEGORY_SPECIFIC_INSTRUCTIONS}}:

Extract from API reference page. SKIP content about authentication, errors, or appendix.

Focus on:
- API name and endpoint paths (e.g., "create payment", "/v1/charges")
- Core operations (e.g., "capture payment", "void transaction")
- Key parameters unique to this API (e.g., "currency_code", "merchant_id")
- Use cases mentioned (e.g., "split payment", "partial refund")
- Resource/object names (e.g., "payment intent", "subscription object")
```

### Guides
```
{{CATEGORY_SPECIFIC_INSTRUCTIONS}}:

Extract from developer guide/tutorial.

Focus on:
- Task phrases (e.g., "integrate payments", "set up webhooks")
- How-to variations (e.g., "how to test", "testing sandbox")
- Concepts explained (e.g., "3ds authentication", "pci compliance")
- Integration patterns (e.g., "server-side", "mobile sdk")
- Tools/technologies (e.g., "node.js", "postman collection")
```

### Solutions
```
{{CATEGORY_SPECIFIC_INSTRUCTIONS}}:

Extract from solution/use-case page.

Focus on:
- Business use cases (e.g., "subscription billing", "marketplace payments")
- Industry terms (e.g., "saas", "ecommerce checkout")
- Problem statements (e.g., "reduce cart abandonment", "prevent fraud")
- Solution names (e.g., "hosted checkout", "payment links")
```

### Product Overview
```
{{CATEGORY_SPECIFIC_INSTRUCTIONS}}:

Extract from product overview page.

Focus on:
- Product/feature names (e.g., "radar", "billing portal")
- Capability phrases (e.g., "fraud detection", "recurring payments")
- Benefit terms (e.g., "reduce churn", "increase conversion")
```

---

## Final Aggregation Prompt (With Target)
```
You have a raw list of search keyphrases extracted from developer documentation.

=== TARGET ===
Final count: exactly {{TOTAL_TARGET}} keyphrases

=== TASKS ===
1. Remove exact duplicates
2. Merge near-duplicates:
   - "create payment" + "creating payment" → "create payment"
   - "api key" + "api keys" → "api key"
3. Remove overly generic terms (e.g., "api", "request", "response")
4. If count > {{TOTAL_TARGET}}: prioritize by estimated search popularity, remove least useful
5. If count < {{TOTAL_TARGET}}: this is acceptable, do not pad with low-quality terms

=== OUTPUT ===
Return JSON array of strings, sorted by estimated search popularity (most searched first).

=== RAW PHRASES ===
{{ALL_EXTRACTED_PHRASES}}