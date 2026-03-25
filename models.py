class GpuOffer:
    def __init__(
        self,
        provider,
        offer_id,
        gpu_type,
        hourly_price,
        reliability,
        is_spot,
        region,
    ):
        self.provider = provider
        self.offer_id = offer_id
        self.gpu_type = gpu_type
        self.hourly_price = hourly_price
        self.reliability = reliability
        self.is_spot = is_spot
        self.region = region
        self.effective_hourly_cost = hourly_price
