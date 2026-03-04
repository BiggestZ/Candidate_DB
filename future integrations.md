# Future Integrations

This document lists high-impact additions to improve the Candidate DB app over time.

## 1. Retrieval and Ranking
- Add a two-stage retrieval pipeline:
  - Stage 1: vector recall (high recall, larger candidate pool).
  - Stage 2: reranking (precision-focused final ordering).
- Add minimum relevance score threshold to filter weak matches.
- Add hybrid retrieval (vector + lexical/BM25 style matching).
- Expand filters in semantic search (skills, location, years experience, seniority).
- Add query rewriting for vague user prompts.
- Add support for faceted result summaries (top skills, top locations, role distribution).

## 2. Intent and Query Understanding
- Add an explicit `unknown` + clarification flow in UI and API responses.
- Improve intent prompt with more ambiguous examples.
- Add entity extraction for role, location, seniority, skills, and years.
- Add confidence calibration and thresholds from real traffic.
- Add support for multi-intent queries (e.g., "find candidates and summarize top trends").

## 3. Candidate Data Quality
- Enrich candidate embeddings with summary, projects, certifications, and resume text.
- Normalize skill names (e.g., "JS" -> "JavaScript", "Postgres" -> "PostgreSQL").
- Add deduplication checks for duplicate candidates by email/profile links.
- Add profile completeness scoring and missing-data flags.
- Add periodic re-indexing jobs to refresh embeddings when schema changes.

## 4. Database and Search Infrastructure
- Add migrations for richer searchable fields (normalized skills table, tags, source metadata).
- Tune pgvector index parameters and monitor recall/latency tradeoffs.
- Add caching for repeated or near-identical search queries.
- Add pagination and stable ordering for large result sets.
- Add safe DB-backed analytics endpoints (counts by role/location/time).

## 5. API and Product Features
- Add saved searches and alert subscriptions.
- Add candidate comparison endpoint (A vs B for a role).
- Add shortlist/favorites support with notes and status.
- Add bulk import endpoint (CSV/LinkedIn exports/resume batches).
- Add conversation memory per session for follow-up queries.
- Add explainability fields in search results (why this candidate matched).

## 6. Evaluation and Monitoring
- Build an evaluation dataset of real recruiting queries + expected outcomes.
- Track retrieval metrics: precision@k, recall@k, MRR, NDCG.
- Track intent metrics: accuracy, unknown rate, confidence calibration.
- Add structured logs for each pipeline stage (intent, retrieval, rerank, response).
- Add dashboards and alerts for latency spikes and failure rates.

## 7. Security, Privacy, and Compliance
- Add authentication and role-based access control.
- Add rate limiting and abuse protections.
- Add audit logs for create/update/delete and search actions.
- Add PII protection policy (masking, retention windows, deletion workflows).
- Add secrets management and environment hardening for production.

## 8. Testing and Reliability
- Add integration tests for `/chat` and `/search` end-to-end behavior.
- Add regression tests for known edge cases and ambiguous inputs.
- Add fixture-based retrieval ranking tests to prevent quality drift.
- Add load tests for search and chat endpoints.
- Add contract tests for frontend-backend schema compatibility.

## 9. Frontend UX Improvements
- Add clearer states for "no results", "uncertain intent", and "partial matches".
- Add query suggestion chips (skills, locations, role templates).
- Add filters sidebar synced with semantic query.
- Add result cards with highlighted matching evidence.
- Add admin page for search quality feedback labeling.

## 10. Delivery and Operations
- Add CI pipeline (tests, lint, type checks, migration checks).
- Add staging environment with production-like data shape.
- Containerize API + frontend for repeatable deploys.
- Add release notes and migration runbooks.
- Add feature flags for incremental rollout of reranking and new intent logic.

## Suggested Implementation Order
1. Retrieval reranking + threshold filtering.
2. Intent/entity extraction improvements.
3. Evaluation dataset and quality dashboards.
4. Data normalization + richer embeddings.
5. Product features (saved searches, shortlists, explainability).
6. Security hardening and production operations.
