
### Why am I getting blank events when messages are sent in channels the bot is monitoring?

As of late August 2022, discord bots now need the message content permission to be explicitly enabled (was implicitly enabled up to this point).
If this scope is not enabled all the messages will have null message content.
Enable the scope for the token via the developer portal and things should start working again.

### Pycord is not seeing events I expect it to

If you have enabled the appropiate scope for your bot via the developer token, and you are still not getting input events, you may need to update the intents in the __init__ of DiscordInput.
Currently they are set to `all` - but something might have altered here.

