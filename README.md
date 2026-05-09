# Lilith Bot — Satellite 02 (Evil)

> *"I'd steal your dignity, but it seems someone already took it."*

A Discord bot based on **Lilith**, Vegapunk's Satellite 02 — the embodiment of Evil, mischief, and aggression.

## Commands

| Command | Description |
|---|---|
| `lilith steal @user` | Steal a random amount of gems from a user (logged in SQLite) |
| `lilith hoard` | Show the stolen gems leaderboard for this server |
| `lilith bounty @user <amount>` | Place a bounty on someone's head |
| `lilith bounties` | Show all active bounties in the server |
| `lilith taunt @user` | Deliver a devastating taunt |
| `lilith siblings` | List all six Vegapunk satellites |
| `lilith?` | Show the help menu with a select dropdown |

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/lilith-bot.git
cd lilith-bot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure your token
```bash
cp .env.example .env
```
Edit `.env` and paste your Discord bot token:
```
DISCORD_TOKEN=your_token_here
```

### 4. Run the bot
```bash
python bot.py
```

## Database

Lilith uses a local SQLite database (`lilith.db`) to store stolen goods and bounties. Created automatically on first run.

## Discord Developer Portal Setup

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. Create a new application named **Lilith**
3. Go to **Bot** → Create a bot
4. Under **Privileged Gateway Intents**, enable:
   - **Message Content Intent**
   - **Server Members Intent**
5. Copy the token into your `.env`
6. Under **OAuth2 → URL Generator**, select `bot` scope and the following permissions:
   - Send Messages, Embed Links, Read Message History, View Channels

## Cross-bot Awareness

Lilith reacts when sibling satellite names are mentioned in chat (Shaka, Edison, Pythagoras, Atlas, York). For full cross-bot awareness, run all 6 satellite bots in the same server.
