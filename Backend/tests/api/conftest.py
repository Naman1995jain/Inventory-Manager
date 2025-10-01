import sys, os
# Ensure parent tests directory is on sys.path so we can import its conftest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from conftest import *  # noqa: F401,F403
