# Copy-Paste Prompts for Each Folder Type

Use the appropriate prompt below based on which folder you're processing. Copy the prompt, then paste the JSON content where indicated.

---

## 1. API REFERENCE (`api-reference/` folder)

**Target: 3-4 keyphrases per file**

```
You are a search keyphrase extractor for banking/financial API documentation. Extract keyphrases that developers would type into a search box.

TASK: Extract 3-4 search keyphrases from this API Reference document.

EXTRACT (High Value):
- API name (e.g., "Instant Payments API")
- Key operations (e.g., "create credit transfer", "verify routing number")
- Unique fields (e.g., "uetr", "payment_id")
- API-specific scopes (e.g., "INSTPYMT-Read")
- One "how to" phrase (e.g., "how to send instant payment")

SKIP (Common/Repeated):
- Generic auth: "Bearer token", "OAuth 2.0", "API key"
- Standard headers: "Content-Type", "Authorization", "client-request-id"
- Generic errors: "400 Bad Request", "401 Unauthorized"
- Environment names: "Sandbox", "Validation", "Production"

OUTPUT FORMAT (JSON only, no explanation):
{"document_name": "<filename>", "type": "api_reference", "keyphrases": ["phrase1", "phrase2", "phrase3", "phrase4"]}

DOCUMENT CONTENT:
[PASTE JSON CONTENT HERE]
```

---

## 2. GUIDES (`guides/` folder)

**Target: 5-6 keyphrases per file**

```
You are a search keyphrase extractor for banking/financial API documentation. Extract keyphrases that developers would type into a search box.

TASK: Extract 5-6 search keyphrases from this Guide document.

EXTRACT (High Value):
- Guide/workflow name (e.g., "Open Banking Europe")
- Integration concepts (e.g., "consent authorization", "TPP integration")
- Step names (e.g., "GURN validation", "JWS signature")
- 2-3 "how to" phrases (e.g., "how to authorize consent", "how to set up webhooks")

SKIP (Common/Repeated):
- Generic auth: "Bearer token", "OAuth 2.0", "API key"
- Standard headers: "Content-Type", "Authorization"
- Environment names: "Sandbox", "Validation", "Production"

OUTPUT FORMAT (JSON only, no explanation):
{"document_name": "<filename>", "type": "guide", "keyphrases": ["phrase1", "phrase2", "phrase3", "phrase4", "phrase5", "phrase6"]}

DOCUMENT CONTENT:
[PASTE JSON CONTENT HERE]
```

---

## 3. API OVERVIEW (`api-overview/` folder)

**Target: 1-2 keyphrases per file**

```
You are a search keyphrase extractor for banking/financial API documentation. Extract keyphrases that developers would type into a search box.

TASK: Extract 1-2 search keyphrases from this Product Overview document.

EXTRACT (High Value):
- Product/API name (e.g., "Treasury Management")
- One key capability (e.g., "cash positioning")

SKIP:
- Generic marketing language
- Common banking terms that appear everywhere

OUTPUT FORMAT (JSON only, no explanation):
{"document_name": "<filename>", "type": "product_overview", "keyphrases": ["phrase1", "phrase2"]}

DOCUMENT CONTENT:
[PASTE JSON CONTENT HERE]
```

---

## 4. SOLUTIONS (`solution/` folder)

**Target: 3-4 keyphrases per file**

```
You are a search keyphrase extractor for banking/financial API documentation. Extract keyphrases that developers would type into a search box.

TASK: Extract 3-4 search keyphrases from this Solution document.

EXTRACT (High Value):
- Solution name (e.g., "payment solutions")
- Use case names (e.g., "bulk payments")
- Business scenarios (e.g., "payment processing")
- One "how to" phrase (e.g., "how to process bulk payments")

SKIP:
- Generic marketing language
- Common terms that appear everywhere

OUTPUT FORMAT (JSON only, no explanation):
{"document_name": "<filename>", "type": "solution", "keyphrases": ["phrase1", "phrase2", "phrase3", "phrase4"]}

DOCUMENT CONTENT:
[PASTE JSON CONTENT HERE]
```

---

## 5. COMMON SECTIONS (Run ONCE only)

**Target: ~15 keyphrases total**

```
You are a search keyphrase extractor for banking/financial API documentation. Extract common keyphrases that appear across ALL documentation pages.

TASK: Extract ~15 common search keyphrases that users might search for across all documentation.

EXTRACT:
- Authentication terms: "OAuth 2.0", "Bearer token", "API key", "access token"
- Environment terms: "Sandbox", "Validation", "Production"
- Common headers: "gateway-entity-id", "client-request-id"
- Error handling: "error handling", "HTTP status codes"
- Security: "mutual authentication"
- "How to" basics: "how to generate API key", "how to authenticate", "how to test in sandbox"

OUTPUT FORMAT (JSON only, no explanation):
{"type": "common_sections", "keyphrases": ["phrase1", "phrase2", ...]}
```

---

## AFTER COLLECTING ALL RESULTS

Once you have all the keyphrases from each folder, combine them and remove duplicates. Target final count: ~300 unique keyphrases.

### Expected Totals:
| Folder | Files | Per File | Estimated |
|--------|-------|----------|-----------|
| api-reference | 70 | 3-4 | ~210-280 |
| guides | 10 | 5-6 | ~50-60 |
| solution | 5 | 3-4 | ~15-20 |
| api-overview | 28 | 1-2 | ~28-56 |
| common (once) | 1 | 15 | 15 |
| **TOTAL** | | | **~320-430** |
| **After dedup** | | | **~300** |
