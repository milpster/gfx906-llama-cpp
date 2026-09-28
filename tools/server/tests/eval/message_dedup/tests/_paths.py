"""sys.path and fixture helpers shared by the SPEC-0001 increment-14 suite tests."""
import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUITE_DIR = HERE.parent                      # tools/server/tests/eval/message_dedup
SERVER_TESTS_DIR = SUITE_DIR.parents[1]      # tools/server/tests
FIXTURES = HERE / "fixtures"

for p in (str(SERVER_TESTS_DIR), str(SUITE_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)


def load(name: str) -> dict:
    """A deep copy of one hand-made mini scenario fixture (synthetic)."""
    with open(FIXTURES / name, encoding="utf-8") as f:
        return copy.deepcopy(json.load(f))
