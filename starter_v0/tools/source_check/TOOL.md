---
name: source_check
track: core
kind: local_knowledge
provider: local_domain_allowlist
requires_env: []
inputs: [url]
outputs: [domain, source_type, organization, citation_guidance]
side_effect: false
---
# source_check

Classifies the hostname of a supplied HTTP(S) URL as an official organization
site, research archive, known news publisher, or unclassified domain. It does
not fetch or validate page content.

Use it when the user explicitly asks about a source's provenance or before
making a high-confidence citation claim about a supplied URL. Use `fetch` to
read a URL, and do not use `source_check` for ordinary summaries.
