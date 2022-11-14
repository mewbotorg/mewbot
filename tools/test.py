#!/usr/bin/env python3

from __future__ import annotations

from mewbot_tests import parse_test_options, TestToolchain


if __name__ == "__main__":
    options = parse_test_options()

    testing = TestToolchain(in_ci=options.is_ci)
    testing.coverage = options.coverage
    testing()
