import sys
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

LOCAL_DEPENDENCIES = PROJECT_ROOT / ".deps"
if LOCAL_DEPENDENCIES.is_dir() and str(LOCAL_DEPENDENCIES) not in sys.path:
    sys.path.insert(0, str(LOCAL_DEPENDENCIES))

import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
