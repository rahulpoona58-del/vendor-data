import os
import sys

# Configure writable matplotlib config directory for serverless environment
os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib'

# Ensure project root directory is in Python path for Vercel Serverless Function imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import app
