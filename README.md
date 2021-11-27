This is a small Discord bot made with discord.py, used on the guild HoQ, and guilds related to it

The original repo file also includes a decompressed static build for FFMPEG, which the bot uses for playing audio.

Currently, the bot can:
* Set AFK messages
* Show Google search results for images and gifs
* Show information about a user
* Show information about a guild (commonly called *server*)
* Carry out moderation functions, like kicking, banning, unbanning, warning users, etc.
* Return edited and deleted messages
* Search for xkcd comics
* ...
* And more

Future plans:
- [ ] Create a systematic approach to handling slash commands
- [X] Add a loop to retrieve data automatically
- [ ] Create a game of hangman
- [ ] Implement a queue for music

Due to the limitations provided by the original "host" (aka Replit), the bot does not access any external database for storage, but stores its data in json files, the examples of which can be found [here](https://github.com/baron-ghost-i/HoQ-Bot/tree/master/data). The data will be regularly accessed to ensure that it is not lost when restarting the bot.

The bot is not available publicly (owing to the limitations it still suffers from).