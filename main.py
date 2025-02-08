import streamlit as st
import datetime
import uuid
import hashlib
import os
import random

# Function to hash passwords securely
def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)  # Generate a random salt
    salted_password = salt + password.encode('utf-8')
    hashed_password = hashlib.sha256(salted_password).hexdigest()
    return salt, hashed_password

# Function to verify passwords
def verify_password(stored_salt, stored_hash, password):
    salt = stored_salt
    salted_password = salt + password.encode('utf-8')
    hashed_password = hashlib.sha256(salted_password).hexdigest()
    return hashed_password == stored_hash

# Coping Mechanisms List (for panic attacks)
COPING_MECHANISMS = [
    "Breathe in for 4 counts, hold for 4 counts, and breathe out for 4 counts.",
    "Try to ground yourself by naming 5 things you can see, 4 things you can feel, 3 things you can hear, 2 things you can smell, and 1 thing you can taste.",
    "Focus on your breathing. Inhale for a count of 4, hold for 7, exhale for 8.",
    "Clench your fists tightly for a few seconds, then slowly release them to relieve tension.",
    "Try visualizing a calming scene, like a beach or forest, and focus on the details of it.",
    "Recite a calming affirmation: 'This will pass, I am safe, and I can handle this.'"
]

# Function to select a random coping mechanism
def get_random_coping_mechanism():
    return random.choice(COPING_MECHANISMS)

# SupportService Class (make sure it's defined before usage)
class SupportService:
    def __init__(self):
        self.users = {}
        self.resources = {
            "resource1": Resource("resource1", "Calm Breathing Exercise", "A guided breathing exercise...", "Coping Strategies", "some_link"),
            "resource2": Resource("resource2", "National Suicide Prevention Lifeline", "Call or text 988", "Hotlines"),
            "resource3": Resource("resource3", "Find a Therapist", "Directory of therapists", "Therapists", "therapist_link")
        }

    def register_user(self, name, email, password):
        user_id = self._generate_unique_id()
        salt, hashed_password = hash_password(password)  # Hash the password
        new_user = User(user_id, name, email, salt, hashed_password)
        self.users[user_id] = new_user
        return new_user

    def add_resource(self, name, description, category, link=None):
        resource_id = self._generate_unique_id()
        new_resource = Resource(resource_id, name, description, category, link)
        self.resources[resource_id] = new_resource

    def get_resources_by_category(self, category):
        return [resource for resource in self.resources.values() if resource.category == category]

    def find_resource_by_id(self, resource_id):
        return self.resources.get(resource_id)

    def provide_support(self, user_id, support_type, details=None):
        user = self.users.get(user_id)
        if user:
            user.log_support_interaction(support_type, details)
            st.write(f"Support provided to {user.name} ({support_type})")  # Display in Streamlit
        else:
            st.error("User not found.")

    def _generate_unique_id(self):
        return str(uuid.uuid4())

    def authenticate_user(self, email, password):
        for user_id, user in self.users.items():
            if user.email == email:
                if verify_password(user.password_salt, user.password_hash, password):
                    return user
                else:
                    return None # Incorrect Password
        return None  # User not found

# Define User and Resource classes (unchanged)
class User:
    def __init__(self, user_id, name, email, password_salt, password_hash, preferences=None):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password_salt = password_salt  # Store the salt
        self.password_hash = password_hash  # Store the hashed password
        self.preferences = preferences or {}
        self.support_history = []

    def update_preferences(self, **kwargs):
        self.preferences.update(kwargs)

    def log_support_interaction(self, interaction_type, details=None):
        timestamp = datetime.datetime.now()
        self.support_history.append({"timestamp": timestamp, "type": interaction_type, "details": details})

class Resource:
    def __init__(self, resource_id, name, description, category, link=None):
        self.resource_id = resource_id
        self.name = name
        self.description = description
        self.category = category
        self.link = link

# Now you can create your UI class and app (unchanged)

if __name__ == "__main__":
    support_app = SupportService()

    # Add some initial users (for testing)
    support_app.register_user("Test User", "test@example.com", "password")
    support_app.register_user("Another User", "another@example.com", "another_password")

    ui = MentalHealthAppUI(support_app)
    ui.run()

