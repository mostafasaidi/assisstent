# Quick Setup Instructions for Cal.com Integration

## Prerequisites
1. Cal.com account with API access (paid plan required)
2. Telegram bot token
3. Groq API key

## Setup Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create/update your `.env` file:

```env
# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_USER_ID=your_telegram_user_id

# Cal.com Configuration  
CALCOM_API_KEY=cal_live_xxxxxxxxxxxxx
CALCOM_API_URL=https://api.cal.com/v1

# Groq AI Configuration
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
```

### 3. Get Your Cal.com API Key

1. Log in to Cal.com: https://app.cal.com
2. Go to Settings → Developer → API Keys
3. Click "Create New API Key"
4. Copy the key and add it to `.env`

### 4. Get Your Event Type ID (Important!)

1. Go to https://app.cal.com/event-types
2. Click on the event type you want to use
3. Look at the URL: `/event-types/[ID]`
4. Edit `calendar_manager.py` line ~34:
   ```python
   "eventTypeId": YOUR_ID_HERE,  # Replace with your actual event type ID
   ```

### 5. Run the Bot
```bash
python bot.py
```

## Quick Test

Once the bot is running, send it a message on Telegram:
- "Schedule a meeting tomorrow at 2pm"
- "/today" to see today's events
- "/upcoming" to see upcoming bookings

## Common Issues

### "Calendar features are disabled"
- Check that `CALCOM_API_KEY` is set in `.env`
- Verify the API key is valid
- Restart the bot after updating `.env`

### "API error: 401"
- Your API key is invalid or expired
- Generate a new key from Cal.com

### "API error: 403"
- Your Cal.com plan doesn't include API access
- Upgrade to a paid plan

### "API error: 404"
- Check your event type ID
- Make sure the event type exists in your account

## Need More Help?

See `MIGRATION_GUIDE.md` for detailed information.
See `README.md` for full documentation.

## Support Links
- Cal.com API Docs: https://cal.com/docs/api-reference
- Groq Console: https://console.groq.com
- Telegram Bot API: https://core.telegram.org/bots
