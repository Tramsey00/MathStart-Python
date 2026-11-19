"""R02 profile IDs and the v1 parser budgets from learning requirements §9."""

from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True, slots=True)
class Profile:
    linear: bool


PROFILES = MappingProxyType({
    "arithmetic_v1": Profile(linear=False),
    "algebra_scalar_v1": Profile(linear=False),
    "probability_fraction_v1": Profile(linear=False),
    "algebra_linear_v1": Profile(linear=True),
})

MAX_REQUEST_BYTES = 64 * 1024
MAX_STEPS = 40
MAX_CHARS = 512
MAX_TOKENS = 128
MAX_NESTING = 16
MAX_LITERAL_DIGITS = 12
MAX_ABS_POWER = 10
EXPRESSION_SECONDS = 0.250
BATCH_SECONDS = 2.0

# Four bits cover each decimal digit. Bound intermediate numerator and
# denominator growth, including repeated powers of already computed values.
MAX_RATIONAL_BITS = MAX_TOKENS * MAX_LITERAL_DIGITS * 4
