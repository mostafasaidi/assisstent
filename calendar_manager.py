"""
Cal.com API Integration Module
Handles all calendar operations including creating, reading, updating events and bookings
"""
import datetime
from typing import List, Dict, Optional
import requests
import pytz
from config import CALCOM_API_KEY, CALCOM_API_URL


class CalendarManager:
    """Manages Cal.com operations"""
    
    def __init__(self):
        self.api_key = CALCOM_API_KEY
        self.api_url = CALCOM_API_URL
        # Cal.com uses query parameter authentication, not Bearer token
        self.headers = {
            "Content-Type": "application/json"
        }
        self.is_authenticated = self.authenticate()
    
    def is_connected(self):
        """Check if calendar is connected"""
        return self.is_authenticated and self.api_key is not None
    
    def authenticate(self):
        """Verify Cal.com API connection"""
        try:
            if not self.api_key:
                print("⚠️  Warning: Cal.com API key not found. Calendar features will be disabled.")
                print("📝 To enable calendar features:")
                print("   1. Go to https://app.cal.com/settings/developer/api-keys")
                print("   2. Create a new API key")
                print("   3. Add CALCOM_API_KEY to your .env file")
                return False
            
            # Test API connection by fetching user profile
            response = requests.get(
                f"{self.api_url}/me",
                headers=self.headers,
                params={"apiKey": self.api_key},
                timeout=10
            )
            
            if response.status_code == 200:
                return True
            else:
                print(f"⚠️  Cal.com API authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"⚠️  Calendar authentication error: {e}")
            return False
    
    def create_event(
        self,
        summary: str,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        description: str = "",
        location: str = "",
        timezone: str = "UTC"
    ) -> Dict:
        """
        Create a new booking/event in Cal.com
        
        Args:
            summary: Event title
            start_time: Event start time
            end_time: Event end time
            description: Event description
            location: Event location
            timezone: Timezone for the event
        
        Returns:
            Created event details
        """
        if not self.is_connected():
            return {'success': False, 'error': 'Cal.com not connected. Please set up API key in .env'}
        
        try:
            # Get user profile to fetch username and default calendar
            user_response = requests.get(
                f"{self.api_url}/me",
                headers=self.headers,
                params={"apiKey": self.api_key},
                timeout=10
            )
            
            if user_response.status_code != 200:
                return {'success': False, 'error': 'Could not fetch user profile'}
            
            user_data = user_response.json()
            user_email = user_data.get('email', 'bot@calendar.com')
            username = user_data.get('username', 'user')
            
            # First, get the user's event types to use the first available one
            event_types_response = requests.get(
                f"{self.api_url}/event-types",
                headers=self.headers,
                params={"apiKey": self.api_key},
                timeout=10
            )
            
            if event_types_response.status_code != 200:
                return {
                    'success': False,
                    'error': 'Could not fetch event types. Please create an event type in Cal.com first.'
                }
            
            event_types = event_types_response.json().get('event_types', [])
            if not event_types:
                return {
                    'success': False,
                    'error': 'No event types found. Please create an event type in your Cal.com account first.'
                }
            
            event_type_id = event_types[0]['id']
            
            # Cal.com booking API requires specific format with proper attendee info
            booking_data = {
                "eventTypeId": event_type_id,
                "start": start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "responses": {
                    "name": username,
                    "email": user_email,
                    "title": summary,
                    "notes": description,
                    "location": {"value": location, "optionValue": ""} if location else {"value": "inPerson", "optionValue": ""}
                },
                "title": summary,
                "timeZone": timezone,
                "language": "en",
                "metadata": {"customTitle": summary},
                "organizer": {
                    "name": username,
                    "email": user_email,
                    "timeZone": timezone
                }
            }
            
            response = requests.post(
                f"{self.api_url}/bookings",
                headers=self.headers,
                params={"apiKey": self.api_key},
                json=booking_data,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                booking = data.get('booking', data)
                return {
                    'success': True,
                    'event_id': booking.get('id', data.get('id')),
                    'link': booking.get('bookingUrl', data.get('link', '')),
                    'summary': summary,
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                }
            else:
                error_msg = response.text
                try:
                    error_json = response.json()
                    error_msg = error_json.get('message', error_msg)
                except:
                    pass
                return {
                    'success': False,
                    'error': f"Cal.com API error ({response.status_code}): {error_msg}"
                }
        except Exception as error:
            return {
                'success': False,
                'error': f"Error creating booking: {str(error)}"
            }
    
    def get_upcoming_events(self, max_results: int = 10) -> List[Dict]:
        """
        Get upcoming bookings from Cal.com
        
        Args:
            max_results: Maximum number of events to retrieve
        
        Returns:
            List of upcoming events
        """
        if not self.is_connected():
            return []
        
        try:
            # Get bookings from Cal.com
            response = requests.get(
                f"{self.api_url}/bookings",
                headers=self.headers,
                params={"apiKey": self.api_key, "take": max_results, "status": "upcoming"},
                timeout=10
            )
            
            if response.status_code != 200:
                print(f'API error: {response.status_code}')
                return []
            
            data = response.json()
            bookings = data.get('bookings', [])
            
            formatted_events = []
            for booking in bookings:
                # Skip cancelled or rejected bookings
                status = booking.get('status', '').lower()
                if status in ['cancelled', 'rejected', 'canceled']:
                    continue
                
                # Try to get custom title from metadata or responses, fallback to default title
                custom_title = None
                if booking.get('metadata') and isinstance(booking['metadata'], dict):
                    custom_title = booking['metadata'].get('customTitle')
                if not custom_title and booking.get('responses'):
                    if isinstance(booking['responses'], dict):
                        custom_title = booking['responses'].get('title')
                    elif isinstance(booking['responses'], list):
                        for resp in booking['responses']:
                            if resp.get('label') == 'title':
                                custom_title = resp.get('value')
                                break
                
                title = custom_title or booking.get('title', 'No Title')
                
                formatted_events.append({
                    'id': booking.get('id'),
                    'summary': title,
                    'start': booking.get('startTime'),
                    'end': booking.get('endTime'),
                    'description': booking.get('description', ''),
                    'location': booking.get('location', ''),
                    'link': booking.get('link', ''),
                    'status': status
                })
            
            return formatted_events
        except Exception as error:
            print(f'An error occurred: {error}')
            return []
    
    def update_event(
        self,
        event_id: str,
        summary: Optional[str] = None,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
        description: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict:
        """
        Update an existing booking in Cal.com
        
        Args:
            event_id: ID of the booking to update
            summary: New event title
            start_time: New start time
            end_time: New end time
            description: New description
            location: New location
        
        Returns:
            Updated event details
        """
        try:
            update_data = {}
            
            if summary:
                update_data['title'] = summary
            if description is not None:
                update_data['description'] = description
            if location is not None:
                update_data['location'] = location
            if start_time:
                update_data['startTime'] = start_time.isoformat()
            if end_time:
                update_data['endTime'] = end_time.isoformat()
            
            response = requests.patch(
                f"{self.api_url}/bookings/{event_id}",
                headers=self.headers,
                params={"apiKey": self.api_key},
                json=update_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'event_id': data.get('id'),
                    'link': data.get('link', ''),
                    'summary': data.get('title', summary)
                }
            else:
                return {
                    'success': False,
                    'error': f"API error: {response.status_code} - {response.text}"
                }
        except Exception as error:
            return {
                'success': False,
                'error': str(error)
            }
    
    def delete_event(self, event_id: str) -> Dict:
        """
        Cancel a booking in Cal.com
        
        Args:
            event_id: ID of the booking to cancel
        
        Returns:
            Status of the cancellation
        """
        try:
            # Try to cancel the booking using Cal.com's cancel endpoint
            cancel_data = {
                "id": event_id,
                "reason": "Cancelled via Telegram Bot"
            }
            
            # First try the cancel endpoint
            response = requests.post(
                f"{self.api_url}/bookings/{event_id}/cancel",
                headers=self.headers,
                params={"apiKey": self.api_key},
                json=cancel_data,
                timeout=10
            )
            
            # If cancel endpoint doesn't work, try delete
            if response.status_code not in [200, 201, 204]:
                response = requests.delete(
                    f"{self.api_url}/bookings/{event_id}",
                    headers=self.headers,
                    params={"apiKey": self.api_key},
                    timeout=10
                )
            
            if response.status_code in [200, 201, 204]:
                return {
                    'success': True,
                    'message': 'Event cancelled successfully'
                }
            else:
                # Try to get error details
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', response.text)
                except:
                    error_msg = response.text
                
                return {
                    'success': False,
                    'error': f"API error ({response.status_code}): {error_msg}"
                }
        except Exception as error:
            return {
                'success': False,
                'error': f"Exception: {str(error)}"
            }
    
    def search_events(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for bookings by query
        
        Args:
            query: Search query
            max_results: Maximum number of results
        
        Returns:
            List of matching events
        """
        try:
            # Get all bookings and filter client-side
            response = requests.get(
                f"{self.api_url}/bookings",
                headers=self.headers,
                params={"apiKey": self.api_key, "take": 100},  # Get more to search through
                timeout=10
            )
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            bookings = data.get('bookings', [])
            
            # Filter bookings by query
            query_lower = query.lower()
            formatted_events = []
            
            for booking in bookings:
                # Skip cancelled bookings
                status = booking.get('status', '').lower()
                if status in ['cancelled', 'rejected', 'canceled']:
                    continue
                
                # Get custom title
                custom_title = None
                if booking.get('metadata') and isinstance(booking['metadata'], dict):
                    custom_title = booking['metadata'].get('customTitle')
                if not custom_title and booking.get('responses'):
                    if isinstance(booking['responses'], dict):
                        custom_title = booking['responses'].get('title')
                
                display_title = custom_title or booking.get('title', 'No Title')
                title_lower = display_title.lower()
                description = booking.get('description', '').lower()
                
                if query_lower in title_lower or query_lower in description:
                    formatted_events.append({
                        'id': booking.get('id'),
                        'summary': display_title,
                        'start': booking.get('startTime'),
                        'end': booking.get('endTime'),
                        'description': booking.get('description', ''),
                        'link': booking.get('link', '')
                    })
                    
                    if len(formatted_events) >= max_results:
                        break
            
            return formatted_events
        except Exception as error:
            print(f'An error occurred: {error}')
            return []
    
    def get_events_for_date(self, date: datetime.date) -> List[Dict]:
        """
        Get all bookings for a specific date
        
        Args:
            date: The date to get bookings for
        
        Returns:
            List of bookings on that date
        """
        try:
            time_min = datetime.datetime.combine(date, datetime.time.min)
            time_max = datetime.datetime.combine(date, datetime.time.max)
            
            # Get all bookings and filter by date
            response = requests.get(
                f"{self.api_url}/bookings",
                headers=self.headers,
                params={"apiKey": self.api_key, "take": 100},
                timeout=10
            )
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            bookings = data.get('bookings', [])
            
            formatted_events = []
            for booking in bookings:
                # Skip cancelled bookings
                status = booking.get('status', '').lower()
                if status in ['cancelled', 'rejected', 'canceled']:
                    continue
                
                start_str = booking.get('startTime')
                if start_str:
                    # Parse the start time and check if it's on the target date
                    start_dt = datetime.datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                    if start_dt.date() == date:
                        # Get custom title
                        custom_title = None
                        if booking.get('metadata') and isinstance(booking['metadata'], dict):
                            custom_title = booking['metadata'].get('customTitle')
                        if not custom_title and booking.get('responses'):
                            if isinstance(booking['responses'], dict):
                                custom_title = booking['responses'].get('title')
                        
                        display_title = custom_title or booking.get('title', 'No Title')
                        
                        formatted_events.append({
                            'id': booking.get('id'),
                            'summary': display_title,
                            'start': start_str,
                            'end': booking.get('endTime'),
                            'description': booking.get('description', ''),
                            'location': booking.get('location', ''),
                            'link': booking.get('link', '')
                        })
            
            return formatted_events
        except Exception as error:
            print(f'An error occurred: {error}')
            return []
