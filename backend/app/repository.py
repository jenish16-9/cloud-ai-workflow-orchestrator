import asyncio
import json
from .models import Workflow, Event
from .config import get_settings

class WorkflowRepository:
    def __init__(self):
        self.workflows: dict[str, Workflow] = {}
        self.events: dict[str, list[Event]] = {}
        self.lock = asyncio.Lock()
        try:
            from redis import Redis
            self.redis = Redis.from_url(get_settings().redis_url, decode_responses=True)
            self.redis.ping()
        except Exception:
            self.redis = None

    async def create(self, workflow: Workflow):
        async with self.lock:
            self.workflows[workflow.id] = workflow
            self.events[workflow.id] = [Event(type="created", message="Workflow accepted")]
            if self.redis:
                self.redis.set(f"workflow:{workflow.id}", workflow.model_dump_json())
                self.redis.sadd("workflow_ids", workflow.id)
                self.redis.rpush(f"events:{workflow.id}", self.events[workflow.id][0].model_dump_json())
        return workflow

    async def get(self, workflow_id: str):
        if self.redis:
            raw = self.redis.get(f"workflow:{workflow_id}")
            return Workflow.model_validate_json(raw) if raw else None
        return self.workflows.get(workflow_id)

    async def update(self, workflow: Workflow):
        async with self.lock:
            self.workflows[workflow.id] = workflow
            if self.redis:
                self.redis.set(f"workflow:{workflow.id}", workflow.model_dump_json())
        return workflow

    async def add_event(self, workflow_id: str, event: Event):
        self.events.setdefault(workflow_id, []).append(event)
        if self.redis:
            self.redis.rpush(f"events:{workflow_id}", event.model_dump_json())

    async def list_events(self, workflow_id: str):
        if self.redis:
            return [Event.model_validate_json(raw) for raw in self.redis.lrange(f"events:{workflow_id}", 0, -1)]
        return self.events.get(workflow_id, [])

    async def list_workflows(self):
        if self.redis:
            ids = self.redis.smembers("workflow_ids")
            return [item for item in (await self._get_many(ids)) if item]
        return list(self.workflows.values())

    async def _get_many(self, ids):
        return [await self.get(item) for item in ids]

repository = WorkflowRepository()
