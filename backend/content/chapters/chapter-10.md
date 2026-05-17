# Chapter 10: Production Deployment

## Learning Objectives
- Deploy a FastAPI application to Fly.io
- Configure environment variables and secrets securely
- Set up health checks and monitoring
- Implement zero-downtime deployments

---

## 10.1 Production Readiness Checklist

Before deploying any agent backend to production:

- [ ] All secrets in environment variables (no hardcoded credentials)
- [ ] Health endpoint responding at `/health`
- [ ] Database connection pooling configured
- [ ] CORS origins restricted to production domains
- [ ] Error logging to structured JSON format
- [ ] Rate limiting on public endpoints
- [ ] SSL/TLS enforced
- [ ] Database migrations tested

---

## 10.2 Deploying to Fly.io

Fly.io is the recommended platform for AgentTutor — global edge deployment with a generous free tier.

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### fly.toml

```toml
app = "agenttutor-api"
primary_region = "sin"

[build]

[env]
  APP_ENV = "production"

[[services]]
  protocol = "tcp"
  internal_port = 8080

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

  [[services.ports]]
    port = 80
    handlers = ["http"]
    force_https = true

  [[services.http_checks]]
    interval = "15s"
    timeout = "5s"
    grace_period = "30s"
    method = "GET"
    path = "/health"
```

### Deploy commands

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login and create app
fly auth login
fly launch --name agenttutor-api --region sin

# Set secrets (never commit these)
fly secrets set DATABASE_URL="postgresql+asyncpg://..." \
              ALLOWED_ORIGINS="https://chatgpt.com,https://chat.openai.com"

# Deploy
fly deploy

# View logs
fly logs
```

---

## 10.3 Database Configuration for Production

### Connection pooling with Neon

Use the pooler URL from Neon dashboard:

```
postgresql+asyncpg://user:pass@ep-...-pooler.region.aws.neon.tech/neondb?sslmode=require
```

### SQLAlchemy pool settings

```python
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,   # Verify connections before use
    pool_recycle=300,     # Recycle every 5 minutes
)
```

---

## 10.4 Monitoring and Observability

### Health check
The `/health` endpoint returns `{"status": "ok", "llm_calls": 0}`. Fly.io polls it every 15 seconds — 3 failures triggers an automatic restart.

The `llm_calls: 0` field is a live assertion of the Zero-Backend-LLM invariant.

### Structured logging

```python
import logging, json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "timestamp": self.formatTime(record),
        })
```

### Key metrics to monitor
- Request latency: p95 < 500ms
- DB query time: p95 < 100ms
- Error rate: < 0.1%
- `llm_calls` counter: must always be 0

---

## 10.5 Cost Analysis

For AgentTutor Phase 1 (Zero-Backend-LLM architecture):

| Component | Provider | Monthly Cost |
|-----------|----------|-------------|
| FastAPI backend | Fly.io (shared-cpu-1x) | $0 (free tier) |
| PostgreSQL | Neon (0.5 GB) | $0 (free tier) |
| Chapter content | Local filesystem | $0 |
| LLM API calls | None — Zero-Backend-LLM | $0 |
| **Total** | | **$0/month** |

This is the power of the Zero-Backend-LLM architecture: educational AI at zero infrastructure cost. All LLM intelligence is delivered by the ChatGPT App — which the student already pays for as a ChatGPT Plus subscriber.

---

## Course Complete!

Congratulations — you have completed the AI Agents Course. Topics covered:

1. What AI agents are and the agent loop
2. Claude Agent SDK and tool use
3. Building production-ready agents
4. Model Context Protocol (MCP)
5. Agent Skills and SKILL.md specification
6. Multi-agent collaboration patterns
7. Agent memory and state management
8. Agent-to-Agent (A2A) protocol
9. Agent Factory Architecture and Spec-Driven Development
10. Production deployment on Fly.io

You are now equipped to build, deploy, and scale AI agents in production.
