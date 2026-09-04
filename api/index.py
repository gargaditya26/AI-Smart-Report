import os
import sys

# Keep the existing backend source tree intact while exposing FastAPI through
# Vercel's /api Python entrypoint.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(ROOT, "backend")
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

from main import app  # noqa: E402
