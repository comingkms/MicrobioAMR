def pytest_report_teststatus(report, config):
    """Customize pytest verbose PASSED output."""
    if report.when == "call" and report.passed:
        return "passed", ".", "PASSED\n=================================================================================="
