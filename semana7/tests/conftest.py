import sys
import os
from pathlib import Path

# Add the parent directory to Python path so we can import 'app' module
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Optional: Add the app directory specifically
app_dir = project_root / "app"
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))
