import json


def save_snapshot(offers, decisions, path="scan_snapshot.json"):
    serializable_offers = []
    for offer in offers:
        serializable_offers.append({
            "provider": offer.provider,
            "offer_id": offer.offer_id,
            "gpu_type": offer.gpu_type,
            "hourly_price": offer.hourly_price,
            "effective_hourly_cost": offer.effective_hourly_cost,
            "reliability": offer.reliability,
            "is_spot": offer.is_spot,
            "region": offer.region,
        })

    payload = {
        "offers": serializable_offers,
        "decisions": decisions,
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
