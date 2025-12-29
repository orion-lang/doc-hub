Based on the Wells Fargo Transaction Detail API v3 documentation, here are synthetic search queries and responses that would target this page:

## Search Queries & Responses

### Query 1: "Wells Fargo transaction search API"
**Response:**
The Wells Fargo Transaction Detail API v3 enables Treasury Management customers to search for transactions from the current day through the previous 180 days. The API provides two main endpoints:
- **Search transactions**: `POST /treasury/transaction-reporting/v3/transactions/search`
- **Generate reports**: `POST /treasury/transaction-reporting/v3/transactions/report`

Key features include pagination support for high-volume transactions, multiple filtering options, and per-transaction billing.

### Query 2: "How to search ACH transactions Wells Fargo API"
**Response:**
To search ACH transactions using Wells Fargo's Transaction Detail API v3:
1. Use the `/transactions/search` endpoint
2. Include `transaction_type: "ACH"` in your request
3. For current-day ACH searches, you can use transaction field names like:
   - `COID` (Company ID)
   - `ENTRYDESC` (Entry Description)
   - `RECNAME` (Recipient Name)
   - `TRACE` (Trace Number)

Example filters: date_range, amount_range, debit_credit_indicator.

### Query 3: "Wells Fargo wire transaction report API documentation"
**Response:**
The Transaction Detail API v3 supports wire transaction reporting through the `/transactions/report` endpoint. For wire transactions:
- Filter by `transaction_type: "WIRE"`
- Available wire-specific fields: WIREREF, WELLSREF, ORG, BNF, SRF, OBI
- Supports both domestic and international wire searches
- Real-time and batch processing options available

### Query 4: "Wells Fargo API pagination cursor implementation"
**Response:**
The Transaction Detail API implements cursor-based pagination:
- Default: 50 transactions per page (max: 100)
- Use `next_cursor` to navigate forward
- Use `previous_cursor` to navigate backward
- Cursors are returned when `total_count > limit`
- Maximum retrievable transactions: 999,999
- For >20 results, make multiple calls using cursors

### Query 5: "Wells Fargo bank reference number search API"
**Response:**
Search by bank reference using the Transaction Detail API v3:
- Field: `bank_reference` in the `bank_reference_list` array
- Currently limited to one bank reference per query
- Only applicable for ATM Credit transactions
- Requires: `transaction_type: "ATM"` and `debit_credit_indicator: "CREDIT"`

### Query 6: "Wells Fargo transaction API date range filter"
**Response:**
The API supports three date/time filtering options:
1. **date_range**: Search by posting date (up to 180 days back)
   - Fields: `start_posting_date`, `end_posting_date`
2. **datetime_range**: Search by transaction timestamp (7 days back)
   - Fields: `start_transaction_datetime`, `end_transaction_datetime`
3. **processed_datetime_range**: Search by process date/time (7 days back)
   - Useful for weekend transactions and batch processing

### Query 7: "Wells Fargo RTP instant payment API search"
**Response:**
Real-Time Payment (RTP) transaction search capabilities:
- Transaction type: `"RTP"`
- BAI codes: 158 (credit), 458 (debit)
- RTP-specific search fields:
  - `E2EREF` (End-to-end reference)
  - `INSTRUCTIONID` (Instruction ID)
  - `SENDER` (Sender identification)
  - `RECEIVER` (Receiver identification)
- Includes UETR tracking for instant payments

### Query 8: "Wells Fargo transaction API authentication headers"
**Response:**
Required authentication headers for Transaction Detail API v3:
- `Authorization`: Bearer {Your API Key} (case-sensitive)
- `Content-Type`: application/json
- `gateway-entity-id`: Your 22-character Entity ID
- `client-request-id`: Unique tracking ID (1-36 chars)
- Optional: `ceo-company-id` for ERP providers
- Mutual authentication certificates required in Production

### Query 9: "Wells Fargo check number range search API"
**Response:**
Search checks using the Transaction Detail API:
- Use `check_number_list` for up to 20 specific check numbers
- Use `check_number_range` with `start_check_number` and `end_check_number`
- Cannot combine with serial number or location number filters
- Returns check details including float information
- Transaction type automatically set to "CHECK"

### Query 10: "Wells Fargo transaction API error codes 1018"
**Response:**
Common Transaction Detail API error codes:
- **1018-008**: Invalid transaction_field_name for the transaction_type
- **1018-010**: Start date earlier than 180 days limit
- **1018-011**: Invalid datetime (must be within 7 days)
- **1018-015**: Start/end dates must be current for certain filters
- **1018-017**: Multiple transaction types not allowed with field filters

### Query 11: "Wells Fargo BAI code transaction filtering"
**Response:**
Filter transactions by BAI (Bank Administration Institute) codes:
- Use `bai_code_list` array in search request
- Examples: 
  - 142: ACH Credit Received
  - 475: Check Paid
  - 195: Incoming Money Transfer
- Each transaction type maps to specific BAI codes
- Useful for reconciliation and categorization

### Query 12: "Wells Fargo transaction API test accounts sandbox"
**Response:**
Sandbox test accounts for Transaction Detail API v3:
- Account numbers: 5834834432, 5834834433, 2378647438432
- Bank ID: 091000019
- Test scenarios include:
  - ACH/Wire/RTP transactions
  - Check number ranges
  - Amount filtering
  - Intraday transactions (accounts 2346587091, 2346587092)
- Use "P - X days" notation for relative dates in testing

These synthetic queries and responses cover the major functionality and common use cases for the Wells Fargo Transaction Detail API v3, helping developers find and understand the API documentation effectively.
