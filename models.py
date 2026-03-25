from dataclasses import dataclass, field
from typing import Dict


@dataclass
class GpuOffer:
    provider: str
    offer_id: str
    gpu_type: str
    hourly_price: float
    reliability: float = 0.95
    is_spot: bool = False
    region: str = "unknown"
    effective_hourly_cost: float = 0.0


@dataclass
class JobSpec:
    job_id: str
    gpu_type: str
    expected_runtime_hours: float
    sell_price: float
    docker_image: str
    command: str
    gpu_count: int = 1
    env: Dict[str, str] = field(default_factory=dict)
    disk_gb: int = 30

    total_cost: float = 0.0
    profit_usd: float = 0.0
