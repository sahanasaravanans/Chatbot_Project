from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import csv_models as cm

class User(UserMixin):
    def __init__(self, id=None, username=None, email=None, first_name=None, 
                 last_name=None, graduation_year=None, is_admin=False, password_hash=None):
        self.id = id
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.graduation_year = graduation_year
        self.is_admin = is_admin
        self.password_hash = password_hash

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        return self.password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def save(self):
        if self.id is None:
            # This is a new user
            users = cm.get_all_users()
            if users:
                self.id = max(int(u.id) for u in users) + 1
            else:
                self.id = 1
                
        cm.save_user(self)
        return self
    
    @classmethod
    def get_by_id(cls, user_id):
        return cm.get_user_by_id(user_id)
    
    @classmethod
    def get_by_username(cls, username):
        return cm.get_user_by_username(username)
    
    @classmethod
    def get_by_email(cls, email):
        return cm.get_user_by_email(email)
    
    @classmethod
    def get_all(cls):
        return cm.get_all_users()


class Event:
    def __init__(self, id=None, title=None, description=None, date=None, location=None):
        self.id = id
        self.title = title
        self.description = description
        self.date = date
        self.location = location
    
    def save(self):
        if self.id is None:
            # This is a new event
            events = cm.get_all_events()
            if events:
                self.id = max(int(e.id) for e in events) + 1
            else:
                self.id = 1
                
        cm.save_event(self)
        return self
    
    @classmethod
    def get_by_id(cls, event_id):
        return cm.get_event_by_id(event_id)
    
    @classmethod
    def get_all(cls):
        return cm.get_all_events()
    
    @classmethod
    def get_upcoming_events(cls):
        all_events = cm.get_all_events()
        now = datetime.now()
        return [event for event in all_events if event.date >= now]
    
    @classmethod
    def get_past_events(cls):
        all_events = cm.get_all_events()
        now = datetime.now()
        return [event for event in all_events if event.date < now]


class EventRegistration:
    def __init__(self, id=None, user_id=None, event_id=None):
        self.id = id
        self.user_id = user_id
        self.event_id = event_id
    
    def save(self):
        if self.id is None:
            # This is a new registration
            registrations = cm.get_all_event_registrations()
            if registrations:
                self.id = max(int(r.id) for r in registrations) + 1
            else:
                self.id = 1
                
        cm.save_event_registration(self)
        return self
    
    @classmethod
    def get_by_id(cls, reg_id):
        return cm.get_event_registration_by_id(reg_id)
    
    @classmethod
    def get_by_user_and_event(cls, user_id, event_id):
        return cm.get_event_registration_by_user_and_event(user_id, event_id)
    
    @classmethod
    def get_by_user(cls, user_id):
        return cm.get_event_registrations_by_user(user_id)
    
    @classmethod
    def get_by_event(cls, event_id):
        return cm.get_event_registrations_by_event(event_id)
    
    @classmethod
    def get_all(cls):
        return cm.get_all_event_registrations()


class ChatHistory:
    def __init__(self, id=None, user_id=None, query=None, response=None, timestamp=None):
        self.id = id
        self.user_id = user_id
        self.query = query
        self.response = response
        self.timestamp = timestamp if timestamp else datetime.now()
    
    def save(self):
        if self.id is None:
            # This is a new chat history entry
            entries = cm.get_all_chat_history()
            if entries:
                self.id = max(int(e.id) for e in entries) + 1
            else:
                self.id = 1
                
        cm.save_chat_history(self)
        return self
    
    @classmethod
    def get_by_id(cls, entry_id):
        return cm.get_chat_history_by_id(entry_id)
    
    @classmethod
    def get_by_user(cls, user_id):
        return cm.get_chat_history_by_user(user_id)
    
    @classmethod
    def get_all(cls):
        return cm.get_all_chat_history()
