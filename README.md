# AI-Enhanced CI/CD Workflow Orchestrator

Production-style full-stack starter for automating GitHub-based build, test, security, container, and AWS deployment pipelines.

## Run locally

1. Copy `.env.example` to `.env`.
2. Run `docker compose up --build`.
3. Open the dashboard at `http://localhost:3000` or API docs at `http://localhost:8000/docs`.

The local profile uses Redis and a Redis-backed repository. Set `QUEUE_BACKEND=sqs`, `AWS_REGION`, and `SQS_QUEUE_URL` for AWS queueing. Set `PIPELINE_EXECUTION_MODE=docker` to run pipeline commands; the default `simulated` mode is safe for local demonstrations. GitHub push events can call `/api/v1/webhooks/github`. LangSmith variables are included for tracing and Prometheus metrics are exposed at `/metrics`.
