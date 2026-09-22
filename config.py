import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://lfrqefxgfxochtqtmjgu.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "sb_publishable_iLGZfxO-ZeL-58QvCmbL-Q_OORUAIyF")
JWT_SECRET = os.environ.get("JWT_SECRET", "super_secret_key_footup_2026")
JWT_ALGORITHM = "HS256"