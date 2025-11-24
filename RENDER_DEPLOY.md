# Render Deployment Guide

## Quick Deploy to Render

### Step 1: Prepare Your Repository
Your code is already on GitHub at: `https://github.com/mostafasaidi/assisstent`

### Step 2: Deploy on Render

1. **Go to Render**: https://render.com/
2. **Sign up/Login** with your GitHub account
3. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `mostafasaidi/assisstent`
   - Click "Connect"

### Step 3: Configure the Service

**Basic Settings:**
- **Name**: `telegram-calendar-bot` (or any name you prefer)
- **Region**: Choose closest to you (e.g., Frankfurt)
- **Branch**: `main`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python bot_simple.py`

**Environment Variables** (Click "Add Environment Variable"):
```
TELEGRAM_BOT_TOKEN=8325159356:AAH01SAaRty7rAPcSGr6n4ratGsJcZVKWBI
TELEGRAM_USER_ID=906938973
CALCOM_API_KEY=your_calcom_api_key_here
GROQ_API_KEY=your_groq_api_key_here
CALCOM_API_URL=https://api.cal.com/v1
BOT_NAME=Calendar Assistant Bot
```

### Step 4: Deploy
- Click "Create Web Service"
- Render will automatically:
  - Install dependencies
  - Start your bot
  - Keep it running 24/7

### Step 5: Monitor
- View logs in Render dashboard
- Bot will auto-restart if it crashes
- Free tier includes 750 hours/month

## Alternative: Use render.yaml (Blueprint)

If you want automated deployment:

1. Push the `render.yaml` file to your repo
2. On Render dashboard, click "New +" → "Blueprint"
3. Connect your repo
4. Render will read `render.yaml` and set everything up automatically
5. You only need to add the secret environment variables

## Troubleshooting

**Bot not responding?**
- Check logs in Render dashboard
- Verify all environment variables are set
- Ensure TELEGRAM_BOT_TOKEN is correct

**Out of hours?**
- Free tier: 750 hours/month
- Upgrade to paid plan for unlimited hours

**Need to update?**
- Push changes to GitHub
- Render auto-deploys on git push

## Cost
- **Free Plan**: 750 hours/month (perfect for 24/7 bot)
- **Paid Plan**: $7/month for unlimited hours

Your bot will be live and running 24/7 on Render! 🚀
