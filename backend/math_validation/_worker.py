"""Private entry point for an isolated interpreter. Stdin/stdout carry JSON."""

import json
from pathlib import Path
import sys
from time import process_time

# The parent launches this file with -I -S. Resolve imports from this
# checked-in path and keep ambient PYTHONPATH and site customization out.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.math_validation._normalize import normalize
from backend.math_validation.model import LinearEquation, ParseFailure, ParseReason
from backend.math_validation.profiles import EXPRESSION_SECONDS, PROFILES


def _parse(text, profile):
    deadline = process_time() + EXPRESSION_SECONDS

    # Parser loops run in Python; native integer operations have separate size caps.
    # Check during normalization as well as when its last operation returns.
    def check_budget(frame, event, arg):
        if process_time() >= deadline:
            raise ParseFailure(ParseReason.TIMEOUT)
        return check_budget

    sys.settrace(check_budget)
    try:
        return normalize(text, profile)
    finally:
        sys.settrace(None)
        if process_time() >= deadline:
            raise ParseFailure(ParseReason.TIMEOUT)


def main() -> None:
    for text, profile in json.load(sys.stdin.buffer):
        try:
            value = _parse(text, PROFILES[profile])
        except ParseFailure as error:
            result = {"reason": error.reason}
        else:
            sides = (value.left, value.right) if isinstance(value, LinearEquation) else (value,)
            result = {"terms": [[str(side.coefficient), str(side.constant)] for side in sides]}
        print(json.dumps(result), flush=True)
        if result.get("reason") == ParseReason.TIMEOUT:
            return


if __name__ == "__main__":
    main()
