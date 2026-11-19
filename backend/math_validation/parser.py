"""The server entry points for bounded math parsing. Call outside DB transactions."""

from collections.abc import Sequence
from fractions import Fraction
import json
import os
from pathlib import Path
from queue import Empty, Queue
import subprocess
import sys
from threading import Thread
from time import monotonic

from .model import (
    BatchResult, LinearEquation, LinearExpression, ParseInput, ParseReason, ParseResult, ParseStatus, failed,
)
from .profiles import (
    BATCH_SECONDS, MAX_CHARS, MAX_RATIONAL_BITS, MAX_REQUEST_BYTES, MAX_STEPS, PROFILES,
)


# At most four rational terms. A decimal integer uses fewer characters
# than its bit length, plus a possible sign.
_MAX_FRAME_BYTES = 4 * (2 * MAX_RATIONAL_BITS + 3) + 256


def _worker_command() -> list[str]:
    worker = Path(__file__).with_name("_worker.py").resolve()
    return [sys.executable, "-I", "-S", "-B", str(worker)]


def _decode(item: ParseInput, line: bytes) -> ParseResult:
    frame = json.loads(line)
    if "reason" in frame:
        return failed(item, ParseReason(frame["reason"]))
    terms = [LinearExpression(Fraction(a), Fraction(b)) for a, b in frame["terms"]]
    if len(terms) == 1:
        value = terms[0]
    else:
        left, right = terms
        value = LinearEquation(left, right)
    return ParseResult(item.text, item.profile, ParseStatus.OK, value=value)


def _run_worker(items: list[ParseInput], batch_deadline: float) -> list[ParseResult]:
    payload = json.dumps([[item.text, item.profile] for item in items]).encode("ascii")
    queue: Queue[tuple[float, bytes] | None] = Queue()
    if batch_deadline <= monotonic():
        return [failed(item, ParseReason.WORKER_TIMEOUT) for item in items]

    # Give the worker only the Windows OS path if needed by CreateProcess.
    env = {"SystemRoot": os.environ["SystemRoot"]} if "SystemRoot" in os.environ else {}
    try:
        process = subprocess.Popen(
            _worker_command(), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, env=env,
        )
    except OSError:
        return [failed(item, ParseReason.WORKER_FAILURE) for item in items]

    stdin, stdout = process.stdin, process.stdout
    assert stdin is not None and stdout is not None

    def exchange() -> None:
        # Keep potentially blocking pipe I/O off the deadline-enforcing thread.
        # Killing this child closes its pipe ends and unblocks the exchange.
        try:
            with stdin:
                stdin.write(payload)
            for _ in items:
                line = stdout.readline(_MAX_FRAME_BYTES + 1)
                if not line.endswith(b"\n") or len(line) > _MAX_FRAME_BYTES:
                    break
                queue.put((monotonic(), line))
        except OSError:
            pass
        finally:
            queue.put(None)

    results = []
    reason = ParseReason.WORKER_FAILURE
    reader = Thread(target=exchange, name="math-parser-io")
    reader_started = False
    try:
        reader.start()
        reader_started = True
        for item in items:
            delivery = queue.get(timeout=max(0.0, batch_deadline - monotonic()))
            if delivery is None:
                break
            finished, line = delivery
            if finished >= batch_deadline:
                reason = ParseReason.WORKER_TIMEOUT
                break
            result = _decode(item, line)
            # Only the child can attest that normalization used its budget.
            if result.reason == ParseReason.TIMEOUT:
                reason = ParseReason.TIMEOUT
                break
            results.append(result)
    except Empty:
        reason = ParseReason.WORKER_TIMEOUT
    except (KeyError, TypeError, ValueError, ZeroDivisionError, RuntimeError):
        # Startup or protocol failure is a controlled abstention.
        pass
    finally:
        if process.poll() is None:
            process.kill()
        process.wait()
        if reader_started:
            reader.join()
        stdin.close()
        stdout.close()
    results.extend(failed(item, reason) for item in items[len(results):])
    return results


def parse_batch(items: Sequence[ParseInput]) -> BatchResult:
    """Parse ordered fields from one request, keeping the supplied strings intact.

    The HTTP caller also owns the cap on the full request body. Here the byte
    cap applies to the supplied expression text and profile IDs, in UTF-8.
    """
    batch_deadline = monotonic() + BATCH_SECONDS
    if len(items) > MAX_STEPS:
        return BatchResult(rejection=ParseReason.STEP_LIMIT)
    items = tuple(items)
    strings = [part for item in items for part in (item.text, item.profile) if part is not None]
    if (sum(map(len, strings)) > MAX_REQUEST_BYTES
            or sum(len(part.encode("utf-8", errors="surrogatepass")) for part in strings) > MAX_REQUEST_BYTES):
        return BatchResult(rejection=ParseReason.REQUEST_LIMIT)

    results = {}
    pending = {}
    for index, item in enumerate(items):
        if item.profile is None:
            results[index] = ParseResult(item.text, None, ParseStatus.NOT_REQUIRED)
        elif item.profile not in PROFILES:
            results[index] = failed(item, ParseReason.UNKNOWN_PROFILE)
        elif item.text is None:
            results[index] = failed(item, ParseReason.SYNTAX)
        elif len(item.text) > MAX_CHARS:
            results[index] = failed(item, ParseReason.LENGTH_LIMIT)
        else:
            pending[index] = item
    if pending:
        results.update(zip(pending, _run_worker(list(pending.values()), batch_deadline), strict=True))
    return BatchResult(tuple(results[index] for index in range(len(items))))


def parse_expression(text: str | None, profile: str | None) -> ParseResult:
    """Parse one field with the same resource and status contract as a batch."""
    item = ParseInput(text, profile)
    batch = parse_batch((item,))
    if batch.rejection is not None:
        return failed(item, batch.rejection)
    return batch.results[0]
