import json
import os
import time
import hashlib
from dataclasses import dataclass
from typing import Optional, Dict, Any

import requests

from settings import MAX_ACTIVE_JOBS, LAUNCH_TIMEOUT_SEC


LAUNCH_STATE_FILE = "launch_state.json"


@dataclass
class LaunchResult:
    ok: bool
    provider: str
    launch_id: Optional[str] = None
    status: str = "unknown"
    error: Optional[str] = None
    request_payload: Optional[Dict[str, Any]] = None
    raw_response: Optional[Dict[str, Any]] = None


def load_launch_state() -> Dict[str, Any]:
    if not os.path.exists(LAUNCH_STATE_FILE):
        return {"active": {}, "history": []}
    try:
        with open(LAUNCH_STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"active": {}, "history": []}


def save_launch_state(state: Dict[str, Any]) -> None:
    with open(LAUNCH_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def make_job_key(job, offer) -> str:
    raw = f"{job.job_id}|{job.gpu_type}|{offer.provider}|{offer.offer_id}|{job.sell_price}"
    return hashlib.sha256(raw.encode()).hexdigest()[:24]


def active_count(state: Dict[str, Any]) -> int:
    return len(state.get("active", {}))


def already_active(state: Dict[str, Any], job_key: str) -> bool:
    return job_key in state.get("active", {})


class RenderLauncher:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url

    def enabled(self) -> bool:
        return bool(self.api_key and self.base_url)

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def build_launch_payload(self, job, offer):
        return {
            "name": f"arb-{job.job_id}",
            "gpu_type": offer.gpu_type,
            "gpu_count": job.gpu_count,
            "machine_offer_id": offer.offer_id,
            "docker_image": job.docker_image,
            "command": job.command,
            "env": job.env,
            "disk_gb": job.disk_gb,
            "spot": offer.is_spot,
            "region": offer.region,
            "metadata": {
                "job_id": job.job_id,
                "expected_revenue_usd": job.sell_price,
                "expected_cost_usd": round(job.total_cost, 4),
                "expected_profit_usd": round(job.profit_usd, 4),
            },
        }

    def launch(self, job, offer):
        if not self.enabled():
            return LaunchResult(
                ok=False,
                provider="render",
                error="RENDER_API_KEY or RENDER_API_BASE missing",
            )

        payload = self.build_launch_payload(job, offer)

        try:
            resp = requests.post(
                f"{self.base_url}/instances",
                headers=self._headers(),
                json=payload,
                timeout=LAUNCH_TIMEOUT_SEC,
            )

            try:
                raw = resp.json()
            except Exception:
                raw = {"text": resp.text}

            if 200 <= resp.status_code < 300:
                launch_id = raw.get("id") or raw.get("instance_id") or raw.get("machine_id")
                status = raw.get("status", "submitted")
                return LaunchResult(
                    ok=True,
                    provider="render",
                    launch_id=launch_id,
                    status=status,
                    request_payload=payload,
                    raw_response=raw,
                )

            return LaunchResult(
                ok=False,
                provider="render",
                error=f"HTTP {resp.status_code}",
                request_payload=payload,
                raw_response=raw,
            )

        except Exception as e:
            return LaunchResult(
                ok=False,
                provider="render",
                error=str(e),
                request_payload=payload,
            )


def maybe_launch_job(job, offer, launcher, dry_run=False):
    state = load_launch_state()
    job_key = make_job_key(job, offer)

    if already_active(state, job_key):
        return LaunchResult(
            ok=False,
            provider=offer.provider,
            status="skipped_duplicate",
            error=f"already active: {job_key}",
        )

    if active_count(state) >= MAX_ACTIVE_JOBS:
        return LaunchResult(
            ok=False,
            provider=offer.provider,
            status="max_active_reached",
            error=f"active limit reached ({MAX_ACTIVE_JOBS})",
        )

    if dry_run:
        return LaunchResult(
            ok=True,
            provider=offer.provider,
            status="dry_run_ready",
            request_payload=launcher.build_launch_payload(job, offer),
        )

    result = launcher.launch(job, offer)

    event = {
        "ts": int(time.time()),
        "job_id": job.job_id,
        "job_key": job_key,
        "gpu_type": offer.gpu_type,
        "offer_id": offer.offer_id,
        "provider": offer.provider,
        "sell_price": job.sell_price,
        "total_cost": job.total_cost,
        "profit_usd": job.profit_usd,
        "launch_ok": result.ok,
        "launch_id": result.launch_id,
        "status": result.status,
        "error": result.error,
    }

    state.setdefault("history", []).append(event)

    if result.ok:
        state.setdefault("active", {})[job_key] = {
            "ts": int(time.time()),
            "job_id": job.job_id,
            "launch_id": result.launch_id,
            "provider": result.provider,
            "offer_id": offer.offer_id,
            "gpu_type": offer.gpu_type,
            "profit_usd": job.profit_usd,
            "status": result.status,
        }

    save_launch_state(state)
    return result
