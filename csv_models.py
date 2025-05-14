import csv
import os
import json
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define data directory and ensure it exists
DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

# Define file paths
USERS_FILE = os.path.join(DATA_DIR, 'users.csv')
EVENTS_FILE = os.path.join(DATA_DIR, 'events.csv')
EVENT_REGISTRATIONS_FILE = os.path.join(DATA_DIR, 'event_registrations.csv')
CHAT_HISTORY_FILE = os.path.join(DATA_DIR, 'chat_history.csv')
CHATBOT_DATA_FILE = os.path.join(DATA_DIR, 'chatbot_data.csv')

# Ensure files exist
def ensure_files_exist():
    """Create CSV files with headers if they don't exist"""
    
    # Users file
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'username', 'email', 'first_name', 'last_name', 
                             'graduation_year', 'is_admin', 'password_hash'])
    
    # Events file
    if not os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'title', 'description', 'date', 'location'])
    
    # Event registrations file
    if not os.path.exists(EVENT_REGISTRATIONS_FILE):
        with open(EVENT_REGISTRATIONS_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'user_id', 'event_id'])
    
    # Chat history file
    if not os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'user_id', 'query', 'response', 'timestamp'])
    
    # Create a basic chatbot data file if it doesn't exist
    if not os.path.exists(CHATBOT_DATA_FILE):
        with open(CHATBOT_DATA_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['query', 'response', 'category'])
            # Add some basic responses
            writer.writerow(['What events are coming up?', 
                             'You can check upcoming events on our events page. Would you like me to direct you there?', 
                             'events'])
            writer.writerow(['What are my alumni benefits?', 
                             'As an alumni, you have access to networking events, career services, and library resources.', 
                             'benefits'])
            writer.writerow(['How can I contact the alumni office?', 
                             'You can contact the alumni office at alumni@university.edu or call 555-123-4567.', 
                             'contact'])
            writer.writerow(['When is the next reunion?', 
                             'Reunion events are typically held in the spring. Check the events page for specific dates.', 
                             'events'])

ensure_files_exist()

# Helper functions for datetime
def parse_datetime(dt_str):
    """Parse datetime string from CSV to datetime object"""
    if not dt_str:
        return None
    try:
        return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        logger.error(f"Error parsing datetime: {dt_str}")
        return None

def format_datetime(dt):
    """Format datetime object for storage in CSV"""
    if isinstance(dt, datetime):
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    return str(dt) if dt else ''

# User model functions
def get_all_users():
    """Get all users from the CSV file"""
    from models import User
    
    users = []
    try:
        with open(USERS_FILE, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                user = User(
                    id=row['id'],
                    username=row['username'],
                    email=row['email'],
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    graduation_year=row['graduation_year'],
                    is_admin=row['is_admin'].lower() == 'true',
                    password_hash=row['password_hash']
                )
                users.append(user)
    except Exception as e:
        logger.error(f"Error reading users CSV: {e}")
    
    return users

def get_user_by_id(user_id):
    """Get a user by ID"""
    users = get_all_users()
    for user in users:
        if str(user.id) == str(user_id):
            return user
    return None

def get_user_by_username(username):
    """Get a user by username"""
    users = get_all_users()
    for user in users:
        if user.username == username:
            return user
    return None

def get_user_by_email(email):
    """Get a user by email"""
    users = get_all_users()
    for user in users:
        if user.email == email:
            return user
    return None

def save_user(user):
    """Save a user to the CSV file"""
    users = get_all_users()
    
    # Check if user exists to update or add new
    existing_user = None
    for i, u in enumerate(users):
        if str(u.id) == str(user.id):
            existing_user = i
            break
    
    if existing_user is not None:
        # Update existing user
        users[existing_user] = user
    else:
        # Add new user
        users.append(user)
    
    # Write all users back to CSV
    try:
        with open(USERS_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'username', 'email', 'first_name', 'last_name', 
                            'graduation_year', 'is_admin', 'password_hash'])
            for u in users:
                writer.writerow([
                    u.id, 
                    u.username, 
                    u.email, 
                    u.first_name, 
                    u.last_name, 
                    u.graduation_year, 
                    u.is_admin, 
                    u.password_hash
                ])
        return True
    except Exception as e:
        logger.error(f"Error saving user to CSV: {e}")
        return False

# Event model functions
def get_all_events():
    """Get all events from the CSV file"""
    from models import Event
    
    events = []
    try:
        with open(EVENTS_FILE, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                event = Event(
                    id=row['id'],
                    title=row['title'],
                    description=row['description'],
                    date=parse_datetime(row['date']),
                    location=row['location']
                )
                events.append(event)
    except Exception as e:
        logger.error(f"Error reading events CSV: {e}")
    
    return events

def get_event_by_id(event_id):
    """Get an event by ID"""
    events = get_all_events()
    for event in events:
        if str(event.id) == str(event_id):
            return event
    return None

def save_event(event):
    """Save an event to the CSV file"""
    events = get_all_events()
    
    # Check if event exists to update or add new
    existing_event = None
    for i, e in enumerate(events):
        if str(e.id) == str(event.id):
            existing_event = i
            break
    
    if existing_event is not None:
        # Update existing event
        events[existing_event] = event
    else:
        # Add new event
        events.append(event)
    
    # Write all events back to CSV
    try:
        with open(EVENTS_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'title', 'description', 'date', 'location'])
            for e in events:
                writer.writerow([
                    e.id, 
                    e.title, 
                    e.description, 
                    format_datetime(e.date), 
                    e.location
                ])
        return True
    except Exception as e:
        logger.error(f"Error saving event to CSV: {e}")
        return False

# Event Registration functions
def get_all_event_registrations():
    """Get all event registrations from the CSV file"""
    from models import EventRegistration
    
    registrations = []
    try:
        with open(EVENT_REGISTRATIONS_FILE, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                registration = EventRegistration(
                    id=row['id'],
                    user_id=row['user_id'],
                    event_id=row['event_id']
                )
                registrations.append(registration)
    except Exception as e:
        logger.error(f"Error reading event registrations CSV: {e}")
    
    return registrations

def get_event_registration_by_id(reg_id):
    """Get an event registration by ID"""
    registrations = get_all_event_registrations()
    for reg in registrations:
        if str(reg.id) == str(reg_id):
            return reg
    return None

def get_event_registration_by_user_and_event(user_id, event_id):
    """Get event registration by user and event IDs"""
    registrations = get_all_event_registrations()
    for reg in registrations:
        if str(reg.user_id) == str(user_id) and str(reg.event_id) == str(event_id):
            return reg
    return None

def get_event_registrations_by_user(user_id):
    """Get all event registrations for a user"""
    registrations = get_all_event_registrations()
    return [reg for reg in registrations if str(reg.user_id) == str(user_id)]

def get_event_registrations_by_event(event_id):
    """Get all registrations for an event"""
    registrations = get_all_event_registrations()
    return [reg for reg in registrations if str(reg.event_id) == str(event_id)]

def save_event_registration(registration):
    """Save an event registration to the CSV file"""
    registrations = get_all_event_registrations()
    
    # Check if registration exists to update or add new
    existing_reg = None
    for i, r in enumerate(registrations):
        if str(r.id) == str(registration.id):
            existing_reg = i
            break
    
    if existing_reg is not None:
        # Update existing registration
        registrations[existing_reg] = registration
    else:
        # Add new registration
        registrations.append(registration)
    
    # Write all registrations back to CSV
    try:
        with open(EVENT_REGISTRATIONS_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'user_id', 'event_id'])
            for r in registrations:
                writer.writerow([
                    r.id, 
                    r.user_id, 
                    r.event_id
                ])
        return True
    except Exception as e:
        logger.error(f"Error saving event registration to CSV: {e}")
        return False

# Chat History functions
def get_all_chat_history():
    """Get all chat history from the CSV file"""
    from models import ChatHistory
    
    history = []
    try:
        with open(CHAT_HISTORY_FILE, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                chat = ChatHistory(
                    id=row['id'],
                    user_id=row['user_id'],
                    query=row['query'],
                    response=row['response'],
                    timestamp=parse_datetime(row['timestamp'])
                )
                history.append(chat)
    except Exception as e:
        logger.error(f"Error reading chat history CSV: {e}")
    
    return history

def get_chat_history_by_id(entry_id):
    """Get a chat history entry by ID"""
    history = get_all_chat_history()
    for entry in history:
        if str(entry.id) == str(entry_id):
            return entry
    return None

def get_chat_history_by_user(user_id):
    """Get all chat history for a user"""
    history = get_all_chat_history()
    return [entry for entry in history if str(entry.user_id) == str(user_id)]

def save_chat_history(entry):
    """Save a chat history entry to the CSV file"""
    history = get_all_chat_history()
    
    # Check if entry exists to update or add new
    existing_entry = None
    for i, e in enumerate(history):
        if str(e.id) == str(entry.id):
            existing_entry = i
            break
    
    if existing_entry is not None:
        # Update existing entry
        history[existing_entry] = entry
    else:
        # Add new entry
        history.append(entry)
    
    # Write all entries back to CSV
    try:
        with open(CHAT_HISTORY_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'user_id', 'query', 'response', 'timestamp'])
            for e in history:
                writer.writerow([
                    e.id, 
                    e.user_id, 
                    e.query, 
                    e.response, 
                    format_datetime(e.timestamp)
                ])
        return True
    except Exception as e:
        logger.error(f"Error saving chat history to CSV: {e}")
        return False

# Chatbot data functions
def get_chatbot_data():
    """Get all chatbot data from the CSV file"""
    data = []
    
    # Hardcoded fallback data in case file reading fails
    fallback_data = [
        {
            'query': 'What events are coming up?',
            'response': 'You can check upcoming events on our events page. Would you like me to direct you there?',
            'category': 'events'
        },
        {
            'query': 'What are my alumni benefits?',
            'response': 'As an alumni, you have access to networking events, career services, and library resources.',
            'category': 'benefits'
        },
        {
            'query': 'How can I contact the alumni office?',
            'response': 'You can contact the alumni office at alumni@university.edu or call 555-123-4567.',
            'category': 'contact'
        },
        {
            'query': 'When is the next reunion?',
            'response': 'Reunion events are typically held in the spring. Check the events page for specific dates.',
            'category': 'events'
        }
    ]
    
    try:
        logger.info(f"Attempting to read chatbot data from {CHATBOT_DATA_FILE}")
        
        if not os.path.exists(CHATBOT_DATA_FILE):
            logger.warning(f"Chatbot data file not found at {CHATBOT_DATA_FILE}")
            return fallback_data
        
        with open(CHATBOT_DATA_FILE, 'r', newline='') as file:
            file_content = file.read()
            logger.debug(f"File content preview: {file_content[:200]}")
            
            # Reset file pointer to beginning
            file.seek(0)
            
            reader = csv.DictReader(file)
            
            for row in reader:
                logger.debug(f"Processing row: {row}")
                data.append({
                    'query': row.get('query', ''),
                    'response': row.get('response', ''),
                    'category': row.get('category', '')
                })
                
        logger.info(f"Successfully loaded {len(data)} entries from chatbot data CSV")
    except Exception as e:
        logger.error(f"Error reading chatbot data CSV: {e}", exc_info=True)
        logger.info("Using fallback chatbot data")
        return fallback_data
    
    return data if data else fallback_data
