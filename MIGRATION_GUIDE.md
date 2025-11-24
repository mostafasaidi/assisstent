# Migration Guide: Google Calendar to Cal.com

This guide will help you migrate from Google Calendar to Cal.com integration.

## What Changed

### 1. Calendar Integration
- **Before:** Used Google Calendar API with OAuth authentication
- **After:** Uses Cal.com REST API with API key authentication

### 2. Dependencies
- **Removed:** 
  - `google-auth`
  - `google-auth-oauthlib`
  - `google-auth-httplib2`
  - `google-api-python-client`
  
- **Added:**
  - `requests` (for HTTP API calls)

### 3. Configuration
- **Removed:**
  - `credentials.json` file
  - `token.json` file
  - Google OAuth flow
  
- **Added:**
  - `CALCOM_API_KEY` in `.env` file
  - `CALCOM_API_URL` in `.env` file (defaults to https://api.cal.com/v1)

## Migration Steps

### Step 1: Update Dependencies

```bash
pip uninstall google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
pip install -r requirements.txt
```

### Step 2: Get Cal.com API Key

1. Go to https://app.cal.com/settings/developer/api-keys
2. Create a new API key
3. Copy the generated key

**Note:** Cal.com API requires a paid subscription. You may need to upgrade your account.

### Step 3: Update .env File

Remove Google/OpenAI related variables and add:

```env
CALCOM_API_KEY=cal_live_xxxxxxxxxxxxx
CALCOM_API_URL=https://api.cal.com/v1
```

### Step 4: Remove Old Files

You can safely delete:
- `credentials.json`
- `token.json`

### Step 5: Restart the Bot

```bash
python bot.py
```

## Important Notes

### Cal.com API Limitations

1. **Paid Feature:** Cal.com API access requires a paid subscription
2. **Rate Limits:** Be aware of API rate limits on your plan
3. **Event Types:** You'll need to configure event types in Cal.com dashboard

### Differences from Google Calendar

1. **Booking-Centric:** Cal.com is designed around bookings, not generic events
2. **Event Types Required:** Events are created through event types
3. **Different Data Structure:** Booking objects differ from calendar events

### Troubleshooting

**Issue:** "Cal.com API authentication failed"
- Verify your API key is correct
- Check that your Cal.com subscription includes API access
- Ensure the API key hasn't been revoked

**Issue:** "Cannot create bookings"
- You need to have event types configured in Cal.com
- Check the `eventTypeId` in `calendar_manager.py` and update it with your actual event type ID

**Issue:** Bot features limited
- Make sure `CALCOM_API_KEY` is properly set in `.env`
- Restart the bot after updating environment variables

## Getting Your Event Type ID

To create bookings, you need your event type ID:

1. Go to https://app.cal.com/event-types
2. Click on an event type
3. The ID is in the URL: `/event-types/[ID]`
4. Update line 34 in `calendar_manager.py`:
   ```python
   "eventTypeId": YOUR_ACTUAL_ID_HERE
   ```

## Testing the Integration

1. Start the bot: `python bot.py`
2. Send a message: "Schedule a meeting tomorrow at 2pm"
3. Check if the booking appears in your Cal.com calendar

## Benefits of Cal.com

- ✅ No OAuth flow needed
- ✅ Simple API key authentication
- ✅ Built-in scheduling features
- ✅ Modern booking interface
- ✅ Integration with multiple calendar providers
- ✅ Automatic timezone handling

## Need Help?

- Cal.com API Docs: https://cal.com/docs/api-reference
- Cal.com Support: https://cal.com/support
- Check the bot logs for detailed error messages

## Rollback Instructions

If you need to go back to Google Calendar:

1. Restore the old files from git history
2. Reinstall Google dependencies: `pip install google-auth google-auth-oauthlib google-api-python-client`
3. Add back `credentials.json`
4. Restart the bot
