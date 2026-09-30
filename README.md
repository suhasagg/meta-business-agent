# Meta Business Agent–Inspired Enterprise Platform

>
## 1. Product problem

A business messaging agent must turn a conversation into a safe, personalized business workflow:

```text
WhatsApp / Messenger / Instagram / Web
                  |
             Channel Ingress
                  |
        Identity + Tenant Resolver
                  |
             Conversation
                  |
          LangGraph Orchestrator
                  |
 +----------------+-----------------------------+
 |                |              |              |
Customer 360   Knowledge      Commerce       Support
 |                |              |              |
CRM              RAG        Catalog/Order    Ticketing
 |                |              |              |
 +--------+-------+------+-------+--------------+
          |              |
      Lead/Booking    Recommendation
          |              |
          +-------+------+
                  |
          Compliance/Critic
                  |
             Human Handoff
                  |
          Response / Messaging
```

Public Meta capabilities motivating the design include business-specific Q&A, catalog recommendations, appointment
booking, lead qualification, human takeover and sales. The enterprise platform adds connected systems, guardrails,
measurement and multiple messaging surfaces.

## 2. Principal architecture

```text
                         CHANNEL PLANE
 WhatsApp --------+
 Messenger -------+----> Webhook/Event Ingress
 Instagram -------+              |
 Web/Voice -------+       signature validation
                                  |
                           conversation event
                                  |
                    +-------------v--------------+
                    |      CONTROL PLANE         |
                    | API / AuthN / AuthZ        |
                    | LangGraph / Checkpoints    |
                    | Planner / Task DAG         |
                    | Policy / Approval          |
                    | Memory / Context Builder   |
                    +-------------+--------------+
                                  |
                    +-------------v--------------+
                    |       AGENT PLANE          |
                    | Customer360 / Knowledge    |
                    | Catalog / Recommendation   |
                    | Lead / Appointment / Sales |
                    | Order / Support / Case     |
                    | Handoff / Compliance       |
                    | Critic / Verifier/Response |
                    +-------------+--------------+
                                  |
                         Capability Gateway
                                  |
             +--------------------+--------------------+
             |                    |                    |
          CRM/Calendar         Commerce             Support
             |                    |                    |
          customer            Shopify-like         Zendesk-like
          lead/book           catalog/order         cases
             +--------------------+--------------------+
                                  |
                         EVENT / DATA PLANE
                Postgres / Redis / Kafka / Object Store
                                  |
                    Audit / Metrics / Traces / Evals
```

## 3. Why LangGraph

Customer conversations are stateful workflows, not one LLM call. A request can read customer context, retrieve
knowledge, inspect products, request approval for a write, pause, resume, open a case and transfer to a human. LangGraph
provides explicit state, conditional routing, checkpointing and interrupt/resume.

## 4. State model

`core/models.py` separates workflow facts from prose: tenant/customer/thread/channel, plan, active step, customer,
evidence, cart, lead, appointment, order, case, handoff, iteration limits, verification and final answer.

Keep credentials and huge documents out of graph state. Store immutable artifact references instead.

## 5. Task DAG

`agents/orchestrator.py` creates dependency-aware steps. Production planners should validate acyclicity, agent allowlists,
maximum depth, token/tool/time/cost budgets and action risk before accepting a generated plan.

## 6. Customer360 Agent

Reads CRM/customer profile through `crm.customer`. Useful context includes identity, account tier, consent, recent
orders, service cases and allowed personalization fields. The agent is read-only; CRM is the source of truth.

## 7. Knowledge Agent

`rag/store.py` demonstrates tenant-filtered retrieval. Production RAG should use:
- ingestion from approved business documents;
- chunking and versioning;
- embeddings + lexical BM25;
- reciprocal-rank fusion/reranking;
- ACL filtering **before** ranking;
- freshness/expiry;
- provenance and citation IDs;
- deletion propagation.

Never answer a policy/shipping/refund question from model memory when business knowledge is authoritative.

## 8. Catalog Agent

Uses a commerce connector to retrieve real catalog data. Product title, variant, price, inventory and eligibility should
remain provider facts.

## 9. Recommendation Agent

Ranks grounded catalog candidates against explicit customer need and allowed preference memory. It must not invent
inventory, price, discount or product capability.

A production ranker can combine:
`eligibility × semantic relevance × inventory × business rule × diversity`, with transparent policy constraints.

## 10. Lead Agent

Creates a CRM lead using an idempotency key tied to the conversation. Qualification fields should be schema-driven:
need, product/service, location, timeline, consent, budget when appropriate, and next action.

Lead creation is a write and passes the Gateway.

## 11. Appointment Agent

Captures appointment intent and writes through a scheduling/CRM provider. A mature adapter first reads availability,
then asks the customer to select/confirm, then performs an idempotent booking. Never fabricate slots.

## 12. Sales Agent

Sales coordinates discovery, catalog evidence, lead/appointment/order intent and response. It does not bypass policy and
does not directly capture payment.

## 13. Order Agent

Reads authoritative order state from commerce. Ownership verification must occur before exposing sensitive order data.

## 14. Support Agent

Combines customer, knowledge and order context. It decides whether the request can be resolved with evidence or requires
case creation/handoff.

## 15. Case Agent

Creates a support ticket idempotently. Include compact conversation summary, customer reference, issue category,
priority, evidence and previous attempted resolution.

## 16. Human Handoff Agent

Handoff is a state transition, not "tell the user to call support."

```text
AI_OWNED -> HANDOFF_REQUESTED -> HUMAN_OWNED -> HUMAN_RESOLVED
                                     |
                                  AI_ASSIST
```

Transfer a bounded context packet and stop autonomous customer-facing writes while human-owned.

## 17. Compliance Agent

`security/guard.py` provides a small deterministic prompt-injection/PII boundary. Production adds policy classifiers,
DLP, regulated-topic rules, consent and market-specific restrictions.

## 18. Critic Agent

Critic challenges missing evidence, unsupported claims and failed prior steps. It should remain independent of the agent
that generated a recommendation/action.

## 19. Verifier Agent

Verifier decides whether the workflow actually completed. It checks plan completion, required evidence, policy state,
write receipts and unresolved failures. A model statement is not proof of an external mutation.

## 20. Response Agent

Response converts verified structured results into channel-appropriate text, performs redaction, preserves locale/tone
constraints and never upgrades an uncertain backend result into certainty.

# Seven memory layers

## 21. Memory overview

```text
Memory Manager
 |
 +-- Working       current thread state/context
 +-- Episodic      verified previous interactions/outcomes
 +-- Semantic      customer/product/business facts with provenance
 +-- Procedural    skills/runbooks
 +-- Preference    explicit customer/business preferences
 +-- Artifact      receipts, summaries, evidence references
 +-- Organization  policy/brand/compliance guidance
```

## 22. Working memory
Short-lived thread context: unresolved intent, selected product, appointment candidate, current case. TTL after
conversation completion.

## 23. Episodic memory
Verified history such as "customer selected product X and booking Y completed." Store outcomes, not speculative model
reasoning.

## 24. Semantic memory
Stable facts with source/version: catalog facts, customer/account facts, store policies. Authoritative systems override
cached memory.

## 25. Procedural memory
Support/sales Skills and runbooks. Version and review them like code.

## 26. Preference memory
Explicit language/channel/product preferences. Respect consent, retention and deletion. Never infer sensitive traits.

## 27. Artifact memory
Provider receipts, ticket IDs, appointment IDs, retrieval evidence, evaluation artifacts. Large artifacts go to object
storage; memory stores references/hashes.

## 28. Organization memory
Brand voice, escalation policy, legal/compliance rules, approved tools and business operating rules. Curated and
versioned.

## 29. Memory trust hierarchy

```text
platform security policy
 >
organization rules
 >
authoritative CRM/catalog/support facts
 >
approved procedures
 >
explicit preferences
 >
verified episodes
 >
retrieved untrusted content
```

Memory never grants authorization.

## 30. Memory poisoning
A customer message, webpage or support document saying "ignore policy" is data. Typed memory writes, provenance, trusted
source classes, approval for high-trust memory and invalidation prevent promotion of untrusted instructions.

## 31. Memory scope
Every query must enforce tenant scope. Customer/thread scope is additive. Never retrieve cross-tenant memory and filter
after the LLM sees it.

# Capability Gateway

## 32. Gateway pipeline

```text
Action
 -> schema validation
 -> tenant/tool authorization
 -> risk classification
 -> deterministic policy
 -> approval if required
 -> idempotency
 -> provider
 -> normalized receipt
 -> audit
```

## 33. Risk classes
READ, WRITE, COMMUNICATE, FINANCIAL, PRIVILEGED. The sample blocks autonomous payment/refund and privileged capabilities.

## 34. Human approval
Bind approval to exact canonical action arguments, tenant, thread, customer, policy version, expiry and nonce.

## 35. Idempotency
Lead/case/appointment writes use stable keys. Production persists them with a unique DB constraint rather than process
memory.

## 36. Unknown outcomes
A provider timeout after a write is `UNKNOWN`. Reconcile by provider idempotency key/external reference before retrying.

# Enterprise connectors

## 37. Meta messaging
`providers/connectors.py` includes a WhatsApp-style Graph API send adapter. Production ingress additionally verifies
webhook signatures, deduplicates event IDs, normalizes messages and respects messaging-policy/template rules.

## 38. Commerce
The sample Shopify-like adapter implements catalog/order reads. Production should add pagination, rate-limit budgets,
webhook reconciliation, inventory/variant normalization and provider-version contract tests.

## 39. CRM
Customer reads and lead/appointment writes are normalized behind provider interfaces. This prevents agent logic from
depending on one CRM schema.

## 40. Support
The Zendesk-like adapter creates tickets. Add ticket lookup/update, assignment, SLA metadata and webhook resume.

## 41. MCP
MCP is a capability protocol, not an authorization layer. Production needs authenticated server registry, tool
discovery, schema drift detection, per-tool risk mapping, DLP and audit.

# Messaging and omnichannel

## 42. Channel normalization
Normalize inbound channel events into:
`tenant, customer, thread, channel, locale, message, attachments, event_id, timestamp`.

## 43. Conversation identity
Map channel identity to business customer identity only through verified mappings. Avoid accidental account linking.

## 44. Delivery
Outbound communication is an external side effect. Persist intent/outbox first, then send, then reconcile delivery
status.

## 45. Ordering
Channels may redeliver or reorder events. Use event IDs, channel timestamps and conversation sequence/fencing.

## 46. Attachments
Virus scan, MIME validate, size limit, isolate parsing and apply DLP before exposing attachment text to models.

## 47. Voice
Voice adds ASR/TTS, interruption, latency and explicit recording/consent requirements. Keep business actions in the same
Gateway.

# RAG and grounding

## 48. Ingestion pipeline

```text
source -> connector -> ACL -> parse -> normalize -> chunk -> embed/index -> version -> publish
```

## 49. Hybrid retrieval
Use lexical + vector + metadata + reranker. Customer/account ACL filtering occurs before model context.

## 50. Freshness
Policy/product facts need validity intervals and source versions. Webhook/change-data-capture can invalidate affected
chunks.

## 51. Citation/provenance
Every consequential answer should retain document/product/order/provider provenance internally.

# Security

## 52. Authentication
Production API derives tenant/user/service identity from OIDC/JWT/JWKS middleware; never trust tenant/customer roles from
an arbitrary request body.

## 53. Authorization
Combine RBAC and ABAC:
role + tenant + customer relationship + channel + tool + resource + risk + consent.

## 54. Secrets
Use workload identity/secret broker. Never put provider secrets in prompts, memory or graph checkpoints.

## 55. Prompt injection
All customer, document, web and MCP text is untrusted. Tool permission is deterministic outside the model.

## 56. DLP
Inspect outbound model/MCP/provider payloads for sensitive classes and destination policy.

## 57. Audit
The sample hash chain demonstrates tamper evidence. Production writes append-only durable events and optionally exports
to WORM storage/SIEM.

## 58. Abuse/fraud
Add rate limits, bot/spam detection, account-takeover signals, order ownership checks, high-value action limits and
manual review.

# Durable distributed execution

## 59. Postgres checkpointing
Use `AsyncPostgresSaver`/production LangGraph checkpoint storage with a pooled DB. The included default can be replaced
through dependency injection; production must not depend on process memory.

## 60. Transactional outbox
Workflow mutation and event publication intent commit in one DB transaction.

## 61. Kafka/Redpanda
Separate topics for inbound conversation, orchestration, provider writes, notifications, evaluation and DLQ.

## 62. Inbox
Consumers dedupe event IDs before applying business effects.

## 63. Redis
Use for rate limiting, short leases/cache and presence—not authoritative workflow state.

## 64. Leases/fencing
Workers lease a thread. Every authoritative write carries fencing epoch so a stale worker cannot continue after failover.

## 65. Multi-region
Assign a thread home region. Failover increments epoch; providers are reconciled before writes resume.

## 66. Durable timers
Appointments, SLA escalation, delayed follow-up and approval expiry require persisted timers/scheduler.

# Reliability

## 67. Failure taxonomy
MODEL, RETRIEVAL, POLICY, AUTH, PROVIDER, RATE_LIMIT, TIMEOUT, UNKNOWN_WRITE, CHECKPOINT, QUEUE, VALIDATION, HUMAN_WAIT.

## 68. Retry
Retry transient reads. Reconcile writes. Replan semantic failures. Never blindly retry an unknown external mutation.

## 69. Circuit breaker
Protect unhealthy CRM/commerce/support/model providers.

## 70. Bulkhead
Separate pools so slow ticketing or model calls do not starve inbound webhook acknowledgement.

## 71. Backpressure
Acknowledge/persist ingress quickly, then queue work. Apply tenant quotas and priority.

## 72. DLQ
Store exhausted events with tenant/thread/provider/error/provenance for replay after correction.

# Observability

## 73. Trace
`channel ingress -> graph -> agent -> model -> gateway -> provider -> response delivery`.

## 74. Correlation
request_id, event_id, tenant, customer, thread, plan revision, step, agent, tool, provider, approval, model, trace.

## 75. Metrics
first-response latency, resolution rate, human-handoff rate, grounded-answer rate, lead conversion, booking success,
provider error, duplicate-write prevention, policy blocks, tokens/conversation, cost/resolved conversation.

## 76. SLOs
Define ingress acknowledgement, orchestration availability, provider success and response latency separately.

# Evaluation

## 77. Offline scenarios
FAQ, ambiguous product request, recommendation, unavailable item, lead, appointment, order lookup, complaint, explicit
human request, injection, duplicate webhook, provider timeout.

## 78. Agent evals
Evaluate intent, retrieval, recommendation grounding, tool choice, argument accuracy, escalation and response.

## 79. Security evals
Cross-tenant retrieval, prompt injection, PII leakage, approval bypass, malicious MCP, duplicate write, stale worker.

## 80. Business evals
Measure helpfulness alongside operational outcomes without allowing optimization to bypass compliance or customer
choice.

# Deployment

## 81. Production services

```text
api/webhook-ingress
orchestrator-workers
rag/index-workers
provider-workers
mcp-gateway
scheduler
outbox-relay
evaluation-workers
```

Backed by PostgreSQL, Redis, Kafka/Redpanda, vector index and object storage.

## 82. Kubernetes
Non-root, read-only filesystem, dropped capabilities, workload identity, NetworkPolicies, HPA, PDB, topology spread and
separate service accounts.

## 83. CI/CD
format/lint/type/test -> security/dependency/secret scans -> SBOM -> image signing -> integration/provider contract tests
-> eval suite -> staging/canary -> production.

## 84. Model migration
Offline eval -> shadow -> canary -> staged rollout. Store model/prompt/tool-schema versions per run.

# End-to-end traces

## 85. Product recommendation
message -> memory -> customer -> knowledge -> catalog -> eligibility/ranking -> compliance -> grounded response.

## 86. Lead qualification
message -> clarify -> customer -> qualification -> approval -> idempotent CRM lead -> receipt -> response -> episode.

## 87. Appointment
intent -> service/location -> availability read -> customer confirmation -> approval -> idempotent booking -> receipt.

## 88. Support
issue -> customer/order -> RAG -> attempt resolution -> case if needed -> human handoff -> ownership transition.

## 89. Human takeover
customer asks for human -> handoff state -> compact context -> queue/owner -> AI customer writes disabled -> human
continues; AI may remain assistive.

## 90. Provider timeout
write sent -> timeout -> mark UNKNOWN -> query provider using external/idempotency key -> found: record success; absent:
retry safely.

# Code reading guide

## 91. `core/models.py`
Typed contract for plan, action, memory and workflow state.

## 92. `agents/orchestrator.py`
Deterministic dependency routing. Replace/augment plan creation with structured LLM planning under the same validation
contract.

## 93. `core/graph.py`
LangGraph orchestration and interrupt/resume boundary.

## 94. `core/bootstrap.py`
Dependency injection: agents receive Gateway, memory and knowledge; providers register capabilities centrally.

## 95. `tools/gateway.py`
Most important security boundary in the repository.

## 96. `providers/connectors.py`
Concrete HTTP adapters for messaging, commerce, CRM and support.

## 97. `memory/*`
Seven-layer memory scope and retrieval.

## 98. `rag/store.py`
Small runnable retrieval seam; replace storage/ranking with production hybrid retrieval while preserving tenant filters.

## 99. `security/*`
Deterministic policy, injection/redaction boundary and tamper-evident audit.

## 100. `migrations/001.sql`
Durable primitives: workflow, memory, idempotency, approvals, outbox and audit.

# Principal design review

## 101. Invariants

```text
Model != authorization
Memory != policy
Customer text != trusted instruction
RAG document != permission
MCP capability != authorization
Timeout != failure
Approval != idempotency
Human handoff != lost context
Recommendation != fabricated catalog fact
LLM statement != provider receipt
```

## 102. Principal questions
1. Why use a graph instead of one ReAct loop?
2. Where does conversation state live after a pod dies?
3. How is cross-tenant RAG prevented?
4. How do seven memory layers differ?
5. How is memory poisoning prevented?
6. How are stale catalog facts invalidated?
7. Why is customer identity separate from channel identity?
8. What happens when lead creation times out?
9. How do approval and idempotency differ?
10. How do you prevent duplicate appointments?
11. How does human ownership stop autonomous writes?
12. How are out-of-order WhatsApp events handled?
13. How do you enforce product/order ownership?
14. Why is MCP behind the Gateway?
15. How do you prevent prompt injection from support documents?
16. How do you version business procedures?
17. How does multi-region fencing work?
18. How do you evaluate recommendations without optimizing only conversion?
19. What are useful SLOs?
20. How do you canary a new model?
21. How do you handle a CRM outage?
22. How do you preserve auditability?
23. What belongs in graph state versus object storage?
24. How do you apply data retention/deletion to memory?
25. How do you scale from 100 to millions of conversations?

## 103. What is concrete here
Concrete code includes LangGraph orchestration, specialist agents, memory manager/store, tenant-filtered RAG seam,
capability Gateway, policy, approval interrupts, idempotency behavior, audit chain, resilient HTTP, Meta-channel send,
commerce catalog/order, CRM customer/lead/appointment, support ticket adapter, MCP server, FastAPI run/resume, SQL
schemas, tests, Docker and Kubernetes baseline.

## 104. What production infrastructure remains environment-specific
No repository can contain your real Meta/Shopify/Zendesk/CRM tenants, credentials, IdP, production Postgres/Kafka/Redis,
KMS, vector cluster, SIEM, workload identities or organization-specific legal policies. The code provides explicit
interfaces and deployment seams for them rather than pretending those external systems exist locally.

## 105. Final mental model

```text
Business conversation
      |
identity + tenant
      |
durable LangGraph
      |
memory + RAG + customer context
      |
specialist agents
      |
Capability Gateway
      |
enterprise systems
      |
receipts/evidence
      |
critic + verifier
      |
response or human handoff
      |
audit + memory + metrics
```

The LLM supplies adaptive reasoning. Production quality comes from grounded enterprise data, explicit workflow state,
least-privilege tools, durable side-effect semantics, human ownership, memory governance, verification and operations.


# Comprehensive System Design Expansion

## 106. Product capability map

This repository models the publicly described Business Agent problem as a governed enterprise agent platform:

```text
Public capability                  Architecture capability
--------------------------------------------------------------------
Business-specific Q&A          -> Knowledge/RAG Agent
Catalog recommendations        -> Catalog + Recommendation Agents
Appointment booking            -> Appointment Agent
Lead qualification             -> Lead Agent
Sales assistance               -> Sales Agent
Human takeover                 -> Handoff Agent + ownership state
WhatsApp/Messenger/Instagram   -> Omnichannel ingress/egress
Enterprise integrations        -> Capability Gateway + connectors/MCP
Enterprise controls            -> Policy/approval/audit/evaluation
```

The implementation is original. The table is a product-to-design mapping, not a statement about Meta's private
implementation.

## 107. Full production topology

```text
CUSTOMER CHANNELS
WhatsApp | Messenger | Instagram | Web
                   |
              Edge/Webhooks
                   |
       signature + replay validation
                   |
             Event Normalizer
                   |
        Identity / Tenant Resolver
                   |
              Event Inbox
                   |
              Kafka/Redpanda
                   |
        +----------v-----------+
        | ORCHESTRATION PLANE  |
        | LangGraph            |
        | Postgres checkpoint  |
        | Planner / Task DAG   |
        | Memory hydration     |
        +----------+-----------+
                   |
        +----------v-----------+
        |    AGENT RUNTIME     |
        | Customer360          |
        | Knowledge            |
        | Catalog              |
        | Recommendation       |
        | Lead / Appointment   |
        | Sales / Order        |
        | Support / Case       |
        | Handoff              |
        | Compliance / Critic  |
        | Verifier / Response  |
        +----------+-----------+
                   |
            Capability Gateway
                   |
     +-------------+-------------+-------------+
     |             |             |             |
    CRM         Commerce       Support         MCP
     |             |             |             |
 customer       products       tickets     enterprise
 lead/book      orders         handoff       tools
     +-------------+-------------+-------------+
                   |
          Provider receipts/events
                   |
            Transactional Outbox
                   |
          Delivery / Notifications
                   |
        Audit / Metrics / Tracing
```

## 108. Why separate channel, control, agent and data planes

Channel ingress must acknowledge quickly and safely. The control plane owns durable workflow state. Agents reason over
bounded context. Enterprise providers execute actions. Data systems retain authoritative state. This separation allows
each plane to scale, fail and be secured independently.

## 109. Channel ingress contract

Normalize every inbound event to:

```json
{
  "event_id": "...",
  "tenant_id": "...",
  "channel": "whatsapp",
  "channel_account_id": "...",
  "channel_user_id": "...",
  "customer_id": "...",
  "thread_id": "...",
  "message_id": "...",
  "timestamp": "...",
  "locale": "en",
  "text": "...",
  "attachments": []
}
```

Never let the model parse provider-specific webhook envelopes directly.

## 110. Webhook authenticity

Ingress validates provider signature, timestamp/replay window and expected application/account before persisting an
event. Authentication happens before agent execution.

## 111. Fast acknowledgement

Do not run the LLM synchronously inside the webhook acknowledgement path.

```text
webhook
 -> verify
 -> persist/dedupe
 -> enqueue
 -> 2xx
```

Workers continue asynchronously.

## 112. Event deduplication

Providers can redeliver. Store `(provider, event_id)` under a unique constraint before dispatch.

Duplicate delivery is normal distributed-system behavior, not an exceptional condition.

## 113. Out-of-order messages

Track provider timestamp and conversation sequence where available. Late events can be:
- processed with ordering metadata;
- ignored when superseded;
- reconciled into current state;
- routed to a human if ambiguity could cause a harmful action.

## 114. Conversation identity

`channel_user_id` is not automatically a CRM customer ID.

```text
channel identity
 -> verified mapping
 -> business customer identity
```

Sensitive order/account information requires an appropriate ownership/authentication check.

## 115. Tenant resolution

Tenant is resolved from authenticated channel/business account configuration, not from customer-provided text.

## 116. Conversation ownership

State machine:

```text
AI_OWNED
  |
HANDOFF_REQUESTED
  |
HUMAN_OWNED
  |
HUMAN_RESOLVED
  |
AI_OWNED (only through explicit transition)
```

When `HUMAN_OWNED`, autonomous customer-facing mutations/messages are blocked unless explicitly configured as assistive.

## 117. LangGraph execution semantics

Graph nodes represent durable business-workflow boundaries rather than arbitrary prompt turns.

A node should:
1. consume typed state;
2. call bounded agent/tool logic;
3. produce typed state updates;
4. checkpoint;
5. expose failures explicitly.

## 118. Checkpoint boundaries

Checkpoint:
- after normalized ingress;
- after plan creation;
- before/after sensitive actions;
- after provider receipts;
- before human waits;
- after handoff;
- after final verification.

## 119. Planner validation

If an LLM planner is added, validate its structured plan deterministically:
- allowed agent names;
- acyclic dependencies;
- maximum steps;
- tenant/resource scope;
- required customer verification;
- maximum tool/model/time/cost budgets;
- no forbidden capability.

## 120. Plan revision

A replan increments `plan.revision`. Preserve completed verified work and failure history. Replanning should produce a
materially different route, not reset the same failed step indefinitely.

## 121. Customer360 data model

A normalized customer view can contain:

```text
customer_id
verified identities
locale
consents
account tier
preferences
recent orders
open cases
appointments
lead/opportunity refs
service eligibility
```

Do not copy every CRM field into the prompt.

## 122. Customer context minimization

Retrieve only fields needed for the current intent. This reduces privacy exposure, tokens and accidental use of
irrelevant sensitive information.

## 123. Knowledge ingestion architecture

```text
Business source
     |
connector
     |
source ACL + tenant
     |
parser
     |
normalizer
     |
chunker
     |
embedding + lexical index
     |
versioned publication
```

Store source URI/ID, version/hash, validity interval and ACL with every chunk.

## 124. ACL before retrieval

Correct order:

```text
tenant/resource authorization
 -> eligible corpus
 -> retrieval/ranking
 -> model
```

Incorrect order:

```text
retrieve everything -> model -> filter answer
```

The latter already leaked unauthorized data into model context.

## 125. Hybrid retrieval

Production retrieval:

```text
BM25 / lexical
     +
vector ANN
     +
metadata/structured lookup
     |
RRF or learned fusion
     |
reranker
     |
freshness/ACL validation
```

## 126. Grounding threshold

If authoritative evidence is missing or weak, ask a question or hand off. Do not compensate for retrieval failure with
model confidence.

## 127. Knowledge freshness

Business facts such as shipping rules, hours, prices and promotions can change quickly. Support:
- validity windows;
- source version;
- webhook/CDC invalidation;
- scheduled refresh;
- stale-answer suppression.

## 128. Catalog normalization

Normalize provider-specific catalog data to:

```text
product_id
variant_id
title
description
price/currency
inventory state
availability region
attributes
media
policy tags
source version
```

Recommendation agents operate on normalized facts.

## 129. Recommendation pipeline

```text
customer need
 -> hard eligibility
 -> catalog retrieval
 -> semantic relevance
 -> business rules
 -> diversity
 -> explanation
```

Hard eligibility always precedes optimization.

## 130. Recommendation safety

Never fabricate:
- inventory;
- price;
- discount;
- warranty;
- delivery date;
- compatibility.

Provider data is authoritative.

## 131. Lead qualification state

Example:

```text
NEW
 -> DISCOVERY
 -> QUALIFIED
 -> CONSENTED
 -> CRM_CREATED
 -> ASSIGNED
```

Capture only fields justified by the business process and consent requirements.

## 132. Lead scoring

If ML scoring is used, keep scoring separate from conversational reasoning. Version the model, features and thresholds
and audit consequential routing.

## 133. Appointment architecture

```text
service/location need
 -> availability read
 -> present choices
 -> customer selection
 -> confirm
 -> Gateway approval/policy
 -> idempotent booking
 -> provider receipt
```

A requested time is not a confirmed appointment.

## 134. Appointment concurrency

Two customers can select the same slot. Availability is advisory; provider booking transaction decides success. On
conflict, refresh and offer alternatives.

## 135. Sales workflow

Sales Agent orchestrates rather than owns every capability:

```text
need discovery
 -> catalog
 -> recommendation
 -> lead/appointment/order intent
 -> confirmation
 -> governed action
```

## 136. Payments boundary

Payment initiation/capture is a distinct regulated/high-risk capability. The sample deliberately denies autonomous
capture. A production deployment requires payment-provider contracts, strong authentication, fraud/risk controls,
customer confirmation and market-specific compliance.

## 137. Order privacy

Before returning order data, validate customer/order relationship. Avoid exposing address/payment/support details based
only on an order number supplied in chat.

## 138. Support resolution

```text
classify issue
 -> customer/order context
 -> knowledge retrieval
 -> grounded resolution attempt
 -> confidence/risk check
 -> resolve OR case/handoff
```

## 139. Case priority

Priority can combine deterministic business rules and classifier output. Safety, account access, fraud and severe
service-impact categories should not depend only on an LLM judgment.

## 140. Handoff context packet

Transfer:
```text
customer reference
verified identity status
intent/category
short conversation summary
relevant orders/products
knowledge already consulted
actions attempted
provider receipts
open question
risk/compliance flags
```

Avoid dumping the entire raw prompt history.

## 141. Human takeover synchronization

When a human responds through an external support console, ingest that event and update ownership/checkpoint state so
the AI does not race the human.

## 142. Human-assist mode

The AI can remain behind the scenes:
- retrieve knowledge;
- summarize;
- suggest replies;
- surface customer/order facts.

Human remains the sender/decision-maker.

## 143. Response generation contract

Response generation receives verified structured facts, not unrestricted access to every provider. It should know:
- facts allowed to say;
- uncertainties;
- channel;
- locale;
- tone;
- required disclosures;
- handoff state.

## 144. Localization

Separate language generation from policy. A translation/localization model cannot change price, legal terms or
authorization.

## 145. Brand voice

Brand voice belongs in curated procedural/organization memory. It is lower priority than legal/compliance rules.

# Advanced Memory Design

## 146. Working-memory lifecycle

Working memory exists for a thread and expires/compacts after completion. Keep unresolved entities, recent evidence and
workflow state—not a duplicate of the full transcript.

## 147. Episodic-memory write gate

Only write an episode after verification:

```text
goal
actions
receipts
outcome
human resolution if known
applicability
```

Failed/speculative attempts can be retained as failure lessons with explicit status.

## 148. Semantic-memory sources

Semantic facts should be derived from authoritative CRM/catalog/knowledge sources with provenance and expiry.

## 149. Procedural-memory governance

Runbooks/Skills are reviewed artifacts. Use owner, version, effective date and rollback.

## 150. Preference-memory consent

Customer preference memory requires clear scope and deletion behavior. Do not infer sensitive characteristics.

## 151. Artifact memory

Store immutable references/hashes for:
- ticket receipts;
- appointment receipts;
- provider request/response metadata;
- retrieval evidence;
- evaluation reports.

## 152. Organization memory

Organization rules may include:
- escalation policy;
- prohibited claims;
- brand requirements;
- approved providers;
- retention;
- compliance.

Only authorized administrators/processes modify this layer.

## 153. Memory provenance

Every durable memory record should expose:
`source_type, source_id, source_version, created_at, verified_at, confidence, expiry`.

## 154. Memory conflict

When memories conflict, authoritative/fresher sources win. Do not ask the LLM to choose between an old cached price and
a current commerce-provider price.

## 155. Memory compaction

Compress verbose episodes into structured facts while preserving links to original evidence. Never compact away
important uncertainty or provider receipt IDs.

## 156. Memory retrieval budget

Allocate token budgets per layer. Organization/procedural rules are small and high priority; episodic examples should
be retrieved only when relevant.

## 157. Right-to-delete propagation

A deletion request must propagate to:
- customer preference/episodic memory;
- indexes;
- caches;
- derived artifacts where required;
- future retrieval.

Keep legally required audit records under separate policy where applicable.

# Tool and Connector Architecture

## 158. Tool contract

Each capability declares:
```text
name
input schema
output schema
risk
required roles/scopes
idempotency semantics
timeout
provider
data classification
```

## 159. Provider normalization

Agents should not reason over raw Shopify/Zendesk/CRM-specific payloads. Adapter layers normalize schemas and errors.

## 160. Provider token broker

Workers request short-lived scoped credentials from a broker/workload-identity mechanism. Do not expose master provider
tokens to the LLM.

## 161. Rate-limit budgets

Track provider quotas per tenant/provider. Retry-after headers feed durable timers instead of sleeping a worker for
minutes.

## 162. Circuit breaker states

```text
CLOSED -> OPEN -> HALF_OPEN -> CLOSED
```

Fallback may be read-only cache, human handoff or delayed retry depending on capability.

## 163. Provider contract tests

Run tests against sandbox/test accounts for:
- auth;
- pagination;
- schema;
- idempotency;
- rate limits;
- error mapping;
- webhook reconciliation.

## 164. MCP server registry

Registry record:
```text
server identity
transport/endpoint
owner
approved tenant(s)
allowed tools
tool schema hash
risk map
data classification
version
```

## 165. MCP schema drift

On rediscovery, compare tool schema hashes. New/changed capabilities require approval rather than silently expanding
agent authority.

# Security and Governance

## 166. Zero-trust agent principle

The model is not a trusted principal. It proposes actions under an authenticated user's/service's bounded authority.

## 167. Identity propagation

Carry verified identity context through queue/event boundaries using signed service-to-service claims or trusted task
records, not model-generated metadata.

## 168. RBAC + ABAC

Example:

```text
role=service_agent
AND tenant=A
AND customer belongs to A
AND action=create_case
AND channel permitted
AND risk <= role policy
```

## 169. Approval token

Bind approval to canonical action hash, resource, tenant, thread, expiry, nonce and policy version.

## 170. Approval invalidation

Invalidate approval if:
- arguments change;
- customer/resource changes;
- policy version changes materially;
- approval expires;
- ownership moves to human.

## 171. Secret exfiltration defense

Secrets are absent from model context. Egress and DLP provide additional controls if malicious content asks for them.

## 172. Prompt-injection handling

Treat injection detection as a signal, not the sole defense. Real safety comes from privilege separation and deterministic
tool authorization.

## 173. Data classification

Tag:
```text
PUBLIC
BUSINESS_INTERNAL
CUSTOMER_PII
PAYMENT_SENSITIVE
REGULATED
SECRET
```

Tool/model/provider routes enforce allowed destinations.

## 174. Encryption

TLS in transit; managed encryption at rest; field-level encryption/tokenization for selected sensitive identifiers.

## 175. Audit separation

Operational logs optimize debugging. Audit logs establish accountability. They have different access, retention and
immutability requirements.

## 176. Policy-as-code

Version deterministic policies with tests. Every action decision records policy version.

# Distributed Systems

## 177. Inbox/outbox flow

```text
channel event
 -> inbox dedupe
 -> workflow transaction
 -> outbox
 -> relay
 -> Kafka
 -> consumer inbox
```

## 178. Exactly-once business effect

Transport is at-least-once. Business effects become effectively once through unique idempotency keys and reconciliation.

## 179. Unknown-write state machine

```text
NOT_STARTED
 -> SENT
 -> CONFIRMED
      or
 -> UNKNOWN
 -> RECONCILING
 -> CONFIRMED / SAFE_TO_RETRY / HUMAN_REVIEW
```

## 180. Queue partitioning

Partition conversation work by tenant/thread key to preserve useful ordering while allowing horizontal scale.

## 181. Hot tenants

Use tenant quotas/weighted fair scheduling so one high-volume business cannot starve the fleet.

## 182. Worker lease

A worker claims `(thread, epoch, expiry)`. Heartbeats extend it.

## 183. Fencing token

Every state-changing worker operation carries epoch. Storage rejects stale epochs.

## 184. Multi-region failover

```text
home region unavailable
 -> acquire global ownership
 -> epoch++
 -> restore checkpoint
 -> reconcile pending provider actions
 -> resume
```

## 185. Split-brain defense

Global ownership plus fencing prevents two regions from performing writes for one thread.

## 186. Durable waiting

Human approvals, appointments and support responses can take hours/days. Persist waits; do not hold a worker/process.

## 187. Cancellation

Cancellation is durable and checked before new provider writes. Already-sent unknown writes must still be reconciled.

# Observability and SRE

## 188. Trace spans

Useful spans:
```text
ingress.verify
inbox.persist
graph.node
memory.retrieve
rag.retrieve
model.call
gateway.policy
approval.wait
provider.call
outbox.publish
channel.send
```

## 189. Business and technical metrics

Do not confuse conversion with agent correctness. Track:
- grounded answer rate;
- containment/resolution;
- human takeover;
- duplicate-write prevention;
- appointment/provider success;
- latency/error;
- policy blocks;
- customer correction rate;
- cost.

## 190. Error budget

Separate SLOs for webhook ingestion, orchestration, read providers, write providers and outbound delivery.

## 191. Alerting

Alert on symptoms:
- backlog age;
- provider error surge;
- checkpoint failure;
- duplicate-effect anomaly;
- cross-tenant authorization denial anomaly;
- handoff queue SLA breach.

## 192. Runbooks

Runbooks should cover provider outage, queue backlog, model degradation, bad deployment, RAG corruption, memory/index
incident and security kill switch.

# Evaluation and Quality

## 193. Conversation simulator

Generate multi-turn scenarios with changing customer constraints, provider errors and human takeover events.

## 194. Deterministic assertions

Examples:
- never expose another tenant's order;
- no appointment success without provider receipt;
- explicit human request transitions ownership;
- unavailable product not recommended as available;
- duplicate event creates one lead.

## 195. LLM-as-judge limits

Use model judges for nuanced helpfulness/style, but deterministic checks for security, provider receipts and side-effect
correctness.

## 196. Production feedback

Human corrections, case resolution and customer follow-up can become evaluation data after privacy/quality controls—not
automatically trusted memory.

## 197. Shadow model

A candidate model can generate decisions without executing tools or sending responses. Compare against production
behavior offline.

## 198. Canary

Roll out by tenant/cohort/traffic percentage with automatic rollback thresholds.

# Capacity and Economics

## 199. Capacity model

Estimate:
```text
inbound messages/sec
conversations/sec
turns/conversation
model calls/turn
retrieval QPS
provider calls/turn
write-action rate
handoff rate
event/checkpoint writes
```

## 200. Latency budget

Example decomposition:
```text
ingress + queue
memory/RAG
model reasoning
provider reads
response model
channel send
```

Write/approval workflows are naturally longer and should have separate objectives.

## 201. Cost attribution

Tag model, retrieval, provider, storage and queue cost by tenant/thread/use case.

## 202. Cost optimization

Use:
- smaller model for classification;
- cache safe read facts with freshness;
- bounded memory context;
- retrieval before generation;
- skip unnecessary agents;
- batch offline analytics;
- limit replan loops.

# Deployment and Operations

## 203. Service decomposition

At scale:

```text
webhook-ingress
conversation-api
orchestrator-worker
memory-service
retrieval-service
provider-worker
mcp-gateway
notification-worker
scheduler
outbox-relay
evaluation-service
```

## 204. Database separation

Consider distinct logical stores/schemas for workflow, customer memory, retrieval metadata and audit to simplify
retention/access controls.

## 205. Kubernetes availability

Use HPA, PDB, topology spread, readiness, graceful shutdown, workload identity and NetworkPolicy.

## 206. Graceful worker shutdown

Stop claiming work, checkpoint active step, finish/reconcile critical provider operation, release lease, then exit.

## 207. Schema migration

Use backward-compatible expand/migrate/contract. In-flight workflows may contain older state versions.

## 208. Workflow-state versioning

Store state schema version and migration function so old checkpoints remain resumable after deployments.

## 209. Feature flags

Gate new model, agent, connector, memory layer and policy behavior per tenant/cohort.

## 210. Disaster recovery

Restore workflow/checkpoint DB, memory metadata, retrieval index metadata, artifact references and policy/config. Provider
systems remain independently authoritative.

## 211. Kill switches

Disable:
- outbound messages;
- all writes;
- specific provider/tool;
- MCP;
- one tenant;
- recommendation;
- memory writes;
- one model version.

# Detailed Failure Scenarios

## 212. CRM down

Use breaker. Avoid guessing customer facts. Continue generic knowledge when safe or hand off/delay.

## 213. Commerce down

Do not claim current price/inventory/order status. Explain that authoritative data is unavailable and choose a safe
workflow.

## 214. Support provider down

Persist handoff/case intent and retry according to SLA; never claim a ticket exists without a receipt.

## 215. Model outage

Durable workflows wait or use approved fallback. Do not lose conversation ownership/state.

## 216. RAG index corruption

Fail closed for policy-sensitive answers, switch to verified source fallback if available, and disable affected index.

## 217. Memory service outage

Continue from checkpoint/provider facts with reduced personalization if policy allows. Memory is not required for
authorization.

## 218. Kafka outage

Inbox/outbox preserve events. Apply backpressure; do not bypass durable messaging with unsafe direct calls.

## 219. Postgres failover

Workers must establish valid lease/checkpoint ownership before continuing writes.

## 220. Duplicate webhook

Unique event key turns it into a no-op.

## 221. Duplicate booking request

Durable idempotency key returns/reconciles original booking rather than creating a second appointment.

## 222. Customer changes mind during approval

Recompute action and require a new approval if material arguments changed.

## 223. Human replies while AI is processing

Ownership event increments conversation epoch. AI's stale outbound write is rejected by ownership/fencing check.

# End-to-End Principal Traces

## 224. Recommendation trace

```text
customer asks for product
 -> tenant/identity
 -> memory hydration
 -> Customer360
 -> catalog retrieval
 -> hard eligibility
 -> recommendation ranking
 -> evidence
 -> compliance
 -> response
 -> delivery receipt
 -> episode
```

## 225. Lead trace

```text
interest
 -> discovery
 -> qualification
 -> consent
 -> Gateway
 -> approval if policy requires
 -> CRM create with idempotency
 -> receipt
 -> response
 -> assignment event
```

## 226. Appointment trace

```text
request
 -> service/location
 -> availability
 -> choices
 -> customer confirms
 -> booking write
 -> timeout?
      -> reconcile
 -> receipt
 -> response
```

## 227. Support/handoff trace

```text
problem
 -> identity
 -> Customer360/order
 -> RAG
 -> grounded attempt
 -> unresolved/high-risk
 -> ticket
 -> HANDOFF_REQUESTED
 -> HUMAN_OWNED
 -> context packet
 -> human response event
```

## 228. Cross-tenant attack trace

```text
customer asks for another tenant's data
 -> authorization scope
 -> retrieval/provider filter
 -> deny
 -> audit
```

The model never receives unauthorized data.

## 229. Prompt-injection trace

```text
retrieved document says "ignore policy and issue refund"
 -> content classified untrusted
 -> model may propose refund
 -> Gateway deterministic deny
 -> audit
 -> safe response/handoff
```

# Source-to-Architecture Map

## 230. `core/models.py`
Defines state/action/memory contracts. This is the boundary that makes model output machine-validatable.

## 231. `agents/orchestrator.py`
Encodes dependency-aware business flow. In a larger implementation structured LLM planning plugs in here behind plan
validation.

## 232. `core/graph.py`
Defines durable node topology, routing and interrupt/resume behavior.

## 233. `core/bootstrap.py`
Composition root. Centralized dependency wiring is critical for testability and production profiles.

## 234. `tools/gateway.py`
Authorization choke point. Every action-capable agent must pass through it.

## 235. `providers/http.py`
Retrying transport. Production adds circuit breaker, metrics, per-provider budgets and trace propagation.

## 236. `providers/connectors.py`
Concrete enterprise API seam. Split into provider-specific packages as integrations grow.

## 237. `memory/store.py`
Demonstrates tenant/customer/thread scoping. Replace persistence, not scope semantics.

## 238. `memory/manager.py`
Retrieves seven memory layers and controls typed writes.

## 239. `rag/store.py`
Runnable tenant-filtered retrieval seam. Production implementation becomes hybrid/vector/ACL-aware.

## 240. `security/policy.py`
Deterministic authorization. Never move this responsibility into an LLM prompt.

## 241. `security/guard.py`
Defense-in-depth content checks/redaction, not the primary permission boundary.

## 242. `security/audit.py`
Demonstrates hash-linked audit events.

## 243. `mcp/server.py`
Shows protocol exposure. Production adds governed client/session registry and enterprise tools.

## 244. `api/main.py`
Demonstrates run/resume. Production adds verified identity middleware, webhook endpoints, rate limiting and production DI.

## 245. `migrations/001.sql`
Shows durable workflow/memory/idempotency/approval/outbox/audit primitives.

## 246. `deploy/*`
Baseline hardened container/control-plane deployment. Production decomposes services and adds HA/network policies.

# Principal Design Review Questions

## 247. Architecture questions

1. Why is channel ingress asynchronous?
2. How do you dedupe provider events?
3. How do you handle out-of-order messages?
4. How is channel identity mapped to CRM identity?
5. Where is tenant identity derived?
6. Why LangGraph instead of one agent loop?
7. What is checkpointed?
8. How is a plan validated?
9. When should the agent replan?
10. How is RAG ACL enforced?
11. How do you invalidate stale catalog knowledge?
12. Why normalize provider schemas?
13. How does appointment concurrency work?
14. How do you verify order ownership?
15. How does human takeover prevent races?
16. What goes into a handoff packet?
17. How do seven memory layers differ?
18. How is memory poisoning prevented?
19. How are memory conflicts resolved?
20. How does deletion propagate?
21. Why is MCP behind a Gateway?
22. How do you detect MCP schema drift?
23. Why does approval not solve duplicate writes?
24. What is an unknown side effect?
25. How do you reconcile a timeout?
26. Why use outbox/inbox?
27. How do leases and fencing differ?
28. How does multi-region failover work?
29. What if CRM is down?
30. What if the model is down?
31. What if memory is down?
32. What are useful SLOs?
33. How do you evaluate recommendation grounding?
34. How do you prevent conversion optimization from bypassing compliance?
35. How do you canary a new model?
36. How do you calculate capacity?
37. What is the largest cost driver?
38. What kill switches are required?
39. What must be in an audit record?
40. What would you change for regulated industries?

# Final Architecture Invariants

## 248. Invariants

```text
Model != authority
Memory != policy
Customer text != trusted instruction
RAG result != authorization
Channel identity != verified customer identity
Recommendation != provider fact
Requested appointment != confirmed booking
Timeout != failed write
Approval != idempotency
MCP tool != permission
Handoff != context loss
Human ownership != AI autonomy
LLM claim != provider receipt
Worker RAM != durable state
```

## 249. Production-readiness checklist

Before a real deployment, require:
- verified channel webhooks;
- OIDC/workload identity;
- tenant/customer authorization;
- durable Postgres checkpointing;
- durable idempotency;
- provider reconciliation;
- outbox/inbox + queue;
- human ownership state;
- hybrid ACL-aware RAG;
- governed seven-layer memory;
- secrets broker;
- DLP;
- MCP governance;
- immutable audit;
- traces/metrics/SLOs;
- adversarial evals;
- HPA/PDB/NetworkPolicy;
- DR exercise;
- kill switches.

## 250. Mental model

A Meta-Business-Agent-class system is not merely:

```text
customer -> LLM -> answer
```

It is:

```text
customer event
 -> authenticated business context
 -> durable workflow
 -> governed memory + enterprise knowledge
 -> specialist reasoning
 -> deterministic capability authorization
 -> enterprise system of record
 -> provider evidence
 -> verification
 -> response or human ownership
 -> durable audit/metrics/memory
```

The model supplies adaptive reasoning. The surrounding distributed system supplies correctness, security, durability,
enterprise integration and operational trust.
