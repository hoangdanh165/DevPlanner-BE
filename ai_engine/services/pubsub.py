from __future__ import annotations
import json, time, logging
from enum import Enum
from dataclasses import dataclass
from typing import Protocol, Any, Optional

import redis
from django.conf import settings

logger = logging.getLogger(__name__)


class ProgressEvent(str, Enum):
    QUEUED = "queued"
    PART_UPLOADING = "part_uploading"
    PART_DONE = "part_done"
    COMPLETED = "completed"
    FAILED = "failed"
    INIT = "init"


class PublisherBackend(Protocol):
    def publish(self, channel: str, message: str) -> int: ...


@dataclass
class RedisBackend:
    client: redis.Redis

    def publish(self, channel: str, message: str) -> int:
        return self.client.publish(channel, message)


@dataclass
class ProgressPublisher:
    backend: PublisherBackend
    channel_prefix: str
    version: int = 1

    def _channel(self, project_id: str) -> str:
        return f"{self.channel_prefix}{project_id}"

    def _build_payload(self, project_id: str, event: str, data: dict) -> str:
        payload = {
            "v": self.version,
            "project_id": project_id,
            "event": event,
            "data": data,
            "ts": time.time(),
        }
        print("Publishing event:", payload)
        return json.dumps(payload)

    def publish(self, project_id: str, event: ProgressEvent | str, data: dict) -> None:
        # msg = self._build_payload(project_id, event.value, data)
        msg = self._build_payload(project_id, event, data)
        ch = self._channel(project_id)
        try:
            self.backend.publish(ch, msg)
        except Exception:
            logger.exception("Publish failed: channel=%s payload=%s", ch, msg)


_publisher_singleton: Optional[ProgressPublisher] = None


def get_default_publisher() -> ProgressPublisher:
    global _publisher_singleton
    if _publisher_singleton is None:
        client = redis.Redis.from_url(
            settings.REDIS_PS_URL,
            decode_responses=True,
            health_check_interval=30,
        )
        _publisher_singleton = ProgressPublisher(
            backend=RedisBackend(client),
            channel_prefix=settings.UPLOAD_PROGRESS_CHANNEL_PREFIX,
            version=1,
        )
    return _publisher_singleton


def save_ai_history(project, model_name, prompt, response, usage):
    from ai_engine.models import AIHistory

    AIHistory.objects.create(
        project=project,
        model_name=model_name,
        prompt=prompt,
        response=response,
        token_usage=usage,
        duration_ms=usage.get("duration_ms", 0),
    )
