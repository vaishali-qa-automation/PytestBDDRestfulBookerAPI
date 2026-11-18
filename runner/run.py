"""
Custom test runner entry point.
Wraps pytest invocation so this can be run as: python -m runner.run --tags smoke -n auto
"""
import sys
import pytest

def main():
    args = sys.argv[1:] or ["tests/"]
    exit_code = pytest.main(args)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()