import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings

print(f"DATABASE_URL: {settings.DATABASE_URL}")

from app.core.database import engine

try:
    connection = engine.connect()

    print("✅ Database connecté avec succès")

    connection.close()

except Exception as e:
    print("❌ Erreur connexion DB")
    import traceback
    traceback.print_exc()
