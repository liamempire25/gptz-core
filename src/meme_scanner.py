import os, httpx, datetime

class MemeScanner:
    def __init__(self, db, bw):
        self.db = db
        self.bw = bw
        # Configurable endpoints:
        self.dex_api = os.getenv("DEX_API_URL", "https://api.dexscreener.com/latest/dex/pairs")

    async def scan_once(self):
        hits = []
        async with httpx.AsyncClient(timeout=20) as client:
            try:
                resp = await client.get(self.dex_api)
                data = resp.json()
                pairs = data.get("pairs", [])[:200]
                for p in pairs:
                    score = self.score_pair(p)
                    if score >= int(os.getenv("AUTO_EXECUTE_THRESHOLD_SCORE","9")):
                        hits.append({"pair": p, "score": score})
                        await self.db.log_event("meme_hit", {"pair": p, "score": score})
            except Exception as e:
                await self.db.log_event("meme_scan_error", {"error": str(e)})
        return hits

    def score_pair(self, p):
        # basic heuristic (customize)
        score = 0
        vol = p.get("priceChange", 0)  # placeholder, adapt to real API fields
        liquidity = p.get("liquidity", 0)
        age = p.get("age_minutes", 9999)
        if vol and float(vol) > 50: score += 3
        if liquidity and float(liquidity) > 10000: score += 2
        if age < 60: score += 2
        # social & other checks - to be added
        return score
