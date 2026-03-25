import requests
from models import GpuOffer


VAST_API_URL = "https://vast.ai/api/v0/bundles"


def get_vast_offers():
    offers = []

    try:
        resp = requests.get(VAST_API_URL, timeout=10)
        data = resp.json()

        for item in data.get("offers", []):
            try:
                gpu_name = item.get("gpu_name", "")
                dph = float(item.get("dph_total", 0))  # dollars per hour

                offer = GpuOffer(
                    provider="vast",
                    offer_id=str(item.get("id")),
                    gpu_type=gpu_name,
                    hourly_price=dph,
                    reliability=0.95,  # placeholder
                    is_spot=False,
                    region=item.get("geolocation", "unknown"),
                )

                # 🔥 YOUR EFFECTIVE COST LOGIC (IMPORTANT)
                offer.effective_hourly_cost = (
                    offer.hourly_price
                    + 0.03   # failure penalty
                    + 0.01   # startup
                    + 0.01   # transfer
                    + (0.03 if offer.is_spot else 0)
                    + (1 - offer.reliability) * 0.05
                )

                offers.append(offer)

            except Exception:
                continue

    except Exception as e:
        print(f"[VAST ERROR] {e}")

    return offers
