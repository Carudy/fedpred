import os
from pathlib import Path

BASE_PATH = Path(os.path.realpath(__file__)).parent.parent
LOG_PATH = BASE_PATH / 'info.log'
