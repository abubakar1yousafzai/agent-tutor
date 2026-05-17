# AgentTutor — Cost Analysis

## Phase 1: Zero-Backend-LLM Architecture

The Zero-Backend-LLM constraint is not just a hackathon rule — it is the core cost optimization strategy.

### Monthly Infrastructure Cost

| Component | Provider | Plan | Cost |
|-----------|----------|------|------|
| FastAPI backend | Fly.io | shared-cpu-1x, 256 MB RAM | **$0** (free tier) |
| PostgreSQL | Neon | 0.5 GB storage, 10 compute hours | **$0** (free tier) |
| Chapter content | Local filesystem (Fly volume) | 1 GB volume | **$0** (free tier) |
| LLM API calls | None | Zero-Backend-LLM architecture | **$0** |
| Domain / TLS | Fly.io | Auto-provisioned | **$0** |
| **TOTAL** | | | **$0/month** |

### Student Cost

Students need a ChatGPT Plus subscription ($20/month) to use the ChatGPT App. This subscription is:
- Already paid by the student independently
- Not a cost to the course provider
- Provides access to all GPT-4o features including GPT Actions

**Course provider cost per student: $0.00**

---

## Why Zero-Backend-LLM Is Cost-Optimal

### Traditional LLM-backed course platform

| Component | Cost |
|-----------|------|
| Claude/GPT API per student/month (50 sessions × 2K tokens) | ~$3–8 |
| Backend hosting | $5–20 |
| Vector database (RAG) | $10–50 |
| **Total per student/month** | **$18–78** |

### AgentTutor (Zero-Backend-LLM)

| Component | Cost |
|-----------|------|
| LLM API calls | $0 (student's ChatGPT Plus) |
| Backend hosting | $0 (Fly.io free tier) |
| Database | $0 (Neon free tier) |
| **Total per student/month** | **$0** |

**Savings: 100% reduction in infrastructure cost**

---

## Scaling Economics

| Students | Traditional Platform | AgentTutor |
|----------|---------------------|------------|
| 100 | ~$1,800–7,800/month | **$0** |
| 1,000 | ~$18,000–78,000/month | **$0–50*** |
| 10,000 | ~$180,000+/month | **$0–200*** |

*Small Fly.io costs may apply at high scale; Neon paid plan at >10GB storage.

---

## Phase 2 Cost Projection (with LLM backend)

If Phase 2 adds backend LLM calls (e.g., adaptive quiz generation):

| Component | Estimated Cost |
|-----------|---------------|
| Claude Haiku (summarization, adaptive hints) | ~$0.25/student/month |
| Claude Sonnet (complex explanations) | ~$1.50/student/month |
| Neon paid plan (>0.5 GB) | $19/month flat |
| Fly.io (dedicated CPU for LLM routing) | $10–20/month |
| **Total at 100 students** | **~$200/month** |

Phase 1 Zero-Backend-LLM architecture provides a cost-free baseline to validate product-market fit before incurring any LLM API costs.

---

## Return on Investment

Assuming a course price of $50/student (one-time):

| Students | Revenue | Phase 1 Cost | Margin |
|----------|---------|-------------|--------|
| 10 | $500 | $0 | 100% |
| 100 | $5,000 | $0 | 100% |
| 1,000 | $50,000 | $0–50 | ~100% |

The Zero-Backend-LLM architecture delivers **100% gross margin** on infrastructure for the first 1,000+ students.
