from flask import render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app import app
from models import User, Event, EventRegistration, ChatHistory
from chatbot import get_bot_response
from datetime import datetime
import json
import os


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.get_by_username(username)
        
        if not user or not user.check_password(password):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        
        login_user(user, remember=True)
        next_page = request.args.get('next')
        
        return redirect(next_page or url_for('dashboard'))
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        graduation_year = request.form.get('graduation_year')
        
        # Check if username or email already exists
        existing_user_by_username = User.get_by_username(username)
        existing_user_by_email = User.get_by_email(email)
        
        if existing_user_by_username or existing_user_by_email:
            flash('Username or email already exists', 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            graduation_year=graduation_year,
            is_admin=False
        )
        new_user.set_password(password)
        new_user.save()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    upcoming_events = Event.get_upcoming_events()
    # Sort upcoming events by date
    upcoming_events.sort(key=lambda x: x.date)
    # Limit to 3 events
    upcoming_events = upcoming_events[:3]
    
    # Get events registered by the current user
    user_registrations = EventRegistration.get_by_user(current_user.id)
    registered_event_ids = [reg.event_id for reg in user_registrations]
    registered_events = [Event.get_by_id(event_id) for event_id in registered_event_ids]
    
    return render_template('dashboard.html', 
                           upcoming_events=upcoming_events, 
                           registered_events=registered_events,
                           user=current_user)


@app.route('/events')
@login_required
def events():
    upcoming_events = Event.get_upcoming_events()
    past_events = Event.get_past_events()
    
    # Sort events by date
    upcoming_events.sort(key=lambda x: x.date)
    past_events.sort(key=lambda x: x.date, reverse=True)
    
    # Get events registered by the current user
    user_registrations = EventRegistration.get_by_user(current_user.id)
    registered_event_ids = [reg.event_id for reg in user_registrations]
    
    return render_template('events.html', 
                           upcoming_events=upcoming_events, 
                           past_events=past_events,
                           registered_events=registered_event_ids)


@app.route('/register_event/<int:event_id>', methods=['POST'])
@login_required
def register_event(event_id):
    # Check if event exists
    event = Event.get_by_id(event_id)
    if not event:
        flash('Event not found', 'danger')
        return redirect(url_for('events'))
    
    # Check if already registered
    existing_reg = EventRegistration.get_by_user_and_event(current_user.id, event_id)
    if existing_reg:
        flash('You are already registered for this event', 'warning')
        return redirect(url_for('events'))
    
    # Register for event
    registration = EventRegistration(user_id=current_user.id, event_id=event_id)
    registration.save()
    
    flash(f'Successfully registered for {event.title}', 'success')
    return redirect(url_for('events'))
    
    
@app.route('/cancel_registration/<int:event_id>', methods=['POST'])
@login_required
def cancel_registration(event_id):
    # Check if event exists
    event = Event.get_by_id(event_id)
    if not event:
        flash('Event not found', 'danger')
        return redirect(url_for('events'))
    
    # Check if registered
    registration = EventRegistration.get_by_user_and_event(current_user.id, event_id)
    if not registration:
        flash('You are not registered for this event', 'warning')
        return redirect(url_for('events'))
    
    # Get all registrations and identify the one to remove
    all_registrations = EventRegistration.get_all()
    
    for i, reg in enumerate(all_registrations):
        if reg.user_id == current_user.id and reg.event_id == event_id:
            # Delete the registration by removing it from the list
            del all_registrations[i]
            
            # Recreate the registrations CSV file without this registration
            import csv
            import os
            
            csv_path = os.path.join('data', 'event_registrations.csv')
            with open(csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'user_id', 'event_id', 'registered_at'])
                for i, reg in enumerate(all_registrations, 1):
                    # Re-index IDs to ensure continuity
                    reg.id = i
                    writer.writerow([reg.id, reg.user_id, reg.event_id, reg.registered_at.strftime('%Y-%m-%d %H:%M:%S')])
            
            flash(f'Successfully cancelled registration for {event.title}', 'success')
            return redirect(url_for('events'))
    
    flash('Error cancelling registration', 'danger')
    return redirect(url_for('events'))


@app.route('/chatbot')
@login_required
def chatbot_page():
    # Get recent chat history
    chat_history = ChatHistory.get_by_user(current_user.id)
    # Sort by timestamp
    chat_history.sort(key=lambda x: x.timestamp)
    # Limit to 10 recent entries
    chat_history = chat_history[-10:] if len(chat_history) > 10 else chat_history
    
    return render_template('chatbot.html', chat_history=chat_history)


@app.route('/api/chatbot', methods=['POST'])
@login_required
def chatbot_api():
    data = request.json
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'error': 'Empty query'}), 400
    
    # Get response from chatbot
    response_data = get_bot_response(query)
    
    # Chat history saving disabled as requested
    
    return jsonify(response_data)


# API route to get all chat history
@app.route('/api/chat_history')
@login_required
def get_chat_history():
    chat_history = ChatHistory.get_by_user(current_user.id)
    # Sort by timestamp
    chat_history.sort(key=lambda x: x.timestamp)
    
    history = []
    for entry in chat_history:
        history.append({
            'id': entry.id,
            'query': entry.query,
            'response': json.loads(entry.response),
            'timestamp': entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify(history)


# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        graduation_year = request.form.get('graduation_year')
        new_password = request.form.get('new_password')
        
        # Validate email
        if email != current_user.email:
            existing_user = User.get_by_email(email)
            if existing_user:
                flash('Email already in use by another account', 'danger')
                return redirect(url_for('edit_profile'))
        
        # Update user
        user = User.get_by_id(current_user.id)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.graduation_year = int(graduation_year)
        
        # Update password if provided
        if new_password and new_password.strip():
            user.set_password(new_password)
            
        # Save changes
        user.save()
        
        flash('Profile updated successfully', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('edit_profile.html', user=current_user)
