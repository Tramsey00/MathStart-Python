"""R04 required-check identifiers shared by manifest and runtime."""

REPO_BASELINE = "repo-baseline"
HARNESS_UNIT = "harness-unit"
HARNESS_CLI_SMOKE = "harness-cli-smoke"

KNOWN_CHECKS = frozenset({
    REPO_BASELINE,
    HARNESS_UNIT,
    HARNESS_CLI_SMOKE,
})
