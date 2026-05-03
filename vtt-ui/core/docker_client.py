# =============================================================================
# VTT-Node | vtt-ui/core/docker_client.py
# Docker SDK wrapper — safe interface to /var/run/docker.sock
# =============================================================================

import docker
import docker.errors
from typing import Optional
from core.config import settings


class DockerClient:
    def __init__(self):
        self._client: Optional[docker.DockerClient] = None

    def connect(self):
        try:
            self._client = docker.from_env()
            self._client.ping()
        except Exception as e:
            print(f"[VTT-Node] WARNING: Docker socket connection failed: {e}")
            self._client = None

    def disconnect(self):
        if self._client:
            self._client.close()

    @property
    def client(self) -> docker.DockerClient:
        if not self._client:
            self.connect()
        if not self._client:
            raise RuntimeError("Docker socket unavailable. Is /var/run/docker.sock mounted?")
        return self._client

    def get_vtt_container(self):
        return self.client.containers.get(settings.container_name)

    def get_container_stats(self) -> dict:
        container = self.get_vtt_container()
        stats = container.stats(stream=False)
        cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - stats["precpu_stats"]["cpu_usage"]["total_usage"]
        system_delta = stats["cpu_stats"]["system_cpu_usage"] - stats["precpu_stats"]["system_cpu_usage"]
        num_cpus = stats["cpu_stats"].get("online_cpus") or len(stats["cpu_stats"]["cpu_usage"].get("percpu_usage", [1]))
        cpu_percent = (cpu_delta / system_delta) * num_cpus * 100.0 if system_delta > 0 else 0.0
        mem_usage = stats["memory_stats"].get("usage", 0)
        mem_limit = stats["memory_stats"].get("limit", 1)
        cache = stats["memory_stats"].get("stats", {}).get("cache", 0)
        mem_actual = max(0, mem_usage - cache)
        return {"cpu_percent": round(cpu_percent, 2), "memory_usage_mb": round(mem_actual / (1024 ** 2), 1), "memory_limit_mb": round(mem_limit / (1024 ** 2), 1), "memory_percent": round((mem_actual / mem_limit) * 100, 2) if mem_limit > 0 else 0}

    def get_container_info(self) -> dict:
        container = self.get_vtt_container()
        state = container.attrs.get("State", {})
        config = container.attrs.get("Config", {})
        return {"name": settings.container_name, "engine": settings.vtt_engine, "status": state.get("Status", "unknown"), "running": state.get("Running", False), "started_at": state.get("StartedAt"), "image": config.get("Image", "unknown"), "health": state.get("Health", {}).get("Status", "none")}

    def restart_container(self, timeout: int = 10):
        self.get_vtt_container().restart(timeout=timeout)


docker_client = DockerClient()
