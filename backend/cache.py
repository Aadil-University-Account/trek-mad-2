import json
import redis
from flask import jsonify

# Redis database 1 is used for caching (database 0 is used by Celery)
r = redis.Redis(host="localhost", port=6379, db=1, decode_responses=True)

CACHE_SECONDS = 60  # cache expiry: data is refreshed from the database after 60 seconds


def cached_response(key, build_data, ttl=CACHE_SECONDS):
    """Return JSON from Redis if present, otherwise build it, store it and return it.
    The header X-Cache tells if it was a HIT or a MISS (useful in the demo).
    If Redis is down the app still works (it just reads from the database)."""
    data = None
    try:
        text = r.get(key)
        if text:
            data = json.loads(text)
    except redis.RedisError:
        pass

    hit = data is not None
    if not hit:
        data = build_data()
        try:
            r.setex(key, ttl, json.dumps(data))
        except redis.RedisError:
            pass

    response = jsonify(data)
    response.headers["X-Cache"] = "HIT" if hit else "MISS"
    return response


def clear_trek_cache():
    """Call this whenever treks / slots / bookings change, so users never see old data."""
    try:
        for key in r.scan_iter("trek*"):
            r.delete(key)
        r.delete("public:stats")
    except redis.RedisError:
        pass
        