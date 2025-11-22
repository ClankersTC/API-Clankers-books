from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.coder import PickleCoder

async def init_cache():
    FastAPICache.init(
        backend = InMemoryBackend(), 
        prefix = "Clankers_API_Cache",
        coder = PickleCoder
    )

def book_key_builder(
    func,
    namespace: str = "",
    request = None,
    response = None,
    *args,
    **kwargs
):    
    prefix = namespace if namespace else "Clankers_API_Cache"

    item_id = kwargs.get("kwargs", {}).get("libro_id") or kwargs.get("kwargs",{}).get("id")

    return f"{prefix}:{item_id}"