# app/config.py
class Config:
    # Existing configuration
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/dbserial'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Enhanced database configuration
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,  # Increased pool size
        'pool_recycle': 1800,  # Recycle connections after 30 minutes
        'pool_pre_ping': True,
        'max_overflow': 10,
        'pool_timeout': 30
    }
    
    # Enhanced caching configuration
    CACHE_TYPE = 'redis'  # Using Redis instead of simple cache
    CACHE_REDIS_URL = 'redis://localhost:6379/0'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Rate limiting
    RATELIMIT_DEFAULT = "200 per day;50 per hour;1 per second"
    
    # Compression
    COMPRESS_MIMETYPES = ['text/html', 'text/css', 'text/xml', 'application/json']
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500