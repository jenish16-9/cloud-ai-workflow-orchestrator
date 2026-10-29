from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from .config import get_settings
from .models import Workflow, WorkflowCreate, GitHubWebhook
from .planner import plan_pipeline
from .queue import enqueue
from .repository import repository

settings = get_settings()
app = FastAPI(title="AI CI/CD Workflow Orchestrator", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.api_cors_origins.split(",")], allow_methods=["*"], allow_headers=["*"])
Instrumentator().instrument(app).expose(app)

@app.middleware("http")
async def request_id(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", "generated")
    return response

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ci-cd-orchestrator", "queue_backend": settings.queue_backend}

async def create_pipeline(payload: WorkflowCreate):
    steps = await plan_pipeline(payload.goal)
    workflow = Workflow(name=f"{payload.repository} pipeline", template="ci_cd", repository=payload.repository, branch=payload.branch, commit_sha=payload.commit_sha, event_name=payload.event_name, goal=payload.goal, input=payload.input, steps=steps)
    workflow = await repository.create(workflow)
    enqueue(workflow.id)
    return workflow

@app.post("/api/v1/pipelines", response_model=Workflow, status_code=202)
async def trigger_pipeline(payload: WorkflowCreate):
    return await create_pipeline(payload)

@app.post("/api/v1/webhooks/github", response_model=Workflow, status_code=202)
async def github_webhook(payload: GitHubWebhook, x_hub_signature_256: str | None = Header(default=None), x_github_event: str | None = Header(default="push")):
    if settings.github_webhook_secret and x_hub_signature_256 is None:
        raise HTTPException(401, "Missing GitHub signature")
    return await create_pipeline(WorkflowCreate(repository=payload.repository, branch=payload.branch, commit_sha=payload.commit_sha, event_name=x_github_event or payload.event_name, goal=payload.goal))

@app.get("/api/v1/pipelines/{workflow_id}", response_model=Workflow)
async def get_pipeline(workflow_id: str):
    workflow = await repository.get(workflow_id)
    if not workflow:
        raise HTTPException(404, "Pipeline not found")
    return workflow

@app.get("/api/v1/pipelines/{workflow_id}/events")
async def get_pipeline_events(workflow_id: str):
    return await repository.list_events(workflow_id)

@app.get("/api/v1/pipelines")
async def list_pipelines():
    return await repository.list_workflows()
