<!--
SPDX-FileCopyrightText: 2023 Mewbot Developers <mewbot@quicksilver.london>

SPDX-License-Identifier: BSD-2-Clause
-->

## Final steps

### 15) Test an example actually works

For the example below, it's a case of "bring your own token" - instructions as to how to generate tokens for each of the supported services are located elsewhere in this documentation.

None of the `discord` examples have functional tokens. 
You might want to try `rss_input.yaml` - but it's less of a demonstration of capability than the one below.

Execute something like

```shell
(mewbot_venv) C:\mewbot_dev\mewbot>python -m examples examples\discord_to_desktop_notification.yaml
```

with the paths replaced as appropriate for your setup and the example replaced with the example you actually want to run (though the desktop notificaiton example is perfectly inoffensive).

### 16) Proceed with dev

With everything built, installed and tested you should be ready to proceed with dev.

Some tips
* It's a good idea to regularly `lint` and `test` the code base - this stops the number of errors from getting out of hand
* Checking `test --cov` from time to time also can help you build tests as you go along

While you're working on a feature, it's not vital that _every_ commit passes testing or linting.
However, if you could run the `preflight` tool before issuing a pull request, that'd be good.
`preflight` is intended to be a tool you can run one final time before commiting.

Naturally, things can go wrong.
But if your files pass `preflight`, you should be able to commit them in the _reasonable_ hope that they will pass the remote checks as well.



