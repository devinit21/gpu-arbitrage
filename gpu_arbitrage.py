from settings import MIN_PROFIT_USD, PROFIT_MULTIPLIER


def gpu_matches(job_gpu: str, offer_gpu: str) -> bool:
    job_gpu = job_gpu.lower()
    offer_gpu = offer_gpu.lower()

    if job_gpu in offer_gpu:
        return True

    aliases = {
        "rtx 3060 ti": ["3060 ti", "rtx 3060ti"],
        "rtx 3090": ["3090", "rtx3090"],
        "rtx 4090": ["4090", "rtx4090"],
    }

    for canonical, variants in aliases.items():
        if job_gpu == canonical and any(v in offer_gpu for v in variants):
            return True

    return False


def evaluate_job(job, offer):
    if not gpu_matches(job.gpu_type, offer.gpu_type):
        return {
            "run": False,
            "profit": -999.0,
            "cost": 0.0,
            "sell_price": job.sell_price,
        }

    effective_rate = offer.effective_hourly_cost or offer.hourly_price
    total_cost = effective_rate * job.expected_runtime_hours * job.gpu_count
    profit = job.sell_price - total_cost

    passes_floor = profit >= MIN_PROFIT_USD
    passes_multiplier = job.sell_price >= (total_cost * PROFIT_MULTIPLIER)

    return {
        "run": passes_floor and passes_multiplier,
        "profit": profit,
        "cost": total_cost,
        "sell_price": job.sell_price,
    }
