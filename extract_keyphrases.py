"""
Keyphrase Extraction Script for API Documentation
--------------------------------------------------
This script processes JSON documentation files and extracts search keyphrases
using an LLM API (Claude/OpenAI compatible).

Usage:
    python extract_keyphrases.py

The script will process all JSON files in the configured INPUT_DIR and its subfolders.
"""

import json
import os
import re
from pathlib import Path
from collections import Counter
from typing import List, Dict, Any

# ============================================================================
# CONFIGURATION - EDIT THESE PATHS
# ============================================================================

# Input directory containing JSON files (with subfolders)
# Example structure:
#   keywords/
#   ├── api-reference/
#   │   ├── instant_payment.json
#   │   ├── ACH_Payments.json
#   │   └── ...
#   ├── guides/
#   │   ├── webhooks.json
#   │   └── ...
#   ├── solution/
#   │   └── ...
#   └── api-overview/
#       └── ...

INPUT_DIR = "./keywords"  # Root folder containing all JSON files

# Output file path (will be created in the INPUT_DIR)
OUTPUT_FILE = "./keywords/extracted_keyphrases.json"

# Target number of unique keyphrases after deduplication
TARGET_KEYPHRASE_COUNT = 300

# ============================================================================
# EXTRACTION QUOTAS BY PAGE TYPE
# ============================================================================

QUOTAS = {
    "api_reference": {"target_per_page": 4, "description": "API name, key operations, unique fields, scopes"},
    "guide": {"target_per_page": 6, "description": "Workflow names, integration concepts, step names"},
    "solution": {"target_per_page": 4, "description": "Use case names, business scenarios"},
    "product_overview": {"target_per_page": 2, "description": "Product name, key capability only"},
}

# ============================================================================
# SYSTEM PROMPT FOR LLM
# ============================================================================

SYSTEM_PROMPT = """You are a search keyphrase extractor for banking/financial API documentation. Extract keyphrases that developers and integration teams would type into a search box when looking for specific functionality.

## DOCUMENT TYPES
- **API Reference**: Structured with introSection, basicsSection, useCaseSections, errorHandlingSection
- **Guide**: Contains contentSection1, contentSection2, etc. with sectionHeader and bodyText
- **Product Overview**: Introductory content about products/services

## OUTPUT FORMAT
Return ONLY a JSON object (no markdown, no explanation):
{"document_name": "<filename>", "type": "<api_reference|guide|product_overview>", "keyphrases": ["phrase1", "phrase2", ...]}

## EXTRACTION PRIORITIES

### EXTRACT (High Value):
1. API/Product Names: "Instant Payments API", "ACH Payments", "Account Balance"
2. Operations: "create credit transfer", "verify routing number", "retrieve balance"
3. Endpoint paths: "credit-transfers", "routing-numbers/verify"
4. API-specific fields: "uetr", "payment_id", "end_to_end_id"
5. Business concepts: "real-time payments", "RTP", "FedNow", "same-day ACH"
6. Status values: "PROCESSED", "ACCEPTED", "PENDING", "REJECTED"
7. SEC codes (for ACH): "CCD", "PPD", "CTX", "IAT", "WEB", "TEL"
8. Scopes: "INSTPYMT-Read", "ACH-All", "Account-Balance"
9. Integration terms: "webhook listener", "consent authorization"
10. Network/Rail types: "payment_rail", "clearing network"
11. "How to" phrases: Generate task-oriented search phrases based on use cases:
    - "how to initiate ACH payment"
    - "how to verify routing number"
    - "how to set up webhooks"
    - "how to handle payment errors"
    - "how to authorize consent"
    - "how to refresh access token"

### SKIP (Common/Repeated):
- Generic auth: "Bearer token", "OAuth 2.0", "API key" (unless API-specific scope)
- Standard headers: "Content-Type", "Authorization", "client-request-id"
- Generic certificates: "mutual authentication certificates"
- Standard HTTP errors: "400 Bad Request", "401 Unauthorized"
- Generic testing: "Sandbox", "Validation", "Production"
- Postman/Swagger file references

## FORMATTING RULES
1. Lowercase except acronyms (RTP, ACH, FedNow) and proper nouns
2. Keep phrases 1-4 words (max 5 for complex concepts)
3. Preserve technical casing for field names: "payment_id" not "Payment Id"

## EXTRACTION QUOTAS (soft limits - quality over quantity)
- API Reference: 3-4 keyphrases per page
- Guide: 5-6 keyphrases per page
- Solution: 3-4 keyphrases per page
- Product Overview: 1-2 keyphrases per page

If a page has fewer unique valuable terms, return fewer - never pad with generic terms."""


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def detect_document_type(content: Dict[str, Any], filepath: str) -> str:
    """Detect the type of documentation based on JSON structure and filepath."""
    filepath_lower = filepath.lower()

    # Check filepath for hints (updated folder names)
    if "api-reference" in filepath_lower or "api reference" in filepath_lower or "apireference" in filepath_lower:
        return "api_reference"
    elif "guides" in filepath_lower or "guide" in filepath_lower:
        return "guide"
    elif "solution" in filepath_lower:
        return "solution"
    elif "api-overview" in filepath_lower or "product-overview" in filepath_lower or "productoverview" in filepath_lower:
        return "product_overview"

    # Check JSON structure
    if "APIReference" in content:
        return "api_reference"
    elif "gatewayGuides" in content:
        return "guide"
    else:
        return "product_overview"


def strip_html_tags(text: str) -> str:
    """Remove HTML tags from text content."""
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', ' ', text)
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()


def extract_text_content(data: Any, max_depth: int = 10) -> str:
    """Recursively extract all text content from nested JSON."""
    if max_depth <= 0:
        return ""

    texts = []

    if isinstance(data, dict):
        # Priority keys to extract
        priority_keys = [
            'header', 'pageTitleSuffix', 'introductionHeader', 'introductionBodyText',
            'useCaseHeader', 'useCaseBodyText', 'useCaseEndpoint', 'useCaseMethod',
            'sectionHeader', 'bodyText', 'subSectionHeader',
            'parameter', 'bodyText', 'details'
        ]

        for key in priority_keys:
            if key in data:
                if isinstance(data[key], str):
                    texts.append(strip_html_tags(data[key]))
                elif isinstance(data[key], (dict, list)):
                    texts.append(extract_text_content(data[key], max_depth - 1))

        # Also check other keys
        for key, value in data.items():
            if key not in priority_keys:
                if isinstance(value, (dict, list)):
                    texts.append(extract_text_content(value, max_depth - 1))

    elif isinstance(data, list):
        for item in data:
            texts.append(extract_text_content(item, max_depth - 1))

    return " ".join(filter(None, texts))


def prepare_document_summary(filepath: str, content: Dict[str, Any], max_chars: int = 15000) -> str:
    """Prepare a summarized version of the document for the LLM."""
    doc_type = detect_document_type(content, filepath)
    filename = os.path.basename(filepath)

    # Extract key sections based on document type
    summary_parts = [f"Document: {filename}", f"Type: {doc_type}", ""]

    if doc_type == "api_reference" and "APIReference" in content:
        api_ref = content["APIReference"]

        # Header and intro
        if "header" in api_ref:
            summary_parts.append(f"API Name: {api_ref['header']}")

        if "introSection" in api_ref:
            intro = api_ref["introSection"]
            if "introductionBodyText" in intro:
                summary_parts.append(f"Introduction: {strip_html_tags(intro['introductionBodyText'])[:500]}")
            if "codeSnippetsIntroduction" in intro and "code" in intro["codeSnippetsIntroduction"]:
                summary_parts.append(f"Endpoints: {strip_html_tags(intro['codeSnippetsIntroduction']['code'])}")

        # Scopes (API-specific)
        if "basicsSection" in api_ref and "basicsSubsections" in api_ref["basicsSection"]:
            for subsection in api_ref["basicsSection"]["basicsSubsections"]:
                header = subsection.get("basicsSubsectionHeader", "")
                if "Scope" in header:
                    summary_parts.append(f"Scopes: {strip_html_tags(subsection.get('basicsSubsectionBodyText', ''))}")

        # Use cases
        if "useCaseSections" in api_ref:
            summary_parts.append("\nUse Cases:")
            for key, uc in api_ref["useCaseSections"].items():
                if isinstance(uc, dict):
                    uc_header = uc.get("useCaseHeader", "")
                    uc_method = uc.get("useCaseMethod", "")
                    uc_endpoint = uc.get("useCaseEndpoint", "")
                    uc_body = strip_html_tags(uc.get("useCaseBodyText", ""))[:200]
                    summary_parts.append(f"- {uc_method} {uc_header}: {uc_endpoint}")
                    if uc_body:
                        summary_parts.append(f"  {uc_body}")

                    # Extract key field names
                    fields = []
                    if "useCaseRequestFields" in uc:
                        for rf in uc["useCaseRequestFields"]:
                            if "basicsSubsectionTable" in rf and "row" in rf["basicsSubsectionTable"]:
                                for row in rf["basicsSubsectionTable"]["row"]:
                                    if "parameter" in row:
                                        fields.append(row["parameter"])
                    if fields:
                        summary_parts.append(f"  Fields: {', '.join(fields[:15])}")

    elif doc_type == "guide" and "gatewayGuides" in content:
        guide = content["gatewayGuides"]

        if "headerSection" in guide:
            summary_parts.append(f"Guide: {guide['headerSection'].get('header', '')}")
            if "introText" in guide["headerSection"]:
                summary_parts.append(f"Intro: {strip_html_tags(guide['headerSection']['introText'])[:500]}")

        # Content sections
        for key in sorted(guide.keys()):
            if key.startswith("contentSection"):
                section = guide[key]
                if "sectionHeader" in section:
                    summary_parts.append(f"\nSection: {section['sectionHeader']}")
                if "contentBody" in section:
                    for item in section["contentBody"][:3]:  # Limit items
                        if isinstance(item, dict):
                            if "subSectionHeader" in item:
                                summary_parts.append(f"- {item['subSectionHeader']}")
                            if "bodyText" in item:
                                summary_parts.append(f"  {strip_html_tags(item['bodyText'])[:200]}")

    # Join and truncate
    full_summary = "\n".join(summary_parts)
    if len(full_summary) > max_chars:
        full_summary = full_summary[:max_chars] + "...[truncated]"

    return full_summary


def call_llm(prompt: str, system_prompt: str = SYSTEM_PROMPT) -> Dict[str, Any]:
    """
    Call the LLM API.

    REPLACE THIS FUNCTION with your actual LLM API call.
    This is a placeholder that shows the expected interface.
    """
    # =========================================================================
    # REPLACE THIS WITH YOUR ACTUAL LLM API CALL
    # =========================================================================
    # Example for Anthropic Claude API:
    #
    # import anthropic
    # client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    # response = client.messages.create(
    #     model="claude-sonnet-4-20250514",
    #     max_tokens=1024,
    #     system=system_prompt,
    #     messages=[{"role": "user", "content": prompt}]
    # )
    # return json.loads(response.content[0].text)
    #
    # Example for OpenAI:
    #
    # import openai
    # response = openai.ChatCompletion.create(
    #     model="gpt-4",
    #     messages=[
    #         {"role": "system", "content": system_prompt},
    #         {"role": "user", "content": prompt}
    #     ]
    # )
    # return json.loads(response.choices[0].message.content)
    # =========================================================================

    raise NotImplementedError(
        "Please implement the call_llm() function with your LLM API.\n"
        "See the function comments for examples."
    )


def process_file(filepath: str) -> Dict[str, Any]:
    """Process a single JSON file and extract keyphrases."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = json.load(f)

    # Prepare document summary
    summary = prepare_document_summary(filepath, content)
    doc_type = detect_document_type(content, filepath)

    # Create prompt with quota hint
    quota = QUOTAS.get(doc_type, QUOTAS["product_overview"])
    prompt = f"""Extract search keyphrases from this API documentation.

Target: ~{quota['target_per_page']} keyphrases (focus on: {quota['description']})

{summary}"""

    # Call LLM
    result = call_llm(prompt)

    return result


def deduplicate_keyphrases(all_phrases: List[str], target_count: int = 300) -> List[str]:
    """Deduplicate and rank keyphrases."""
    # Count occurrences
    phrase_counts = Counter(all_phrases)

    # Normalize and group similar phrases
    normalized = {}
    for phrase, count in phrase_counts.items():
        # Normalize for comparison
        norm_key = phrase.lower().strip()

        # Handle singular/plural
        if norm_key.endswith('s') and norm_key[:-1] in normalized:
            # Keep plural, add count
            normalized[norm_key] = normalized.get(norm_key, 0) + count + normalized.pop(norm_key[:-1])
        elif norm_key + 's' in normalized:
            # Plural exists, add to it
            normalized[norm_key + 's'] += count
        else:
            normalized[norm_key] = normalized.get(norm_key, 0) + count

    # Sort by frequency and return top N
    sorted_phrases = sorted(normalized.items(), key=lambda x: (-x[1], x[0]))

    # Return the original casing from first occurrence
    result = []
    seen_normalized = set()

    for phrase, _ in sorted_phrases:
        if phrase not in seen_normalized:
            # Find original casing
            for orig in all_phrases:
                if orig.lower().strip() == phrase:
                    result.append(orig)
                    seen_normalized.add(phrase)
                    break
            else:
                result.append(phrase)
                seen_normalized.add(phrase)

        if len(result) >= target_count:
            break

    return result


def main():
    """Main function - processes all JSON files in INPUT_DIR and subfolders."""

    print("=" * 60)
    print("Keyphrase Extraction Script")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Input directory:  {INPUT_DIR}")
    print(f"  Output file:      {OUTPUT_FILE}")
    print(f"  Target count:     {TARGET_KEYPHRASE_COUNT}")
    print()

    # Find all JSON files in INPUT_DIR and subfolders
    input_path = Path(INPUT_DIR)

    if not input_path.exists():
        print(f"ERROR: Input directory does not exist: {INPUT_DIR}")
        print("Please update the INPUT_DIR variable in the script.")
        return

    json_files = list(input_path.rglob('*.json'))

    # Exclude output file if it exists in the input directory
    output_path = Path(OUTPUT_FILE)
    json_files = [f for f in json_files if f.resolve() != output_path.resolve()]

    print(f"Found {len(json_files)} JSON files in {INPUT_DIR}:")

    # Group by folder
    files_by_folder = {}
    for f in json_files:
        folder = f.parent.name if f.parent != input_path else "(root)"
        files_by_folder.setdefault(folder, []).append(f)

    for folder, files in sorted(files_by_folder.items()):
        print(f"  {folder}/: {len(files)} files")

    print()

    # Process each file
    all_keyphrases = []
    results_by_file = {}
    stats_by_type = {"api_reference": 0, "guide": 0, "solution": 0, "product_overview": 0}

    for i, filepath in enumerate(json_files):
        relative_path = filepath.relative_to(input_path)
        print(f"Processing [{i+1}/{len(json_files)}]: {relative_path}")

        try:
            result = process_file(str(filepath))
            keyphrases = result.get('keyphrases', [])
            doc_type = result.get('type', 'unknown')

            all_keyphrases.extend(keyphrases)
            results_by_file[str(relative_path)] = {
                "type": doc_type,
                "keyphrases": keyphrases
            }
            stats_by_type[doc_type] = stats_by_type.get(doc_type, 0) + len(keyphrases)

            print(f"  -> {len(keyphrases)} keyphrases ({doc_type})")
        except Exception as e:
            print(f"  ERROR: {e}")
            results_by_file[str(relative_path)] = {"error": str(e)}

    # Deduplicate
    print(f"\n{'=' * 60}")
    print(f"Deduplicating {len(all_keyphrases)} total phrases...")
    final_keyphrases = deduplicate_keyphrases(all_keyphrases, TARGET_KEYPHRASE_COUNT)
    print(f"Final count: {len(final_keyphrases)} unique keyphrases")

    # Save results
    output_data = {
        "configuration": {
            "input_dir": INPUT_DIR,
            "target_count": TARGET_KEYPHRASE_COUNT
        },
        "stats": {
            "total_files_processed": len(json_files),
            "total_keyphrases_extracted": len(all_keyphrases),
            "final_unique_keyphrases": len(final_keyphrases),
            "by_type": stats_by_type
        },
        "keyphrases": final_keyphrases,
        "by_file": results_by_file
    }

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)

    print(f"\nResults saved to: {OUTPUT_FILE}")

    # Print summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"Files processed:     {len(json_files)}")
    print(f"Total extracted:     {len(all_keyphrases)}")
    print(f"After deduplication: {len(final_keyphrases)}")
    print(f"\nBy document type:")
    for doc_type, count in stats_by_type.items():
        print(f"  {doc_type}: {count} keyphrases")

    # Print sample
    print(f"\nSample keyphrases (first 20):")
    for phrase in final_keyphrases[:20]:
        print(f"  - {phrase}")


if __name__ == "__main__":
    main()
