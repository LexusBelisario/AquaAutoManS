from functools import wraps
from flask_caching import Cache
import hashlib
import json

class CacheManager:
    def __init__(self, app):
        self.cache = Cache(app)

    def cached_with_key(self, timeout=300):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                cache_key = self._create_cache_key(f.__name__, args, kwargs)
                
                response = self.cache.get(cache_key)
                if response is not None:
                    return response
                
                response = f(*args, **kwargs)
                self.cache.set(cache_key, response, timeout=timeout)
                return response
            return decorated_function
        return decorator

    def _create_cache_key(self, func_name, args, kwargs):
        key_parts = [func_name]
        
        for arg in args:
            key_parts.append(str(arg))
            
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}:{value}")
            
        key_string = '_'.join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

class DataOptimizer:
    @staticmethod
    def optimize_query(query, limit=None, offset=None):
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
        return query

    @staticmethod
    def batch_process(items, batch_size=1000):
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]