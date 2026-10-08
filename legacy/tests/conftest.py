import sys
from pathlib import Path

# the parity modules are scripts, not an installed package
sys.path.insert(0, str(Path(__file__).parents[1] / 'parity'))
