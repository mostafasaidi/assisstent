"""
Telegram Bot Module
Handles all Telegram interactions and integrates AI Agent with Calendar Manager
"""
import logging
import datetime
import calendar as cal_module
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from ai_agent import AIAgent
from calendar_manager import CalendarManager
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_USER_ID, BOT_NAME

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot handler with AI integration"""
    
    def __init__(self):
        self.ai_agent = AIAgent()
        self.calendar_manager = CalendarManager()
        self.calendar_enabled = self.calendar_manager.is_connected()
        self.app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.setup_handlers()
        
        if not self.calendar_enabled:
            print("\n⚠️  Bot started in LIMITED MODE - Calendar features disabled")
            print("📝 The bot will work but cannot manage calendar bookings")
            print("✅ To enable full features, add CALCOM_API_KEY to .env and restart\n")
        else:
            print("\n✅ Bot started successfully with full Cal.com calendar features\n")
    
    def setup_handlers(self):
        """Set up command and message handlers"""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("today", self.today_command))
        self.app.add_handler(CommandHandler("upcoming", self.upcoming_command))
        self.app.add_handler(CommandHandler("create", self.create_event_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    def get_main_menu_keyboard(self):
        """Generate main menu keyboard"""
        keyboard = [
            ["➕ Add Event", "📅 Upcoming"],
            ["📋 Today", "🔍 Search"],
            ["✏️ Edit Event", "🗑️ Delete Event"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        
        calendar_status = "" if self.calendar_enabled else "\n⚠️ Calendar features currently disabled. Please add CALCOM_API_KEY to .env to enable.\n"
        
        welcome_message = f"""
🤖 Welcome to {BOT_NAME}!{calendar_status}

I'm your intelligent calendar and task management assistant. 

Use the buttons below to manage your calendar, or just talk to me naturally!

Examples:
• "Schedule a meeting tomorrow at 2pm"
• "What's on my calendar today?"
• "Show my upcoming events"
"""
        
        await update.message.reply_text(
            welcome_message,
            reply_markup=self.get_main_menu_keyboard()
        )
        logger.info(f"User {user_id} started the bot")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
📖 How to use me:

🗣️ Natural Language:
Just talk to me like you would to a human assistant!

Examples:
• "Schedule a meeting with John tomorrow at 3pm"
• "What do I have on Monday?"
• "Create a reminder to call mom at 5pm"
• "Show my schedule for next week"

⚡ Quick Commands:
/today - View today's events
/upcoming - View upcoming events
/create - Create event with date picker 📅
/help - Show this help

💡 Or use the menu buttons below! 👇
"""
        keyboard = self.get_main_menu_keyboard()
        await update.message.reply_text(help_message, reply_markup=keyboard)
    
    async def today_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /today command - show today's events"""
        if not self.calendar_enabled:
            await update.message.reply_text("❌ Calendar features are disabled. Please add CALCOM_API_KEY to your .env file and restart the bot.")
            return
        
        try:
            today = datetime.date.today()
            events = self.calendar_manager.get_events_for_date(today)
            
            if not events:
                response = "📅 You have no events scheduled for today. Enjoy your free time! ✨"
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ Add Event", callback_data="menu_add")],
                    [InlineKeyboardButton("📅 Upcoming", callback_data="menu_upcoming")],
                    [InlineKeyboardButton("🔙 Main Menu", callback_data="menu_back")]
                ])
            else:
                response = f"📅 Today's Schedule ({today.strftime('%B %d, %Y')}):\n\n"
                response += self.ai_agent.format_events_for_display(events)
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ Add Event", callback_data="menu_add")],
                    [InlineKeyboardButton("✏️ Edit", callback_data="menu_edit"), InlineKeyboardButton("🗑️ Delete", callback_data="menu_delete")],
                    [InlineKeyboardButton("🔙 Main Menu", callback_data="menu_back")]
                ])
            
            await update.message.reply_text(response, reply_markup=keyboard)
        
        except Exception as e:
            logger.error(f"Error in today_command: {e}")
            await update.message.reply_text("Sorry, I encountered an error retrieving today's events. Please try again.")
    
    async def upcoming_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /upcoming command - show upcoming events"""
        if not self.calendar_enabled:
            await update.message.reply_text("❌ Calendar features are disabled. Please add CALCOM_API_KEY to your .env file and restart the bot.")
            return
        
        try:
            events = self.calendar_manager.get_upcoming_events(max_results=10)
            
            if not events:
                response = "📅 You have no upcoming events. Your schedule is clear! ✨"
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ Add Event", callback_data="menu_add")],
                    [InlineKeyboardButton("🔙 Main Menu", callback_data="menu_back")]
                ])
            else:
                response = "📅 Your Upcoming Events:\n\n"
                response += self.ai_agent.format_events_for_display(events)
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ Add Event", callback_data="menu_add")],
                    [InlineKeyboardButton("✏️ Edit", callback_data="menu_edit"), InlineKeyboardButton("🗑️ Delete", callback_data="menu_delete")],
                    [InlineKeyboardButton("🔙 Main Menu", callback_data="menu_back")]
                ])
            
            await update.message.reply_text(response, reply_markup=keyboard)
        
        except Exception as e:
            logger.error(f"Error in upcoming_command: {e}")
            await update.message.reply_text("Sorry, I encountered an error retrieving upcoming events. Please try again.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages with AI processing"""
        user_message = update.message.text
        user_id = update.effective_user.id
        
        logger.info(f"Received message from {user_id}: {user_message}")
        
        # Check if message is from keyboard button
        if user_message in ["➕ Add Event", "📅 Upcoming", "📋 Today", "🔍 Search", "✏️ Edit Event", "🗑️ Delete Event"]:
            if user_message == "➕ Add Event":
                await self.create_event_command(update, context)
                return
            elif user_message == "📅 Upcoming":
                await self.upcoming_command(update, context)
                return
            elif user_message == "📋 Today":
                await self.today_command(update, context)
                return
            elif user_message == "🔍 Search":
                context.user_data['waiting_for_search'] = True
                await update.message.reply_text("🔍 Please enter your search query:", reply_markup=self.get_main_menu_keyboard())
                return
            elif user_message == "✏️ Edit Event":
                await update.message.reply_text("✏️ Please type the name of the event you want to edit:", reply_markup=self.get_main_menu_keyboard())
                context.user_data['waiting_for_edit_query'] = True
                return
            elif user_message == "🗑️ Delete Event":
                await self.show_delete_options(update, context)
                return
        
        # Check if we're waiting for event title
        if context.user_data.get('waiting_for_title'):
            await self.process_event_creation(update, context, user_message)
            return
        
        # Check if we're waiting for search query
        if context.user_data.get('waiting_for_search'):
            await self.process_search(update, context, user_message)
            return
        
        # Check if we're waiting for new title for edit
        if context.user_data.get('waiting_for_new_title'):
            await self.process_title_edit(update, context, user_message)
            return
        
        # Send typing indicator
        await update.message.chat.send_action(action="typing")
        
        try:
            # Analyze the user's request with AI
            analysis = self.ai_agent.analyze_user_request(user_message)
            action = analysis.get('action', 'general_chat')
            params = analysis.get('parameters', {})
            
            logger.info(f"AI Analysis - Action: {action}, Params: {params}")
            
            # Handle different actions
            if action == 'create_event':
                # Show calendar picker instead of trying to parse dates
                if not self.calendar_enabled:
                    await update.message.reply_text("❌ Calendar features are disabled. Please add CALCOM_API_KEY to your .env file and restart the bot.")
                    return
                
                # Store event title if provided
                title = params.get('title', '')
                if title:
                    context.user_data['event_data'] = {'title': title}
                else:
                    context.user_data['event_data'] = {}
                
                context.user_data['creating_event'] = True
                await self.show_calendar(update, context)
                return
            
            elif action == 'list_events':
                events = self.calendar_manager.get_upcoming_events(max_results=10)
                if events:
                    response = "📅 Your Upcoming Events:\n\n"
                    response += self.ai_agent.format_events_for_display(events)
                else:
                    response = "You have no upcoming events. Your schedule is clear! ✨"
            
            elif action == 'get_date_events':
                response = await self.handle_get_date_events(params)
            
            elif action == 'search_events':
                query = params.get('query', '')
                if query:
                    events = self.calendar_manager.search_events(query)
                    if events:
                        response = f"🔍 Found events matching '{query}':\n\n"
                        response += self.ai_agent.format_events_for_display(events)
                    else:
                        response = f"No events found matching '{query}'."
                else:
                    response = "Please specify what you want to search for."
            
            elif action == 'delete_event':
                response = await self.handle_delete_event(params)
            
            elif action == 'update_event':
                response = await self.handle_update_event(params)
            
            elif action == 'general_chat':
                response = params.get('response_text', '')
                if not response:
                    response = self.ai_agent.generate_response(user_message)
            
            else:
                response = self.ai_agent.generate_response(user_message)
            
            await update.message.reply_text(response)
        
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            await update.message.reply_text(
                "I apologize, but I encountered an error processing your request. Could you please try again or rephrase your request?"
            )
    
    async def handle_create_event(self, params: dict, original_message: str) -> str:
        """Handle event creation"""
        if not self.calendar_enabled:
            return "❌ Calendar features are disabled. Please add CALCOM_API_KEY to your .env file and restart the bot to enable calendar management."
        
        try:
            title = params.get('title', 'Untitled Event')
            
            # Parse start and end times
            start_time_str = params.get('start_time')
            end_time_str = params.get('end_time')
            duration_minutes = params.get('duration_minutes', 60)
            
            # Try to parse datetime
            if start_time_str:
                try:
                    start_time = datetime.datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                except:
                    start_time = self.ai_agent.parse_datetime(start_time_str)
            else:
                return "I need to know when you want to schedule this event. Please specify a date and time."
            
            if not start_time:
                return "I couldn't understand the time you specified. Please try again with a clearer time description."
            
            # Calculate end time
            if end_time_str:
                try:
                    end_time = datetime.datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))
                except:
                    end_time = self.ai_agent.parse_datetime(end_time_str)
            else:
                end_time = start_time + datetime.timedelta(minutes=duration_minutes)
            
            # Create the event
            result = self.calendar_manager.create_event(
                summary=title,
                start_time=start_time,
                end_time=end_time,
                description=params.get('description', ''),
                location=params.get('location', '')
            )
            
            if result.get('success'):
                response = f"✅ Event created successfully!\n\n"
                response += f"📌 {result['summary']}\n"
                response += f"⏰ {start_time.strftime('%B %d, %Y at %I:%M %p')}\n"
                if result.get('link'):
                    response += f"🔗 {result['link']}"
                return response
            else:
                return f"❌ Failed to create event: {result.get('error', 'Unknown error')}"
        
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            return "I encountered an error while creating the event. Please try again."
    
    async def handle_get_date_events(self, params: dict) -> str:
        """Handle getting events for a specific date"""
        try:
            date_str = params.get('date')
            
            if date_str:
                if date_str.lower() == 'today':
                    target_date = datetime.date.today()
                elif date_str.lower() == 'tomorrow':
                    target_date = datetime.date.today() + datetime.timedelta(days=1)
                else:
                    target_date = datetime.datetime.fromisoformat(date_str).date()
            else:
                target_date = datetime.date.today()
            
            events = self.calendar_manager.get_events_for_date(target_date)
            
            if not events:
                return f"📅 No events scheduled for {target_date.strftime('%B %d, %Y')}."
            else:
                response = f"📅 Events for {target_date.strftime('%B %d, %Y')}:\n\n"
                response += self.ai_agent.format_events_for_display(events)
                return response
        
        except Exception as e:
            logger.error(f"Error getting date events: {e}")
            return "I encountered an error retrieving events for that date."
    
    async def handle_delete_event(self, params: dict) -> str:
        """Handle event deletion"""
        try:
            query = params.get('query', '')
            event_id = params.get('event_id')
            
            if event_id:
                result = self.calendar_manager.delete_event(event_id)
                if result.get('success'):
                    return "✅ Event deleted successfully!"
                else:
                    return f"❌ Failed to delete event: {result.get('error')}"
            
            elif query:
                # Search for the event first
                events = self.calendar_manager.search_events(query)
                if not events:
                    return f"No events found matching '{query}'."
                elif len(events) == 1:
                    # Only one match, delete it
                    result = self.calendar_manager.delete_event(events[0]['id'])
                    if result.get('success'):
                        return f"✅ Deleted: {events[0]['summary']}"
                    else:
                        return f"❌ Failed to delete event: {result.get('error')}"
                else:
                    # Multiple matches, show them
                    response = f"Found {len(events)} events matching '{query}'. Please be more specific:\n\n"
                    response += self.ai_agent.format_events_for_display(events)
                    return response
            else:
                return "Please specify which event you want to delete."
        
        except Exception as e:
            logger.error(f"Error deleting event: {e}")
            return "I encountered an error while deleting the event."
    
    async def handle_update_event(self, params: dict) -> str:
        """Handle event updates"""
        try:
            query = params.get('query', '')
            event_id = params.get('event_id')
            
            # Find the event
            if event_id:
                event = event_id
            elif query:
                events = self.calendar_manager.search_events(query)
                if not events:
                    return f"No events found matching '{query}'."
                elif len(events) > 1:
                    response = f"Found {len(events)} events. Please be more specific:\n\n"
                    response += self.ai_agent.format_events_for_display(events)
                    return response
                event = events[0]['id']
            else:
                return "Please specify which event you want to update."
            
            # Update the event
            result = self.calendar_manager.update_event(
                event_id=event,
                summary=params.get('title'),
                description=params.get('description'),
                location=params.get('location')
            )
            
            if result.get('success'):
                return f"✅ Event updated successfully!\n🔗 {result.get('link', '')}"
            else:
                return f"❌ Failed to update event: {result.get('error')}"
        
        except Exception as e:
            logger.error(f"Error updating event: {e}")
            return "I encountered an error while updating the event."
    
    async def create_event_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /create command - show date picker"""
        if not self.calendar_enabled:
            await update.message.reply_text("❌ Calendar features are disabled. Please add CALCOM_API_KEY to your .env file and restart the bot.")
            return
        
        # Store that we're in event creation mode
        context.user_data['creating_event'] = True
        context.user_data['event_data'] = {}
        
        # Show calendar
        await self.show_calendar(update, context)
    
    def generate_calendar_keyboard(self, year: int, month: int):
        """Generate inline keyboard with calendar"""
        keyboard = []
        
        # Month and year header
        month_name = cal_module.month_name[month]
        keyboard.append([
            InlineKeyboardButton("◀️", callback_data=f"cal_prev_{year}_{month}"),
            InlineKeyboardButton(f"{month_name} {year}", callback_data="cal_ignore"),
            InlineKeyboardButton("▶️", callback_data=f"cal_next_{year}_{month}")
        ])
        
        # Day names
        keyboard.append([
            InlineKeyboardButton(day, callback_data="cal_ignore") 
            for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        ])
        
        # Calendar days
        month_calendar = cal_module.monthcalendar(year, month)
        for week in month_calendar:
            row = []
            for day in week:
                if day == 0:
                    row.append(InlineKeyboardButton(" ", callback_data="cal_ignore"))
                else:
                    row.append(InlineKeyboardButton(
                        str(day), 
                        callback_data=f"cal_day_{year}_{month}_{day}"
                    ))
            keyboard.append(row)
        
        # Cancel button
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cal_cancel")])
        
        return InlineKeyboardMarkup(keyboard)
    
    async def show_calendar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show calendar picker"""
        today = datetime.date.today()
        keyboard = self.generate_calendar_keyboard(today.year, today.month)
        
        message = "📅 Select a date for your event:"
        
        if update.callback_query:
            await update.callback_query.edit_message_text(message, reply_markup=keyboard)
        else:
            await update.message.reply_text(message, reply_markup=keyboard)
    
    async def show_calendar_in_callback(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Show calendar picker in callback"""
        today = datetime.date.today()
        keyboard = self.generate_calendar_keyboard(today.year, today.month)
        await query.edit_message_text("📅 Select a date for your event:", reply_markup=keyboard)
    
    async def show_upcoming_events(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Show upcoming events from callback"""
        if not self.calendar_enabled:
            await query.edit_message_text("❌ Calendar features are disabled.")
            return
        
        try:
            events = self.calendar_manager.get_upcoming_events(max_results=10)
            
            if not events:
                response = "📅 You have no upcoming events. Your schedule is clear! ✨"
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ Add Event", callback_data="menu_add")],
                    [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_back")]
                ])
            else:
                response = "📅 Your Upcoming Events:\n\n"
                response += self.ai_agent.format_events_for_display(events)
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ Add Event", callback_data="menu_add")],
                    [InlineKeyboardButton("🗑️ Delete Event", callback_data="menu_delete")],
                    [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_back")]
                ])
            
            await query.edit_message_text(response, reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Error showing upcoming events: {e}")
            await query.edit_message_text("Sorry, I encountered an error. Please try again.")
    
    async def show_today_events(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Show today's events from callback"""
        if not self.calendar_enabled:
            await query.edit_message_text("❌ Calendar features are disabled.")
            return
        
        try:
            today = datetime.date.today()
            events = self.calendar_manager.get_events_for_date(today)
            
            if not events:
                response = "📅 You have no events scheduled for today. Enjoy your free time! ✨"
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ Add Event", callback_data="menu_add")],
                    [InlineKeyboardButton("📅 Upcoming", callback_data="menu_upcoming")],
                    [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_back")]
                ])
            else:
                response = f"📅 Today's Schedule ({today.strftime('%B %d, %Y')}):\n\n"
                response += self.ai_agent.format_events_for_display(events)
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ Add Event", callback_data="menu_add")],
                    [InlineKeyboardButton("🗑️ Delete Event", callback_data="menu_delete")],
                    [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_back")]
                ])
            
            await query.edit_message_text(response, reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Error showing today's events: {e}")
            await query.edit_message_text("Sorry, I encountered an error. Please try again.")
    
    async def show_events_for_edit(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Show events list for editing"""
        if not self.calendar_enabled:
            await query.edit_message_text("❌ Calendar features are disabled.")
            return
        
        try:
            events = self.calendar_manager.get_upcoming_events(max_results=10)
            
            if not events:
                keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_back")]])
                await query.edit_message_text("No upcoming events to edit.", reply_markup=keyboard)
                return
            
            keyboard = []
            for event in events[:10]:
                event_time = event.get('start', '')
                if 'T' in event_time:
                    dt = datetime.datetime.fromisoformat(event_time.replace('Z', '+00:00'))
                    time_str = dt.strftime('%b %d, %I:%M %p')
                else:
                    time_str = event_time
                
                button_text = f"{event.get('summary', 'Untitled')} - {time_str}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"edit_{event['id']}")])
            
            keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_back")])
            
            await query.edit_message_text(
                "✏️ Select an event to edit:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            context.user_data['editing_mode'] = True
        except Exception as e:
            logger.error(f"Error showing events for edit: {e}")
            await query.edit_message_text("Sorry, I encountered an error. Please try again.")
    
    async def show_events_for_delete(self, query, context: ContextTypes.DEFAULT_TYPE):
        """Show events list for deletion"""
        if not self.calendar_enabled:
            await query.edit_message_text("❌ Calendar features are disabled.")
            return
        
        try:
            events = self.calendar_manager.get_upcoming_events(max_results=10)
            
            if not events:
                keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_back")]])
                await query.edit_message_text("No upcoming events to delete.", reply_markup=keyboard)
                return
            
            keyboard = []
            for event in events[:10]:
                event_time = event.get('start', '')
                if 'T' in event_time:
                    dt = datetime.datetime.fromisoformat(event_time.replace('Z', '+00:00'))
                    time_str = dt.strftime('%b %d, %I:%M %p')
                else:
                    time_str = event_time
                
                button_text = f"🗑️ {event.get('summary', 'Untitled')} - {time_str}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"delete_{event['id']}")])
            
            keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_back")])
            
            await query.edit_message_text(
                "🗑️ Select an event to delete:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            logger.error(f"Error showing events for delete: {e}")
            await query.edit_message_text("Sorry, I encountered an error. Please try again.")
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        # Handle main menu buttons
        if data == "menu_add":
            if not self.calendar_enabled:
                await query.edit_message_text("❌ Calendar features are disabled. Please add CALCOM_API_KEY to your .env file and restart the bot.")
                return
            context.user_data['creating_event'] = True
            context.user_data['event_data'] = {}
            await self.show_calendar_in_callback(query, context)
            return
        
        if data == "menu_upcoming":
            await self.show_upcoming_events(query, context)
            return
        
        if data == "menu_today":
            await self.show_today_events(query, context)
            return
        
        if data == "menu_search":
            await query.edit_message_text(
                "🔍 Please type the event name or keyword you want to search for:",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="menu_back")]])
            )
            context.user_data['waiting_for_search'] = True
            return
        
        if data == "menu_edit":
            await self.show_events_for_edit(query, context)
            return
        
        if data == "menu_delete":
            await self.show_events_for_delete(query, context)
            return
        
        if data == "menu_back":
            context.user_data.clear()
            await query.edit_message_text(
                "🤖 Main Menu\n\nChoose an action:",
                reply_markup=self.get_main_menu_keyboard()
            )
            return
        
        if data == "cal_ignore":
            return
        
        if data == "cal_cancel":
            context.user_data.clear()
            await query.edit_message_text(
                "❌ Cancelled.\n\n🤖 Main Menu",
                reply_markup=self.get_main_menu_keyboard()
            )
            return
        
        if data.startswith("cal_prev_"):
            _, _, year, month = data.split("_")
            year, month = int(year), int(month)
            month -= 1
            if month < 1:
                month = 12
                year -= 1
            keyboard = self.generate_calendar_keyboard(year, month)
            await query.edit_message_text("📅 Select a date for your event:", reply_markup=keyboard)
            return
        
        if data.startswith("cal_next_"):
            _, _, year, month = data.split("_")
            year, month = int(year), int(month)
            month += 1
            if month > 12:
                month = 1
                year += 1
            keyboard = self.generate_calendar_keyboard(year, month)
            await query.edit_message_text("📅 Select a date for your event:", reply_markup=keyboard)
            return
        
        if data.startswith("cal_day_"):
            _, _, year, month, day = data.split("_")
            selected_date = datetime.date(int(year), int(month), int(day))
            
            # Store the selected date
            context.user_data['event_data']['date'] = selected_date
            
            # Now ask for time
            await self.show_time_picker(query, context, selected_date)
            return
        
        if data.startswith("time_"):
            _, hour = data.split("_")
            hour = int(hour)
            
            date = context.user_data['event_data']['date']
            context.user_data['event_data']['hour'] = hour
            
            # Show minute picker
            await self.show_minute_picker(query, context, date, hour)
            return
        
        if data.startswith("min_"):
            _, minute = data.split("_")
            minute = int(minute)
            
            date = context.user_data['event_data']['date']
            hour = context.user_data['event_data']['hour']
            
            # Create datetime
            start_time = datetime.datetime.combine(date, datetime.time(hour, minute))
            context.user_data['event_data']['start_time'] = start_time
            
            # Check if title was already provided
            if context.user_data['event_data'].get('title'):
                title = context.user_data['event_data']['title']
                await query.edit_message_text(
                    f"⏳ Creating event...\n"
                    f"📌 {title}\n"
                    f"⏰ {start_time.strftime('%B %d, %Y at %I:%M %p')}"
                )
                # Create event directly
                await self.create_event_now(query, context, title)
            else:
                # Ask for event title
                await query.edit_message_text(
                    f"✅ Date & Time: {start_time.strftime('%B %d, %Y at %I:%M %p')}\n\n"
                    "📝 Please enter the event title/description:"
                )
                context.user_data['waiting_for_title'] = True
            return
        
        if data.startswith("delete_"):
            event_id = data.replace("delete_", "")
            
            # Confirm deletion
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Yes, Delete", callback_data=f"confirm_delete_{event_id}"),
                    InlineKeyboardButton("❌ Cancel", callback_data="menu_back")
                ]
            ])
            await query.edit_message_text(
                "⚠️ Are you sure you want to delete this event?",
                reply_markup=keyboard
            )
            return
        
        if data.startswith("confirm_delete_"):
            event_id = data.replace("confirm_delete_", "")
            result = self.calendar_manager.delete_event(event_id)
            
            if result.get('success'):
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📅 View Upcoming", callback_data="menu_upcoming")],
                    [InlineKeyboardButton("🗑️ Delete Another", callback_data="menu_delete")],
                    [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_back")]
                ])
                await query.edit_message_text(
                    "✅ Event deleted successfully!",
                    reply_markup=keyboard
                )
            else:
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Try Again", callback_data="menu_delete")],
                    [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_back")]
                ])
                await query.edit_message_text(
                    f"❌ Failed to delete event: {result.get('error')}",
                    reply_markup=keyboard
                )
            return
        
        if data.startswith("edit_"):
            event_id = data.replace("edit_", "")
            context.user_data['editing_event_id'] = event_id
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📝 Change Title", callback_data=f"edit_title_{event_id}")],
                [InlineKeyboardButton("⏰ Change Time", callback_data=f"edit_time_{event_id}")],
                [InlineKeyboardButton("🔙 Back", callback_data="menu_edit")]
            ])
            
            await query.edit_message_text(
                "What would you like to edit?",
                reply_markup=keyboard
            )
            return
        
        if data.startswith("edit_title_"):
            event_id = data.replace("edit_title_", "")
            context.user_data['editing_event_id'] = event_id
            context.user_data['waiting_for_new_title'] = True
            
            await query.edit_message_text(
                "📝 Please enter the new event title:",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="menu_back")]])
            )
            return
        
        if data.startswith("edit_time_"):
            await query.edit_message_text(
                "⏰ Time editing feature coming soon!\n\nFor now, you can delete and recreate the event.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_back")]])
            )
            return
    
    async def show_time_picker(self, query, context: ContextTypes.DEFAULT_TYPE, date: datetime.date):
        """Show time picker (hours)"""
        keyboard = []
        
        # Morning hours
        keyboard.append([
            InlineKeyboardButton(f"{h}:00", callback_data=f"time_{h}")
            for h in range(6, 12)
        ])
        
        # Afternoon hours
        keyboard.append([
            InlineKeyboardButton(f"{h}:00", callback_data=f"time_{h}")
            for h in range(12, 18)
        ])
        
        # Evening hours
        keyboard.append([
            InlineKeyboardButton(f"{h}:00", callback_data=f"time_{h}")
            for h in range(18, 24)
        ])
        
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cal_cancel")])
        
        await query.edit_message_text(
            f"📅 Selected: {date.strftime('%B %d, %Y')}\n\n"
            "🕐 Select the hour:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def show_minute_picker(self, query, context: ContextTypes.DEFAULT_TYPE, date: datetime.date, hour: int):
        """Show minute picker"""
        keyboard = []
        
        # Minutes in 15-minute intervals
        keyboard.append([
            InlineKeyboardButton(f"{hour}:{m:02d}", callback_data=f"min_{m}")
            for m in [0, 15, 30, 45]
        ])
        
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cal_cancel")])
        
        await query.edit_message_text(
            f"📅 Selected: {date.strftime('%B %d, %Y')}\n"
            f"🕐 Hour: {hour}:00\n\n"
            "⏰ Select the minutes:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def create_event_now(self, query_or_update, context: ContextTypes.DEFAULT_TYPE, title: str):
        """Create event immediately"""
        try:
            start_time = context.user_data['event_data']['start_time']
            end_time = start_time + datetime.timedelta(hours=1)  # Default 1 hour duration
            
            # Create the event
            result = self.calendar_manager.create_event(
                summary=title,
                start_time=start_time,
                end_time=end_time,
                description=f"Created via Telegram Bot",
                location="",
                timezone="UTC"
            )
            
            if result.get('success'):
                response = f"✅ Event created successfully!\n\n"
                response += f"📌 {title}\n"
                response += f"⏰ {start_time.strftime('%B %d, %Y at %I:%M %p')}\n"
                response += f"⏱️ Duration: 1 hour\n"
                if result.get('link'):
                    response += f"🔗 {result['link']}"
            else:
                response = f"❌ Failed to create event: {result.get('error', 'Unknown error')}"
            
            # Add action buttons
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Add Another", callback_data="menu_add")],
                [InlineKeyboardButton("📅 View Upcoming", callback_data="menu_upcoming")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_back")]
            ])
            
            # Send response - determine correct method based on object type
            if hasattr(query_or_update, 'edit_message_text'):
                # It's a CallbackQuery
                await query_or_update.edit_message_text(response, reply_markup=keyboard)
            elif hasattr(query_or_update, 'message'):
                # It's an Update object
                await query_or_update.message.reply_text(response, reply_markup=keyboard)
            else:
                # Fallback
                await query_or_update.reply_text(response, reply_markup=keyboard)
            
            # Clear user data
            context.user_data.clear()
        
        except Exception as e:
            logger.error(f"Error creating event: {e}")
            error_msg = "❌ Sorry, I encountered an error creating the event. Please try again."
            
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_back")]])
            
            if hasattr(query_or_update, 'edit_message_text'):
                await query_or_update.edit_message_text(error_msg, reply_markup=keyboard)
            elif hasattr(query_or_update, 'message'):
                await query_or_update.message.reply_text(error_msg, reply_markup=keyboard)
            else:
                await query_or_update.reply_text(error_msg, reply_markup=keyboard)
            
            context.user_data.clear()
    
    async def process_event_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, title: str):
        """Process the final event creation with title from message"""
        await self.create_event_now(update, context, title)
    
    async def process_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query_text: str):
        """Process search query"""
        context.user_data.pop('waiting_for_search', None)
        
        try:
            events = self.calendar_manager.search_events(query_text)
            
            if events:
                response = f"🔍 Found {len(events)} event(s) matching '{query_text}':\n\n"
                response += self.ai_agent.format_events_for_display(events)
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔍 Search Again", callback_data="menu_search")],
                    [InlineKeyboardButton("📅 View All", callback_data="menu_upcoming")],
                    [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_back")]
                ])
            else:
                response = f"🔍 No events found matching '{query_text}'."
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔍 Search Again", callback_data="menu_search")],
                    [InlineKeyboardButton("➕ Add Event", callback_data="menu_add")],
                    [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_back")]
                ])
            
            await update.message.reply_text(response, reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Error searching events: {e}")
            await update.message.reply_text("Sorry, I encountered an error searching for events.")
    
    async def process_title_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE, new_title: str):
        """Process event title edit"""
        event_id = context.user_data.get('editing_event_id')
        context.user_data.clear()
        
        if not event_id:
            await update.message.reply_text("❌ Error: Event ID not found.")
            return
        
        try:
            result = self.calendar_manager.update_event(
                event_id=event_id,
                summary=new_title
            )
            
            if result.get('success'):
                response = f"✅ Event title updated to: {new_title}"
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("✏️ Edit Another", callback_data="menu_edit")],
                    [InlineKeyboardButton("📅 View Upcoming", callback_data="menu_upcoming")],
                    [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_back")]
                ])
            else:
                response = f"❌ Failed to update event: {result.get('error')}"
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Try Again", callback_data="menu_edit")],
                    [InlineKeyboardButton("🔙 Back to Menu", callback_data="menu_back")]
                ])
            
            await update.message.reply_text(response, reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Error updating event title: {e}")
            await update.message.reply_text("Sorry, I encountered an error updating the event.")
    
    def run(self):
        """Start the bot"""
        logger.info("Starting bot...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    bot = TelegramBot()
    bot.run()
