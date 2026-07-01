"""Queue consumer — generates realistic suspicious + clean transaction mix."""
import asyncio, uuid, random
from datetime import datetime
from .aml_scorer import score_transaction
from .graph_builder import add_transaction

_queue: asyncio.Queue = asyncio.Queue(maxsize=10_000)
_running = False

SAMPLE_ACCOUNTS = [
    "ACC-4421","ACC-9823","ACC-3317","ACC-7701","ACC-2209",
    "ACC-6612","ACC-0094","ACC-8801","ACC-2234","ACC-5512",
]

def _random_tx():
    r = random.random()
    if r < 0.25:
        amt = round(random.uniform(900_000, 2_000_000), 2)
        orig, dest = "US", random.choice(["CY","SG","AE","CH"])
    elif r < 0.40:
        amt = round(random.uniform(7_500, 9_900), 2)
        orig = dest = "US"
    elif r < 0.55:
        amt = round(random.uniform(300_000, 800_000), 2)
        orig, dest = "DE", random.choice(["CY","SG"])
    else:
        amt = round(random.uniform(500, 40_000), 2)
        orig = dest = random.choice(["US","DE","UK"])
    return {
        "tx_id":          str(uuid.uuid4()),
        "from_account":   random.choice(SAMPLE_ACCOUNTS),
        "to_account":     random.choice(SAMPLE_ACCOUNTS),
        "amount":         amt,
        "currency":       "USD",
        "timestamp":      datetime.utcnow(),
        "country_origin": orig,
        "country_dest":   dest,
    }

async def enqueue(tx: dict) -> None:
    await _queue.put(tx)

async def _synthetic_producer() -> None:
    await asyncio.sleep(1.0)
    while _running:
        await _queue.put(_random_tx())
        await asyncio.sleep(random.uniform(0.3, 0.7))

async def _worker() -> None:
    from backend.api.websocket import broadcast
    while _running:
        try:
            tx = await asyncio.wait_for(_queue.get(), timeout=1.0)
            result = await score_transaction(tx)
            add_transaction(tx["from_account"], tx["to_account"],
                            tx["amount"], result["risk_level"])
            await broadcast({
                "tx_id":        tx["tx_id"],
                "from_account": tx["from_account"],
                "to_account":   tx["to_account"],
                "amount":       tx["amount"],
                "risk_score":   result["risk_score"],
                "risk_level":   result["risk_level"],
                "flagged":      result["flagged"],
                "pattern_tags": result["pattern_tags"],
                "latency_ms":   result["latency_ms"],
                "timestamp":    str(tx["timestamp"]),
            })
            _queue.task_done()
        except asyncio.TimeoutError:
            continue
        except Exception as e:
            print(f"[QueueWorker] Error: {e}")

async def start(num_workers: int = 2) -> None:
    global _running
    _running = True
    asyncio.create_task(_synthetic_producer())
    for _ in range(num_workers):
        asyncio.create_task(_worker())
    print(f"[Queue] Started {num_workers} async workers + synthetic producer")

async def stop() -> None:
    global _running
    _running = False
