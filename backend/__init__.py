"""Target persistence only; legacy Django remains the live writer until cutover."""


def load_tests(loader, standard_tests, pattern):
    """Keep root discovery in the legacy environment dependency-independent.

    unittest does not recurse into packages implementing this protocol. Only
    the dependency-independent discovery regressions belong in the legacy run.
    Run V01 explicitly with its locked dependencies and disposable PostgreSQL:
    python -m unittest backend.tests.test_unit backend.tests.test_postgres
                       backend.tests.test_remediation -v
    Explicit module loading does not use this package discovery hook.
    """
    return loader.suiteClass([
        standard_tests,
        loader.loadTestsFromName('backend.tests.test_discovery'),
    ])
