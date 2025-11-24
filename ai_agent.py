"""
AI Agent Module - Smart Assistant with OpenAI Integration
Handles natural language processing and intelligent task management
"""
import json
import datetime
from typing import Dict, List, Optional
from groq import Groq
from config import GROQ_API_KEY


class AIAgent:
    """Smart AI Assistant for task and event management"""
    
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.conversation_history = []
    
    def analyze_user_request(self, user_message: str) -> Dict:
        """
        Analyze user's natural language request and determine the action
        
        Args:
            user_message: The user's message
        
        Returns:
            Dictionary containing action type and extracted parameters
        """
        system_prompt = """You are a smart calendar and task management assistant. 
Analyze the user's message and extract:
1. Action type: create_event, list_events, update_event, delete_event, search_events, get_date_events, general_chat
2. Event details if applicable: title, start_time, end_time, description, location, date
3. Any other relevant parameters

Return ONLY a valid JSON object with the following structure:
{
    "action": "action_type",
    "parameters": {
        "title": "event title",
        "start_time": "ISO format datetime or description",
        "end_time": "ISO format datetime or description",
        "duration_minutes": number,
        "description": "description",
        "location": "location",
        "date": "YYYY-MM-DD",
        "query": "search query",
        "event_id": "id",
        "response_text": "friendly response to user"
    }
}

Current date and time: """ + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """

Examples:
- "Schedule a meeting tomorrow at 2pm for 1 hour" -> create_event with calculated times
- "What's on my calendar today?" -> get_date_events with today's date
- "Show my upcoming events" -> list_events
- "Cancel my dentist appointment" -> search_events to find it, then delete
"""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            result = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if result.startswith("```json"):
                result = result[7:]
            if result.startswith("```"):
                result = result[3:]
            if result.endswith("```"):
                result = result[:-3]
            
            result = result.strip()
            
            parsed_result = json.loads(result)
            return parsed_result
        
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response was: {result}")
            return {
                "action": "general_chat",
                "parameters": {
                    "response_text": "I'm sorry, I couldn't understand that request. Could you please rephrase it?"
                }
            }
        except Exception as e:
            print(f"Error analyzing request: {e}")
            return {
                "action": "error",
                "parameters": {
                    "response_text": f"An error occurred: {str(e)}"
                }
            }
    
    def generate_response(self, user_message: str, context: Optional[str] = None) -> str:
        """
        Generate a natural language response
        
        Args:
            user_message: The user's message
            context: Additional context for the response
        
        Returns:
            AI-generated response
        """
        messages = [
            {
                "role": "system",
                "content": """You are a helpful, friendly calendar and task management assistant. 
You help users manage their schedules, events, and tasks. Be concise but friendly.
Current date and time: """ + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
        
        if context:
            messages.append({"role": "system", "content": f"Context: {context}"})
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.8,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I'm having trouble generating a response right now. Please try again."
    
    def parse_datetime(self, time_description: str, reference_date: Optional[datetime.datetime] = None) -> Optional[datetime.datetime]:
        """
        Parse natural language time description into datetime
        
        Args:
            time_description: Natural language time (e.g., "tomorrow at 2pm", "next Monday at 10am")
            reference_date: Reference date for relative times
        
        Returns:
            Parsed datetime object
        """
        if reference_date is None:
            reference_date = datetime.datetime.now()
        
        system_prompt = f"""Convert the time description to ISO format datetime.
Current datetime: {reference_date.isoformat()}
Return ONLY the ISO format datetime string, nothing else.
Examples:
- "tomorrow at 2pm" -> {(reference_date + datetime.timedelta(days=1)).replace(hour=14, minute=0, second=0).isoformat()}
- "in 2 hours" -> {(reference_date + datetime.timedelta(hours=2)).isoformat()}
- "next Monday at 10am" -> calculate the next Monday and set time to 10:00
"""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": time_description}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            datetime_str = response.choices[0].message.content.strip()
            return datetime.datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        
        except Exception as e:
            print(f"Error parsing datetime: {e}")
            return None
    
    def format_events_for_display(self, events: List[Dict]) -> str:
        """
        Format events list into a readable message
        
        Args:
            events: List of event dictionaries
        
        Returns:
            Formatted string for display
        """
        if not events:
            return "No events found."
        
        formatted = f"📅 Found {len(events)} event(s):\n\n"
        
        for i, event in enumerate(events, 1):
            start = event.get('start', 'Unknown time')
            try:
                # Try to format the datetime nicely
                if 'T' in start:
                    dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                    start = dt.strftime('%B %d, %Y at %I:%M %p')
            except:
                pass
            
            formatted += f"{i}. 📌 {event.get('summary', 'No Title')}\n"
            formatted += f"   ⏰ {start}\n"
            
            if event.get('description'):
                formatted += f"   📝 {event['description']}\n"
            
            if event.get('location'):
                formatted += f"   📍 {event['location']}\n"
            
            if event.get('link'):
                formatted += f"   🔗 {event['link']}\n"
            
            formatted += "\n"
        
        return formatted
    
    def create_smart_summary(self, events: List[Dict]) -> str:
        """
        Create an AI-generated summary of events
        
        Args:
            events: List of event dictionaries
        
        Returns:
            Smart summary of the events
        """
        if not events:
            return "You have no upcoming events. Your schedule is clear! ✨"
        
        events_text = "\n".join([
            f"- {event.get('summary')} at {event.get('start')}" 
            for event in events[:10]  # Limit to 10 events
        ])
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that summarizes calendar events in a friendly, concise way."
                    },
                    {
                        "role": "user",
                        "content": f"Summarize these upcoming events:\n{events_text}"
                    }
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Error creating summary: {e}")
            return self.format_events_for_display(events)
