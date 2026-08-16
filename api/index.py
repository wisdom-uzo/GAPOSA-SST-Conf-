import os
import sys

# Ensure the root project directory is in the sys.path for Vercel Serverless runtime
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import create_app
from config import Config

# Expose 'app' WSGI entrypoint for Vercel
app = create_app(Config)
