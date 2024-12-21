from fastapi.templating import Jinja2Templates
from pathlib import Path

# Get the directory containing this file
current_dir = Path(__file__).parent
templates_dir = current_dir.parent / "templates"

# Create templates directory if it doesn't exist
templates_dir.mkdir(exist_ok=True)

# Initialize templates
templates = Jinja2Templates(directory=str(templates_dir))
