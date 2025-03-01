# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_compress import Compress

db = SQLAlchemy()
cache = Cache()
compress = Compress()