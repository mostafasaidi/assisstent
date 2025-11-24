"""
Telegram Bot Module - Simple Keyboard Version
Handles all Telegram interactions with regular keyboard buttons
"""
import logging
import datetime
import calendar as cal_module
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
from ai_agent import AIAgent
from calendar_manager import CalendarManager
from task_note_manager import TaskNoteManager
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_USER_ID, BOT_NAME
from translations import get_text, get_user_language, set_user_language

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def is_admin_user(user_id: int) -> bool:
    """Check if the user is the admin (TELEGRAM_USER_ID)"""
    return user_id == TELEGRAM_USER_ID


class TelegramBot:
    """Telegram bot handler with AI integration"""
    
    def __init__(self):
        self.ai_agent = AIAgent()
        self.calendar_manager = CalendarManager()
        self.task_note_manager = TaskNoteManager()
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
        self.app.add_handler(CommandHandler("menu", self.start_command))
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    def get_main_menu_keyboard(self, lang='en', user_id=None):
        """Generate main menu keyboard - full menu for admin, chat-only for others"""
        if user_id is not None and is_admin_user(user_id):
            # Full menu for admin user
            keyboard = [
                [get_text(lang, 'btn_add_event'), get_text(lang, 'btn_upcoming')],
                [get_text(lang, 'btn_today'), get_text(lang, 'btn_search')],
                [get_text(lang, 'btn_add_task'), get_text(lang, 'btn_list_tasks')],
                [get_text(lang, 'btn_add_note'), get_text(lang, 'btn_list_notes')],
                [get_text(lang, 'btn_edit'), get_text(lang, 'btn_delete')],
                [get_text(lang, 'btn_chat')],
                [get_text(lang, 'btn_language')]
            ]
        else:
            # Chat-only menu for non-admin users
            keyboard = [
                [get_text(lang, 'btn_chat')],
                [get_text(lang, 'btn_language')]
            ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        lang = get_user_language(user_id, context.user_data)
        
        calendar_status = "" if self.calendar_enabled else get_text(lang, 'welcome_limited')
        welcome_message = get_text(lang, 'welcome', bot_name=BOT_NAME, calendar_status=calendar_status)
        
        await update.message.reply_text(
            welcome_message,
            reply_markup=self.get_main_menu_keyboard(lang, user_id)
        )
        logger.info(f"User {user_id} started the bot")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        user_id = update.effective_user.id
        lang = get_user_language(user_id, context.user_data)
        help_message = """
📖 *Help & Commands*

*Button Actions:*
➕ Add Event - Create a new calendar event
📅 Upcoming - View your upcoming events
📋 Today - See today's schedule
🔍 Search - Find specific events
✏️ Edit Event - Modify an existing event
🗑️ Delete Event - Remove an event

*Natural Language:*
You can also just type naturally:
• "Create meeting tomorrow at 3pm"
• "What do I have scheduled?"
• "Delete my dentist appointment"

Type /menu anytime to show the main menu.
"""
        await update.message.reply_text(
            help_message,
            parse_mode='Markdown',
            reply_markup=self.get_main_menu_keyboard(lang, user_id)
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages including keyboard buttons"""
        user_message = update.message.text
        user_id = update.effective_user.id
        
        logger.info(f"Received message from {user_id}: {user_message}")
        
        lang = get_user_language(user_id, context.user_data)
        
        # Define admin-only button messages (calendar, task, note features)
        admin_only_buttons = [
            "➕ Add Event", "➕ رویداد جدید",
            "📅 Upcoming", "📅 رویدادهای آینده",
            "📋 Today", "📋 امروز",
            "🔍 Search", "🔍 جستجو",
            "✏️ Edit Event", "✏️ ویرایش",
            "🗑️ Delete Event", "🗑️ حذف رویداد",
            "✅ Add Task", "✅ وظیفه جدید",
            "📝 My Tasks", "📝 وظایف من",
            "📒 Add Note", "📒 یادداشت جدید",
            "📚 My Notes", "📚 یادداشت‌های من"
        ]
        
        # Check if non-admin user is trying to access admin-only features
        if user_message in admin_only_buttons and not is_admin_user(user_id):
            await update.message.reply_text(
                get_text(lang, 'access_denied'),
                reply_markup=self.get_main_menu_keyboard(lang, user_id)
            )
            return
        
        # Handle keyboard button presses (English and Persian)
        if user_message in ["➕ Add Event", "➕ رویداد جدید"]:
            await self.handle_add_event(update, context)
            return
        elif user_message in ["📅 Upcoming", "📅 رویدادهای آینده"]:
            await self.handle_upcoming(update, context)
            return
        elif user_message in ["📋 Today", "📋 امروز"]:
            await self.handle_today(update, context)
            return
        elif user_message in ["🔍 Search", "🔍 جستجو"]:
            await self.handle_search_request(update, context)
            return
        elif user_message in ["✏️ Edit Event", "✏️ ویرایش"]:
            await self.handle_edit_request(update, context)
            return
        elif user_message in ["🗑️ Delete Event", "🗑️ حذف رویداد"]:
            await self.handle_delete_request(update, context)
            return
        elif user_message in ["🌐 Language", "🌐 زبان"]:
            await self.show_language_selection(update, context)
            return
        elif user_message in ["✅ Add Task", "✅ وظیفه جدید"]:
            await self.handle_add_task(update, context)
            return
        elif user_message in ["📝 My Tasks", "📝 وظایف من"]:
            await self.handle_list_tasks(update, context)
            return
        elif user_message in ["📒 Add Note", "📒 یادداشت جدید"]:
            await self.handle_add_note(update, context)
            return
        elif user_message in ["📚 My Notes", "📚 یادداشت‌های من"]:
            await self.handle_list_notes(update, context)
            return
        elif user_message in ["💬 Chat with Assistant", "💬 چت با دستیار"]:
            # Chat mode - available to all users
            await update.message.reply_text(
                get_text(lang, 'chat_ready'),
                reply_markup=self.get_main_menu_keyboard(lang, user_id)
            )
            return
        
        # Check if we're in a flow
        if context.user_data.get('flow'):
            await self.handle_flow(update, context, user_message)
            return
        
        # Send typing indicator
        await update.message.chat.send_action(action="typing")
        
        try:
            # Analyze the user's request with AI
            analysis = self.ai_agent.analyze_user_request(user_message)
            action = analysis.get('action', 'general_chat')
            params = analysis.get('parameters', {})
            
            logger.info(f"AI Analysis - Action: {action}, Params: {params}")
            
            # Define admin-only actions
            admin_only_actions = ['create_event', 'list_events', 'get_date_events', 'search_events', 'update_event', 'delete_event']
            
            # Check if non-admin user is trying to access admin-only AI actions
            if action in admin_only_actions and not is_admin_user(user_id):
                await update.message.reply_text(
                    get_text(lang, 'access_denied'),
                    reply_markup=self.get_main_menu_keyboard(lang, user_id)
                )
                return
            
            # Handle different actions
            if action == 'create_event':
                if not self.calendar_enabled:
                    await update.message.reply_text(
                        "❌ Calendar features are disabled. Please add CALCOM_API_KEY to your .env file and restart the bot.",
                        reply_markup=self.get_main_menu_keyboard(lang, user_id)
                    )
                    return
                await self.handle_add_event(update, context, params.get('title', ''))
                return
            
            elif action == 'list_events':
                await self.handle_upcoming(update, context)
                return
            
            elif action == 'get_date_events':
                date = params.get('date')
                if date:
                    events = self.calendar_manager.get_events_for_date(date)
                    if events:
                        response = f"📅 Events for {date}:\n\n"
                        response += self.ai_agent.format_events_for_display(events)
                    else:
                        response = f"No events scheduled for {date}."
                else:
                    response = "Please specify a date."
                await update.message.reply_text(response, reply_markup=self.get_main_menu_keyboard(lang, user_id))
                return
            
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
                    await self.handle_search_request(update, context)
                    return
                await update.message.reply_text(response, reply_markup=self.get_main_menu_keyboard(lang, user_id))
                return
            
            elif action == 'general_chat':
                response = params.get('response_text', '')
                if not response:
                    response = self.ai_agent.generate_response(user_message)
                await update.message.reply_text(response, reply_markup=self.get_main_menu_keyboard(lang, user_id))
                return
            
            else:
                response = self.ai_agent.generate_response(user_message)
                await update.message.reply_text(response, reply_markup=self.get_main_menu_keyboard(lang, user_id))
        
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            await update.message.reply_text(
                "I apologize, but I encountered an error processing your request. Could you please try again?",
                reply_markup=self.get_main_menu_keyboard(lang, user_id)
            )
    
    async def handle_add_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE, title: str = ""):
        """Start event creation flow with calendar picker"""
        user_id = update.effective_user.id
        lang = get_user_language(user_id, context.user_data)
        if not self.calendar_enabled:
            await update.message.reply_text(
                "❌ Calendar features are disabled.",
                reply_markup=self.get_main_menu_keyboard(lang, user_id)
            )
            return
        
        context.user_data['flow'] = 'create_event'
        context.user_data['event_data'] = {'title': title} if title else {}
        
        # Show inline calendar picker
        today = datetime.date.today()
        calendar_keyboard = self.generate_calendar_keyboard(today.year, today.month)
        
        await update.message.reply_text(
            "📅 Select a date for your event:",
            reply_markup=calendar_keyboard
        )
    
    async def handle_upcoming(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show upcoming events"""
        user_id = update.effective_user.id
        lang = get_user_language(user_id, context.user_data)
        if not self.calendar_enabled:
            await update.message.reply_text(
                "❌ Calendar features are disabled.",
                reply_markup=self.get_main_menu_keyboard(lang, user_id)
            )
            return
        
        events = self.calendar_manager.get_upcoming_events(max_results=10)
        if events:
            response = "📅 Your Upcoming Events:\n\n"
            response += self.ai_agent.format_events_for_display(events)
        else:
            response = "You have no upcoming events. Your schedule is clear! ✨"
        
        await update.message.reply_text(response, reply_markup=self.get_main_menu_keyboard(lang, user_id))
    
    async def handle_today(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show today's events"""
        user_id = update.effective_user.id
        lang = get_user_language(user_id, context.user_data)
        if not self.calendar_enabled:
            await update.message.reply_text(
                "❌ Calendar features are disabled.",
                reply_markup=self.get_main_menu_keyboard(lang, user_id)
            )
            return
        
        today = datetime.date.today()
        events = self.calendar_manager.get_events_for_date(today.isoformat())
        
        if events:
            response = f"📋 Today's Schedule ({today.strftime('%B %d, %Y')}):\n\n"
            response += self.ai_agent.format_events_for_display(events)
        else:
            response = f"No events scheduled for today ({today.strftime('%B %d, %Y')}). Enjoy your free day! 🌟"
        
        await update.message.reply_text(response, reply_markup=self.get_main_menu_keyboard(lang, user_id))
    
    async def handle_search_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Request search query from user"""
        context.user_data['flow'] = 'search'
        await update.message.reply_text(
            "🔍 Please enter your search query:",
            reply_markup=ReplyKeyboardMarkup([["❌ Cancel"]], resize_keyboard=True, one_time_keyboard=True)
        )
    
    async def handle_edit_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Request event name to edit"""
        context.user_data['flow'] = 'edit'
        await update.message.reply_text(
            "✏️ Please enter the name of the event you want to edit:",
            reply_markup=ReplyKeyboardMarkup([["❌ Cancel"]], resize_keyboard=True, one_time_keyboard=True)
        )
    
    async def handle_delete_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show delete options with inline buttons"""
        user_id = update.effective_user.id
        lang = get_user_language(user_id, context.user_data)
        if not self.calendar_enabled:
            await update.message.reply_text(
                "❌ Calendar features are disabled.",
                reply_markup=self.get_main_menu_keyboard(lang, user_id)
            )
            return
        
        events = self.calendar_manager.get_upcoming_events(max_results=10)
        if not events:
            await update.message.reply_text(
                "You have no upcoming events to delete.",
                reply_markup=self.get_main_menu_keyboard(lang, user_id)
            )
            return
        
        response = "🗑️ Select an event to delete:\n\n"
        keyboard = []
        
        for event in events[:10]:  # Limit to 10 events
            event_id = event.get('id')
            title = event.get('summary', 'Untitled')
            start_time = event.get('start', 'N/A')
            
            button_text = f"🗑️ {title[:30]} - {start_time[:16]}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"delete_{event_id}")])
        
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cal_cancel")])
        
        await update.message.reply_text(
            response,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def handle_flow(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_message: str):
        """Handle ongoing user flows"""
        user_id = update.effective_user.id
        lang = get_user_language(user_id, context.user_data)
        if user_message == "❌ Cancel":
            context.user_data.clear()
            await update.message.reply_text(
                "❌ Cancelled.",
                reply_markup=self.get_main_menu_keyboard(lang, user_id)
            )
            return
        
        flow = context.user_data.get('flow')
        
        if flow == 'create_event':
            await self.handle_create_event_flow(update, context, user_message)
        elif flow == 'create_event_title':
            await self.handle_create_event_with_title(update, context, user_message)
        elif flow == 'search':
            await self.handle_search_flow(update, context, user_message)
        elif flow == 'delete':
            await self.handle_delete_flow(update, context, user_message)
        elif flow == 'edit':
            await self.handle_edit_flow(update, context, user_message)
        elif flow == 'add_task':
            await self.handle_add_task_flow(update, context, user_message)
        elif flow == 'add_note_title':
            await self.handle_add_note_title_flow(update, context, user_message)
        elif flow == 'add_note_content':
            await self.handle_add_note_content_flow(update, context, user_message)
    
    async def handle_create_event_with_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE, title: str):
        """Create event with selected date/time and user-provided title"""
        user_id = update.effective_user.id
        lang = get_user_language(user_id, context.user_data)
        event_data = context.user_data.get('event_data', {})
        start_time = event_data.get('start_time')
        
        if not start_time:
            await update.message.reply_text(
                "❌ Error: No date/time selected. Please try again.",
                reply_markup=self.get_main_menu_keyboard(lang, user_id)
            )
            context.user_data.clear()
            return
        
        # Create the event
        end_time = start_time + datetime.timedelta(hours=1)  # Default 1 hour duration
        
        await update.message.reply_text(
            "⏳ Creating your event...",
            reply_markup=ReplyKeyboardRemove()
        )
        
        result = self.calendar_manager.create_event(
            summary=title,
            start_time=start_time,
            end_time=end_time,
            description="",
            timezone="UTC"
        )
        
        if result.get('success'):
            response = f"✅ Event created successfully!\n\n"
            response += f"📌 {title}\n"
            response += f"📅 {start_time.strftime('%B %d, %Y')}\n"
            response += f"⏰ {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"
        else:
            response = f"❌ Failed to create event: {result.get('error')}"
        
        context.user_data.clear()
        await update.message.reply_text(response, reply_markup=self.get_main_menu_keyboard(lang, user_id))
    
    async def handle_create_event_flow(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_message: str):
        """Handle event creation flow"""
        event_data = context.user_data.get('event_data', {})
        
        # Step 1: Get title
        if 'title' not in event_data:
            event_data['title'] = user_message
            context.user_data['event_data'] = event_data
            await update.message.reply_text(
                f"📌 Event: {user_message}\n\n"
                "📅 Enter the date (e.g., 2025-11-25 or tomorrow):",
                reply_markup=ReplyKeyboardMarkup([["❌ Cancel"]], resize_keyboard=True, one_time_keyboard=True)
            )
            return
        
        # Step 2: Get date
        if 'date' not in event_data:
            # Parse date
            try:
                if user_message.lower() == 'today':
                    date = datetime.date.today()
                elif user_message.lower() == 'tomorrow':
                    date = datetime.date.today() + datetime.timedelta(days=1)
                else:
                    date = datetime.datetime.strptime(user_message, '%Y-%m-%d').date()
                
                event_data['date'] = date
                context.user_data['event_data'] = event_data
                await update.message.reply_text(
                    f"📌 Event: {event_data['title']}\n"
                    f"📅 Date: {date.strftime('%B %d, %Y')}\n\n"
                    "⏰ Enter the time (e.g., 14:30 or 2:30 PM):",
                    reply_markup=ReplyKeyboardMarkup([["❌ Cancel"]], resize_keyboard=True, one_time_keyboard=True)
                )
                return
            except:
                await update.message.reply_text(
                    "❌ Invalid date format. Please use YYYY-MM-DD (e.g., 2025-11-25) or type 'today' or 'tomorrow':",
                    reply_markup=ReplyKeyboardMarkup([["❌ Cancel"]], resize_keyboard=True, one_time_keyboard=True)
                )
                return
        
        # Step 3: Get time and create event
        if 'time' not in event_data:
            # Parse time
            try:
                # Try different time formats
                time_obj = None
                for fmt in ['%H:%M', '%I:%M %p', '%I:%M%p', '%H%M']:
                    try:
                        time_obj = datetime.datetime.strptime(user_message.strip(), fmt).time()
                        break
                    except:
                        continue
                
                if not time_obj:
                    raise ValueError("Invalid time format")
                
                # Combine date and time
                start_time = datetime.datetime.combine(event_data['date'], time_obj)
                end_time = start_time + datetime.timedelta(hours=1)  # Default 1 hour duration
                
                # Create the event
                await update.message.reply_text(
                    "⏳ Creating your event...",
                    reply_markup=ReplyKeyboardRemove()
                )
                
                result = self.calendar_manager.create_event(
                    summary=event_data['title'],
                    start_time=start_time,
                    end_time=end_time,
                    description="",
                    timezone="UTC"
                )
                
                if result.get('success'):
                    response = f"✅ Event created successfully!\n\n"
                    response += f"📌 {event_data['title']}\n"
                    response += f"📅 {start_time.strftime('%B %d, %Y')}\n"
                    response += f"⏰ {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"
                else:
                    response = f"❌ Failed to create event: {result.get('error')}"
                
                context.user_data.clear()
                user_id = update.effective_user.id
                lang = get_user_language(user_id, context.user_data)
                await update.message.reply_text(response, reply_markup=self.get_main_menu_keyboard(lang, user_id))
                
            except Exception as e:
                logger.error(f"Error parsing time: {e}")
                await update.message.reply_text(
                    "❌ Invalid time format. Please use HH:MM format (e.g., 14:30 or 2:30 PM):",
                    reply_markup=ReplyKeyboardMarkup([["❌ Cancel"]], resize_keyboard=True, one_time_keyboard=True)
                )
                return
    
    async def handle_search_flow(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_message: str):
        """Handle search flow"""
        user_id = update.effective_user.id
        lang = get_user_language(user_id, context.user_data)
        events = self.calendar_manager.search_events(user_message)
        if events:
            response = f"🔍 Found events matching '{user_message}':\n\n"
            response += self.ai_agent.format_events_for_display(events)
        else:
            response = f"No events found matching '{user_message}'."
        
        context.user_data.clear()
        await update.message.reply_text(response, reply_markup=self.get_main_menu_keyboard(lang, user_id))
    
    async def handle_delete_flow(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_message: str):
        """Handle delete flow"""
        user_id = update.effective_user.id
        lang = get_user_language(user_id, context.user_data)
        try:
            event_num = int(user_message) - 1
            events_list = context.user_data.get('events_list', [])
            
            if 0 <= event_num < len(events_list):
                event = events_list[event_num]
                event_id = event.get('id')
                
                result = self.calendar_manager.delete_event(event_id)
                
                if result.get('success'):
                    response = f"✅ Event deleted successfully!\n\n📌 {event.get('summary', 'Untitled')}"
                else:
                    response = f"❌ Failed to delete event: {result.get('error')}"
            else:
                response = "❌ Invalid event number. Please try again."
            
            context.user_data.clear()
            await update.message.reply_text(response, reply_markup=self.get_main_menu_keyboard(lang, user_id))
            
        except ValueError:
            await update.message.reply_text(
                "❌ Please enter a valid number:",
                reply_markup=ReplyKeyboardMarkup([["❌ Cancel"]], resize_keyboard=True, one_time_keyboard=True)
            )
    
    async def handle_edit_flow(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_message: str):
        """Handle edit flow"""
        user_id = update.effective_user.id
        lang = get_user_language(user_id, context.user_data)
        await update.message.reply_text(
            get_text(lang, 'edit_coming_soon'),
            reply_markup=self.get_main_menu_keyboard(lang, user_id)
        )
        context.user_data.clear()
    
    async def show_language_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show language selection menu"""
        keyboard = [
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
            [InlineKeyboardButton("🇮🇷 فارسی (Persian)", callback_data="lang_fa")]
        ]
        await update.message.reply_text(
            get_text('en', 'select_language'),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # ===== TASK HANDLERS =====
    
    async def handle_add_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start task creation flow"""
        user_id = update.effective_user.id
        lang = get_user_language(user_id, context.user_data)
        
        context.user_data['flow'] = 'add_task'
        await update.message.reply_text(
            get_text(lang, 'add_task_title'),
            reply_markup=ReplyKeyboardMarkup([[get_text(lang, 'btn_cancel')]], resize_keyboard=True, one_time_keyboard=True)
        )
    
    async def handle_add_task_flow(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_message: str):
        """Handle task creation flow"""
        user_id = update.effective_user.id
        lang = get_user_language(user_id, context.user_data)
        
        # Add the task
        result = self.task_note_manager.add_task(user_id, user_message)
        
        if result['success']:
            response = get_text(lang, 'task_added', title=user_message)
        else:
            response = get_text(lang, 'error_occurred')
        
        context.user_data.clear()
        await update.message.reply_text(response, reply_markup=self.get_main_menu_keyboard(lang, user_id))
    
    async def handle_list_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's tasks"""
        user_id = update.effective_user.id
        lang = get_user_language(user_id, context.user_data)
        
        tasks = self.task_note_manager.get_tasks(user_id, include_completed=False)
        
        if not tasks:
            await update.message.reply_text(
                get_text(lang, 'no_tasks'),
                reply_markup=self.get_main_menu_keyboard(lang, user_id)
            )
            return
        
        # Create inline keyboard for tasks
        keyboard = []
        for task in tasks:
            priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(task.get('priority', 'medium'), '⚪')
            button_text = f"{priority_emoji} {task['title'][:40]}"
            keyboard.append([
                InlineKeyboardButton(f"✅ {button_text}", callback_data=f"task_complete_{task['id']}"),
                InlineKeyboardButton("🗑️", callback_data=f"task_delete_{task['id']}")
            ])
        
        await update.message.reply_text(
            get_text(lang, 'select_task_action'),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # ===== NOTE HANDLERS =====
    
    async def handle_add_note(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start note creation flow"""
        user_id = update.effective_user.id
        lang = get_user_language(user_id, context.user_data)
        
        context.user_data['flow'] = 'add_note_title'
        context.user_data['note_data'] = {}
        await update.message.reply_text(
            get_text(lang, 'add_note_title'),
            reply_markup=ReplyKeyboardMarkup([[get_text(lang, 'btn_cancel')]], resize_keyboard=True, one_time_keyboard=True)
        )
    
    async def handle_add_note_title_flow(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_message: str):
        """Handle note title input"""
        user_id = update.effective_user.id
        lang = get_user_language(user_id, context.user_data)
        
        context.user_data['note_data']['title'] = user_message
        context.user_data['flow'] = 'add_note_content'
        
        await update.message.reply_text(
            get_text(lang, 'add_note_content'),
            reply_markup=ReplyKeyboardMarkup([[get_text(lang, 'btn_cancel')]], resize_keyboard=True, one_time_keyboard=True)
        )
    
    async def handle_add_note_content_flow(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_message: str):
        """Handle note content input and create note"""
        user_id = update.effective_user.id
        lang = get_user_language(user_id, context.user_data)
        
        note_data = context.user_data.get('note_data', {})
        title = note_data.get('title', 'Untitled')
        
        # Add the note
        result = self.task_note_manager.add_note(user_id, title, user_message)
        
        if result['success']:
            response = get_text(lang, 'note_added', title=title)
        else:
            response = get_text(lang, 'error_occurred')
        
        context.user_data.clear()
        await update.message.reply_text(response, reply_markup=self.get_main_menu_keyboard(lang, user_id))
    
    async def handle_list_notes(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's notes"""
        user_id = update.effective_user.id
        lang = get_user_language(user_id, context.user_data)
        
        notes = self.task_note_manager.get_notes(user_id)
        
        if not notes:
            await update.message.reply_text(
                get_text(lang, 'no_notes'),
                reply_markup=self.get_main_menu_keyboard(lang, user_id)
            )
            return
        
        # Create inline keyboard for notes
        keyboard = []
        for note in notes[:20]:  # Limit to 20 notes
            button_text = f"📒 {note['title'][:40]}"
            keyboard.append([
                InlineKeyboardButton(button_text, callback_data=f"note_view_{note['id']}"),
                InlineKeyboardButton("🗑️", callback_data=f"note_delete_{note['id']}")
            ])
        
        await update.message.reply_text(
            get_text(lang, 'select_note_action'),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    def generate_calendar_keyboard(self, year: int, month: int):
        """Generate inline calendar keyboard for date selection"""
        keyboard = []
        
        # Month and year header with navigation
        month_name = cal_module.month_name[month]
        keyboard.append([
            InlineKeyboardButton("◀️", callback_data=f"cal_prev_{year}_{month}"),
            InlineKeyboardButton(f"{month_name} {year}", callback_data="cal_ignore"),
            InlineKeyboardButton("▶️", callback_data=f"cal_next_{year}_{month}")
        ])
        
        # Day names header
        keyboard.append([InlineKeyboardButton(day, callback_data="cal_ignore") 
                        for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]])
        
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
    
    def generate_time_keyboard(self):
        """Generate inline keyboard for time selection"""
        keyboard = []
        
        # Hours in rows of 4
        hours = []
        for hour in range(0, 24, 3):
            row = []
            for h in range(hour, min(hour + 3, 24)):
                row.append(InlineKeyboardButton(f"{h:02d}:00", callback_data=f"time_{h}_0"))
            hours.append(row)
        
        keyboard.extend(hours)
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cal_cancel")])
        
        return InlineKeyboardMarkup(keyboard)
    
    def generate_minute_keyboard(self, hour: int):
        """Generate inline keyboard for minute selection"""
        keyboard = []
        
        # Minutes in 15-minute intervals
        row = []
        for minute in [0, 15, 30, 45]:
            row.append(InlineKeyboardButton(
                f"{hour:02d}:{minute:02d}",
                callback_data=f"time_{hour}_{minute}"
            ))
        keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Hours", callback_data="time_back")])
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cal_cancel")])
        
        return InlineKeyboardMarkup(keyboard)
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = query.from_user.id
        lang = get_user_language(user_id, context.user_data)
        
        # Language selection
        if data.startswith("lang_"):
            new_lang = data.replace("lang_", "")
            set_user_language(context.user_data, new_lang)
            lang = new_lang
            
            await query.edit_message_text(
                get_text(lang, 'language_changed'),
                reply_markup=None
            )
            await query.message.reply_text(
                get_text(lang, 'use_menu'),
                reply_markup=self.get_main_menu_keyboard(lang, user_id)
            )
            return
        
        # Ignore placeholder buttons
        if data == "cal_ignore":
            return
        
        # Cancel action
        if data == "cal_cancel":
            context.user_data.clear()
            await query.edit_message_text(
                get_text(lang, 'cancelled'),
                reply_markup=None
            )
            await query.message.reply_text(
                get_text(lang, 'use_menu'),
                reply_markup=self.get_main_menu_keyboard(lang, user_id)
            )
            return
        
        # Calendar navigation
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
        
        # Date selection
        if data.startswith("cal_day_"):
            _, _, year, month, day = data.split("_")
            selected_date = datetime.date(int(year), int(month), int(day))
            
            context.user_data['event_data']['date'] = selected_date
            
            # Show time picker
            time_keyboard = self.generate_time_keyboard()
            await query.edit_message_text(
                f"📅 Date: {selected_date.strftime('%B %d, %Y')}\n\n⏰ Select a time:",
                reply_markup=time_keyboard
            )
            return
        
        # Time selection
        if data.startswith("time_"):
            if data == "time_back":
                time_keyboard = self.generate_time_keyboard()
                await query.edit_message_text(
                    f"📅 Date: {context.user_data['event_data']['date'].strftime('%B %d, %Y')}\n\n⏰ Select a time:",
                    reply_markup=time_keyboard
                )
                return
            
            parts = data.split("_")
            hour = int(parts[1])
            minute = int(parts[2]) if len(parts) > 2 else None
            
            if minute is None:
                # Show minute picker
                minute_keyboard = self.generate_minute_keyboard(hour)
                await query.edit_message_text(
                    f"📅 Date: {context.user_data['event_data']['date'].strftime('%B %d, %Y')}\n\n"
                    f"⏰ Select minutes for {hour:02d}:__",
                    reply_markup=minute_keyboard
                )
                return
            
            # Time fully selected, ask for title
            selected_date = context.user_data['event_data']['date']
            selected_time = datetime.datetime.combine(selected_date, datetime.time(hour, minute))
            context.user_data['event_data']['start_time'] = selected_time
            
            await query.edit_message_text(
                f"✅ Date & Time: {selected_time.strftime('%B %d, %Y at %I:%M %p')}\n\n"
                "📝 Please type the event title/description:"
            )
            context.user_data['flow'] = 'create_event_title'
            return
        
        # Delete event with inline buttons
        if data.startswith("delete_"):
            event_id = data.replace("delete_", "")
            result = self.calendar_manager.delete_event(event_id)
            
            if result.get('success'):
                await query.edit_message_text("✅ Event deleted successfully!")
                await query.message.reply_text(
                    "Use the menu below:",
                    reply_markup=self.get_main_menu_keyboard(lang, user_id)
                )
            else:
                await query.edit_message_text(f"❌ Failed to delete event: {result.get('error')}")
                await query.message.reply_text(
                    "Use the menu below:",
                    reply_markup=self.get_main_menu_keyboard(lang, user_id)
                )
            context.user_data.clear()
            return
        
        # Task actions
        if data.startswith("task_complete_"):
            task_id = int(data.replace("task_complete_", ""))
            result = self.task_note_manager.complete_task(user_id, task_id)
            
            if result.get('success'):
                task = result['task']
                await query.edit_message_text(
                    get_text(lang, 'task_completed', title=task['title'])
                )
                await query.message.reply_text(
                    get_text(lang, 'use_menu'),
                    reply_markup=self.get_main_menu_keyboard(lang, user_id)
                )
            else:
                await query.edit_message_text(f"❌ {result.get('error')}")
            return
        
        if data.startswith("task_delete_"):
            task_id = int(data.replace("task_delete_", ""))
            result = self.task_note_manager.delete_task(user_id, task_id)
            
            if result.get('success'):
                task = result['task']
                await query.edit_message_text(
                    get_text(lang, 'task_deleted', title=task['title'])
                )
                await query.message.reply_text(
                    get_text(lang, 'use_menu'),
                    reply_markup=self.get_main_menu_keyboard(lang, user_id)
                )
            else:
                await query.edit_message_text(f"❌ {result.get('error')}")
            return
        
        # Note actions
        if data.startswith("note_view_"):
            note_id = int(data.replace("note_view_", ""))
            note = self.task_note_manager.get_note(user_id, note_id)
            
            if note:
                created_date = datetime.datetime.fromisoformat(note['created_at']).strftime('%B %d, %Y')
                content = note.get('content', 'No content')
                await query.edit_message_text(
                    get_text(lang, 'note_content', title=note['title'], content=content, date=created_date)
                )
                await query.message.reply_text(
                    get_text(lang, 'use_menu'),
                    reply_markup=self.get_main_menu_keyboard(lang, user_id)
                )
            else:
                await query.edit_message_text("❌ Note not found")
            return
        
        if data.startswith("note_delete_"):
            note_id = int(data.replace("note_delete_", ""))
            result = self.task_note_manager.delete_note(user_id, note_id)
            
            if result.get('success'):
                note = result['note']
                await query.edit_message_text(
                    get_text(lang, 'note_deleted', title=note['title'])
                )
                await query.message.reply_text(
                    get_text(lang, 'use_menu'),
                    reply_markup=self.get_main_menu_keyboard(lang, user_id)
                )
            else:
                await query.edit_message_text(f"❌ {result.get('error')}")
            return
    
    def run(self):
        """Start the bot"""
        logger.info("Starting bot...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()
