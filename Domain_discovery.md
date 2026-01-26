DOMAIN_DISCOVERY_PROMPT = """You are an expert at analyzing developer documentation and creating search taxonomies.

Analyze this developer portal content and identify the main DOMAINS (feature areas/product categories).

CONTENT INVENTORY:
{content_summary}

A DOMAIN is a major feature area that groups related API functionality. 
Examples from other portals: Authentication, Payments, Accounts, Transfers, Webhooks, Analytics

RULES:
1. Only identify domains that are ACTUALLY present in this content
2. Don't invent domains that aren't represented
3. Each domain should have multiple pages/endpoints
4. Domains should be mutually exclusive (minimal overlap)
5. Use snake_case for names

For each domain provide:
- name: snake_case identifier
- display_name: Human readable name  
- description: What this domain covers (1-2 sentences)
- keywords: 10-15 words/phrases that indicate this domain
- sample_content: 2-3 page titles from the content that belong here

Return JSON:
{{
    "domains": [
        {{
            "name": "authentication",
            "display_name": "Authentication",
            "description": "Covers all authentication and authorization methods including OAuth, API keys, and token management",
            "keywords": ["auth", "authentication", "oauth", "token", "api key", "credential", "login", "bearer", "jwt", "scope", "permission", "authorize"],
            "sample_content": ["OAuth 2.0 Guide", "API Key Management", "Token Refresh"]
        }}
    ],
    "uncategorized_content": ["List of content that doesn't fit any domain"],
    "domain_hierarchy_notes": "Any notes about relationships between domains"
}}"""