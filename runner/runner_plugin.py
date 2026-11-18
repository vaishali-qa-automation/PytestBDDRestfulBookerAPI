"""
Custom pytest plugin: runner_plugin.py

Implements, as pytest hooks:
    1. Dynamic test selection by tags   -> pytest_collection_modifyitems
    2. Parallel execution support       -> relies on pytest-xdist (-n ...), this
                                            plugin only ensures its own hooks are
                                            xdist-safe (no protocol-level overrides)
    3. Logging of test results          -> pytest_runtest_logreport
    4. Retry on failure                 -> pytest_runtest_makereport (hookwrapper),
"""

import json
import logging
import os
import time

import pytest

root_logger = logging.getLogger()
_result_log_path = "reports/results.jsonl"

def pytest_addoption(parser):
    group = parser.getgroup("custom-runner")
    group.addoption("--tags", default=None)
    group.addoption("--exclude-tags", default=None)
    group.addoption("--retries", type=int, default=0)
    group.addoption("--result-log", default="reports/results.jsonl")

def pytest_configure(config):
    global _result_log_path
    _result_log_path = config.getoption("--result-log")

    config.addinivalue_line(
        "markers", "tags(*names): attach one or more custom tags to a test"
    )

    if hasattr(config, "workerinput"):
        return

    os.makedirs("reports", exist_ok=True)
    handler = logging.FileHandler("reports/runner.log", mode="w")
    handler.setFormatter(logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s"))
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter("%(levelname)s | %(name)s | %(message)s"))
    root_logger.addHandler(stream_handler)
    open(_result_log_path, "w").close()

# ---------------------------------------------------------------------------
# 1. Dynamic selection by tags
#    Works for BOTH:
#      - Gherkin @tag -> auto-converted by pytest-bdd into a plain marker
#      - plain pytest @pytest.mark.tags("x", "y") on regular test functions
# ---------------------------------------------------------------------------

def _csv_to_set(value):
    return {v.strip() for v in value.split(",")} if value else set()

def pytest_collection_modifyitems(config, items):
    include = _csv_to_set(config.getoption("--tags"))
    exclude = _csv_to_set(config.getoption("--exclude-tags"))
    if not include and not exclude:
        return

    selected, deselected = [], []
    for item in items:
        tags = {m.name for m in item.iter_markers()}
        tags |= {t for m in item.iter_markers("tags") for t in m.args}

        if include and not (tags & include):
            deselected.append(item)
        elif exclude and (tags & exclude):
            deselected.append(item)
        else:
            selected.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
    items[:] = selected

# ---------------------------------------------------------------------------
# 2. Retry on failure
#    Uses pytest_runtest_makereport (a reporting hookwrapper)
# ---------------------------------------------------------------------------

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    # Only act on the actual test body ("call" phase), not setup/teardown.
    if report.when != "call" or not report.failed:
        return

    max_retries = item.config.getoption("--retries")
    attempt = getattr(item, "_retry_attempt", 0)

    if attempt >= max_retries:
        report.user_properties.append(("attempts", attempt + 1))
        return

    item._retry_attempt = attempt + 1
    root_logger.warning(
        "RETRY %s (attempt %d/%d) after failure",
        item.nodeid, attempt + 1, max_retries
    )

    retry_call = pytest.CallInfo.from_call(lambda: item.runtest(), when="call")
    retry_report = item.ihook.pytest_runtest_makereport(item=item, call=retry_call)
    retry_report.user_properties.append(("attempts", attempt + 2))
    outcome.force_result(retry_report)

# ---------------------------------------------------------------------------
# 3. Logging results
# ---------------------------------------------------------------------------

def pytest_runtest_logreport(report):
    if report.when != "call" and report.passed:
        return

    attempts = dict(report.user_properties).get("attempts", 1)
    record = {
        "test": report.nodeid,
        "phase": report.when,
        "outcome": report.outcome,
        "duration_sec": round(report.duration, 4),
        "attempts": attempts,
        "error": report.longreprtext[-500:] if report.failed else None,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    root_logger.info("%s | %s | %.3fs | attempts=%d",
                record["outcome"].upper(), record["test"], report.duration, attempts)

    with open(_result_log_path, "a") as f:
        f.write(json.dumps(record) + "\n")

# ---------------------------------------------------------------------------
# Session summary (controller-only)
# ---------------------------------------------------------------------------

def pytest_sessionfinish(session, exitstatus):
    if hasattr(session.config, "workerinput"):
        return

    root_logger.info(f"Session finished with exit status {exitstatus}")

    path = session.config.getoption("--result-log")
    if not os.path.exists(path):
        return

    with open(path) as f:
        records = [json.loads(line) for line in f if line.strip()]

    passed = sum(1 for r in records if r["outcome"] == "passed")
    failed = sum(1 for r in records if r["outcome"] == "failed")
    total_time = sum(r["duration_sec"] for r in records)

    summary = (
        "\n--- Custom Runner Summary ---\n"
        f"Total: {len(records)} | Passed: {passed} | Failed: {failed}\n"
        f"Total duration: {total_time:.2f}s\n"
    )

    root_logger.info(summary)

    with open("reports/summary.txt", "w") as f:
        f.write(summary)