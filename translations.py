"""
Language translations for the bot
Supports English and Persian (Farsi)
"""

LANGUAGES = {
    'en': {
        'welcome': """
🤖 Welcome to {bot_name}!{calendar_status}

I'm your intelligent calendar and task management assistant. 

Use the buttons below or talk to me naturally!

Examples:
• "Schedule a meeting tomorrow at 2pm"
• "What's on my calendar today?"
• "Show my upcoming events"
""",
        'welcome_limited': "\n⚠️ Calendar features currently disabled. Please add CALCOM_API_KEY to .env to enable.\n",
        'help_title': '📖 *Help & Commands*',
        'help_buttons': '*Button Actions:*',
        'help_natural': '*Natural Language:*',
        'help_natural_text': 'You can also just type naturally:',
        'help_menu': 'Type /menu anytime to show the main menu.',
        
        # Buttons
        'btn_add_event': '➕ Add Event',
        'btn_upcoming': '📅 Upcoming',
        'btn_today': '📋 Today',
        'btn_search': '🔍 Search',
        'btn_edit': '✏️ Edit Event',
        'btn_delete': '🗑️ Delete Event',
        'btn_cancel': '❌ Cancel',
        'btn_language': '🌐 Language',
        
        # Messages
        'calendar_disabled': '❌ Calendar features are disabled.',
        'creating_event': '📝 Let\'s create a new event!\n\nPlease enter the event title:',
        'select_date': '📅 Select a date for your event:',
        'select_time': '⏰ Select a time:',
        'enter_title': '📝 Please type the event title/description:',
        'creating': '⏳ Creating your event...',
        'event_created': '✅ Event created successfully!',
        'event_failed': '❌ Failed to create event: {error}',
        'cancelled': '❌ Cancelled.',
        'use_menu': 'Use the menu buttons below:',
        
        # Events
        'upcoming_events': '📅 Your Upcoming Events:',
        'no_upcoming': 'You have no upcoming events. Your schedule is clear! ✨',
        'today_schedule': '📋 Today\'s Schedule ({date}):',
        'no_today': 'No events scheduled for today ({date}). Enjoy your free day! 🌟',
        'search_query': '🔍 Please enter your search query:',
        'found_events': '🔍 Found events matching \'{query}\':',
        'no_found': 'No events found matching \'{query}\'.',
        'select_delete': '🗑️ Select an event to delete:',
        'no_delete': 'You have no upcoming events to delete.',
        'event_deleted': '✅ Event deleted successfully!',
        'delete_failed': '❌ Failed to delete event: {error}',
        
        # Time
        'date_time_selected': '✅ Date & Time: {datetime}',
        'date_selected': '📅 Date: {date}',
        'select_minutes': '⏰ Select minutes for {hour}:__',
        'back_to_hours': '🔙 Back to Hours',
        
        # Edit
        'edit_coming_soon': '✏️ Edit feature coming soon! Use Delete and Add for now.',
        'enter_edit_name': '✏️ Please enter the name of the event you want to edit:',
        
        # Errors
        'error_occurred': 'I apologize, but I encountered an error processing your request. Could you please try again?',
        'invalid_date': '❌ Invalid date format. Please use YYYY-MM-DD (e.g., 2025-11-25) or type \'today\' or \'tomorrow\':',
        'invalid_time': '❌ Invalid time format. Please use HH:MM format (e.g., 14:30 or 2:30 PM):',
        'error_no_datetime': '❌ Error: No date/time selected. Please try again.',
        'invalid_number': '❌ Please enter a valid number:',
        'invalid_event_number': '❌ Invalid event number. Please try again.',
        
        # Language
        'language_changed': '✅ Language changed to English',
        'select_language': '🌐 Select your language:\n\nانتخاب زبان:'
    },
    
    'fa': {
        'welcome': """
🤖 به {bot_name} خوش آمدید!{calendar_status}

من دستیار هوشمند تقویم و مدیریت وظایف شما هستم.

از دکمه‌های زیر استفاده کنید یا به صورت طبیعی با من صحبت کنید!

مثال‌ها:
• "فردا ساعت ۲ بعدازظهر جلسه بذار"
• "امروز چه برنامه‌ای دارم؟"
• "رویدادهای آینده رو نشون بده"
""",
        'welcome_limited': "\n⚠️ امکانات تقویم غیرفعال است. لطفاً CALCOM_API_KEY را به .env اضافه کنید.\n",
        'help_title': '📖 *راهنما و دستورات*',
        'help_buttons': '*عملکرد دکمه‌ها:*',
        'help_natural': '*زبان طبیعی:*',
        'help_natural_text': 'می‌توانید به صورت طبیعی تایپ کنید:',
        'help_menu': 'برای نمایش منو /menu را تایپ کنید.',
        
        # Buttons
        'btn_add_event': '➕ رویداد جدید',
        'btn_upcoming': '📅 رویدادهای آینده',
        'btn_today': '📋 امروز',
        'btn_search': '🔍 جستجو',
        'btn_edit': '✏️ ویرایش',
        'btn_delete': '🗑️ حذف رویداد',
        'btn_cancel': '❌ لغو',
        'btn_language': '🌐 زبان',
        
        # Messages
        'calendar_disabled': '❌ امکانات تقویم غیرفعال است.',
        'creating_event': '📝 بیایید یک رویداد جدید بسازیم!\n\nلطفاً عنوان رویداد را وارد کنید:',
        'select_date': '📅 یک تاریخ برای رویداد خود انتخاب کنید:',
        'select_time': '⏰ زمان را انتخاب کنید:',
        'enter_title': '📝 لطفاً عنوان/توضیحات رویداد را تایپ کنید:',
        'creating': '⏳ در حال ایجاد رویداد...',
        'event_created': '✅ رویداد با موفقیت ایجاد شد!',
        'event_failed': '❌ خطا در ایجاد رویداد: {error}',
        'cancelled': '❌ لغو شد.',
        'use_menu': 'از دکمه‌های منو استفاده کنید:',
        
        # Events
        'upcoming_events': '📅 رویدادهای آینده شما:',
        'no_upcoming': 'شما رویداد آینده‌ای ندارید. برنامه شما خالی است! ✨',
        'today_schedule': '📋 برنامه امروز ({date}):',
        'no_today': 'رویدادی برای امروز ({date}) ثبت نشده. از روز آزاد خود لذت ببرید! 🌟',
        'search_query': '🔍 لطفاً کلمه جستجو را وارد کنید:',
        'found_events': '🔍 رویدادهای مطابق با \'{query}\' پیدا شد:',
        'no_found': 'رویدادی مطابق با \'{query}\' پیدا نشد.',
        'select_delete': '🗑️ یک رویداد برای حذف انتخاب کنید:',
        'no_delete': 'شما رویداد آینده‌ای برای حذف ندارید.',
        'event_deleted': '✅ رویداد با موفقیت حذف شد!',
        'delete_failed': '❌ خطا در حذف رویداد: {error}',
        
        # Time
        'date_time_selected': '✅ تاریخ و زمان: {datetime}',
        'date_selected': '📅 تاریخ: {date}',
        'select_minutes': '⏰ دقیقه را برای ساعت {hour} انتخاب کنید:',
        'back_to_hours': '🔙 بازگشت به ساعت‌ها',
        
        # Edit
        'edit_coming_soon': '✏️ امکان ویرایش به زودی! فعلاً از حذف و اضافه کردن استفاده کنید.',
        'enter_edit_name': '✏️ لطفاً نام رویدادی که می‌خواهید ویرایش کنید را وارد کنید:',
        
        # Errors
        'error_occurred': 'متأسفم، اما در پردازش درخواست شما خطایی رخ داد. لطفاً دوباره تلاش کنید.',
        'invalid_date': '❌ فرمت تاریخ نامعتبر است. لطفاً از فرمت YYYY-MM-DD استفاده کنید (مثال: 2025-11-25) یا \'today\' یا \'tomorrow\' تایپ کنید:',
        'invalid_time': '❌ فرمت زمان نامعتبر است. لطفاً از فرمت HH:MM استفاده کنید (مثال: 14:30 یا 2:30 PM):',
        'error_no_datetime': '❌ خطا: تاریخ/زمان انتخاب نشده. لطفاً دوباره تلاش کنید.',
        'invalid_number': '❌ لطفاً یک عدد معتبر وارد کنید:',
        'invalid_event_number': '❌ شماره رویداد نامعتبر است. لطفاً دوباره تلاش کنید.',
        
        # Language
        'language_changed': '✅ زبان به فارسی تغییر کرد',
        'select_language': '🌐 Select your language:\n\nانتخاب زبان:'
    }
}


def get_text(lang_code: str, key: str, **kwargs) -> str:
    """
    Get translated text for a given language code and key
    
    Args:
        lang_code: Language code ('en' or 'fa')
        key: Translation key
        **kwargs: Format arguments for string formatting
    
    Returns:
        Translated text
    """
    # Default to English if language not found
    lang = LANGUAGES.get(lang_code, LANGUAGES['en'])
    text = lang.get(key, LANGUAGES['en'].get(key, key))
    
    # Format if kwargs provided
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    
    return text


def get_user_language(user_id: int, user_data: dict) -> str:
    """
    Get user's preferred language
    
    Args:
        user_id: Telegram user ID
        user_data: User's context data
    
    Returns:
        Language code ('en' or 'fa')
    """
    return user_data.get('language', 'en')


def set_user_language(user_data: dict, lang_code: str):
    """
    Set user's preferred language
    
    Args:
        user_data: User's context data
        lang_code: Language code to set
    """
    user_data['language'] = lang_code
