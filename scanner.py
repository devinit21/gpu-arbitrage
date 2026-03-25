from providers.vast import get_vast_offers
from jobs_config import JOBS
from gpu_arbitrage import evaluate_job
launch_result = maybe_launch_job(job, best_offer, launcher, dry_run=True)
from settings import RENDER_API_KEY, RENDER_API_BASE


def run_scanner():
    print("=== SCAN START ===")

    offers = get_vast_offers()

    launcher = RenderLauncher(
        api_key=RENDER_API_KEY,
        base_url=RENDER_API_BASE,
    )

    for job in JOBS:
        best_offer = None
        best_profit = -999

        for offer in offers:
            result = evaluate_job(job, offer)

            if not result["run"]:
                continue

            if result["profit"] > best_profit:
                best_profit = result["profit"]
                best_offer = offer
                job.total_cost = result["cost"]
                job.profit_usd = result["profit"]
                job.sell_price = result["sell_price"]

        if best_offer:
            print(f"[RUN JOB] {job.job_id} -> {best_offer.gpu_type} profit=${job.profit_usd:.2f}")

            launch_result = maybe_launch_job(job, best_offer, launcher)

            if launch_result.ok:
                print(f"[LAUNCHED] {launch_result.launch_id}")
            else:
                print(f"[FAILED] {launch_result.error}")
        else:
            print(f"[SKIP JOB] {job.job_id}")

    print("=== SCAN END ===")
