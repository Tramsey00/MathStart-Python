"""Private entry point for an isolated interpreter. Stdin/stdout carry JSON."""

import json
from pathlib import Path
import sys
from time import monotonic

# The parent launches this file with -I -S. Resolve imports from this
# checked-in path and keep ambient PYTHONPATH and site customization out.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.math_validation._normalize import normalize
from backend.math_validation.model import LinearEquation, ParseFailure, ParseReason
from backend.math_validation.profiles import EXPRESSION_SECONDS, PROFILES


def main() -> None:
    for text, profile in json.load(sys.stdin.buffer):
        started = monotonic()
        try:
            value = normalize(text, PROFILES[profile])
        except ParseFailure as error:
            result = {"reason": error.reason}
        else:
            sides = (value.left, value.right) if isinstance(value, LinearEquation) else (value,)
            result = {"terms": [[str(side.coefficient), str(side.constant)] for side in sides]}
        if monotonic() - started >= EXPRESSION_SECONDS:
            print(json.dumps({"reason": ParseReason.TIMEOUT}), flush=True)
            return
        print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
