from __future__ import annotations

from typing import Any
from urllib.parse import urlparse


OFFICIAL_DOMAINS = {
    "openai.com": "OpenAI",
    "anthropic.com": "Anthropic",
    "ai.google.dev": "Google AI",
    "deepmind.google": "Google DeepMind",
    "groq.com": "Groq",
    "microsoft.com": "Microsoft",
    "meta.com": "Meta",
}

RESEARCH_DOMAINS = {"arxiv.org", "doi.org", "acm.org", "ieee.org"}
NEWS_DOMAINS = {"reuters.com", "apnews.com", "bbc.com", "theverge.com", "techcrunch.com"}


def _matches_domain(host: str, known_domain: str) -> bool:
    return host == known_domain or host.endswith(f".{known_domain}")


def check_source(url: str = "") -> dict[str, Any]:
    """Classify a URL's source type from its hostname; never fetches the URL."""
    raw = (url or "").strip()
    parsed = urlparse(raw)
    host = (parsed.hostname or "").lower().removeprefix("www.")
    if parsed.scheme not in {"http", "https"} or not host:
        return {
            "tool": "source_check",
            "url": raw,
            "error": "invalid_url",
            "message": "Provide an absolute http(s) URL.",
        }

    for known_domain, organization in OFFICIAL_DOMAINS.items():
        if _matches_domain(host, known_domain):
            return {
                "tool": "source_check",
                "url": raw,
                "domain": host,
                "source_type": "official",
                "organization": organization,
                "citation_guidance": "Primary source: cite it for statements made by this organization.",
            }
    for known_domain in RESEARCH_DOMAINS:
        if _matches_domain(host, known_domain):
            return {
                "tool": "source_check",
                "url": raw,
                "domain": host,
                "source_type": "research_archive",
                "organization": None,
                "citation_guidance": "Research source: check the paper authors, date, and version before citing conclusions.",
            }
    for known_domain in NEWS_DOMAINS:
        if _matches_domain(host, known_domain):
            return {
                "tool": "source_check",
                "url": raw,
                "domain": host,
                "source_type": "news_publisher",
                "organization": None,
                "citation_guidance": "News source: cite the article and cross-check material claims with a primary source when possible.",
            }
    return {
        "tool": "source_check",
        "url": raw,
        "domain": host,
        "source_type": "unclassified",
        "organization": None,
        "citation_guidance": "The domain is not in this local allowlist; inspect authorship, date, and corroborating sources before citing it.",
    }
