<!--
SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>

SPDX-License-Identifier: BSD-2-Clause
-->

Bandit produces errors of three different levels of severity, with three different levels of confidence.
Capturing and parsing these blocks into github annotations.

Here is an example of typical bandit output - which must then be parsed into a useful format.

```shell

Run started:2023-06-22 21:49:31.662238

Test results:
>> Issue: [B404:blacklist] Consider possible security implications associated with the subprocess module.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.7.5/blacklists/blacklist_imports.html#b404-import-subprocess
   Location: src\mewbot\io\desktop_notification.py:18:0
17      import sys
18      import subprocess
19

--------------------------------------------------
>> Issue: [B101:assert_used] Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.
   Severity: Low   Confidence: High
   CWE: CWE-703 (https://cwe.mitre.org/data/definitions/703.html)
   More Info: https://bandit.readthedocs.io/en/1.7.5/plugins/b101_assert_used.html
   Location: src\mewbot\io\desktop_notification.py:251:8
250                 return
251             assert ToastNotifier is not None
252

--------------------------------------------------

Code scanned:
        Total lines of code: 3515
        Total lines skipped (#nosec): 0

Run metrics:
        Total issues (by severity):
                Undefined: 0
                Low: 2
                Medium: 0
                High: 0
        Total issues (by confidence):
                Undefined: 0
                Low: 0
                Medium: 0
                High: 2
Files skipped (0):

```