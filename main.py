import streamlit as st
import datetime
import uuid
import hashlib
import os
import random

# Function to hash passwords securely (unchanged)
def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)  # Generate a random salt
    salted_password = salt + password.encode('utf-8')
    hashed_password = hashlib.sha256(salted_password).hexdigest()
    return salt, hashed_password

# Function to verify passwords (unchanged)
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

# User, Resource, and SupportService classes (no changes here, same as your existing code)

class MentalHealthAppUI:
    def __init__(self, support_service):
        self.support_service = support_service
        self.user = None

    def run(self):
        st.title("Mental Health Support App")

        if self.user is None:
            self.show_login_or_register()
        else:
            self.show_main_menu()

    def show_login_or_register(self):
        choice = st.radio("Login or Register?", ("Login", "Register"))

        if choice == "Login":
            self.handle_login()
        else:
            self.handle_registration()

    def handle_login(self):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = self.support_service.authenticate_user(email, password)
            if user:
                self.user = user
                st.success(f"Logged in as {user.name}!")
                st.experimental_rerun() # Refresh to show the main menu
            else:
                st.error("Invalid email or password.")

    def handle_registration(self):
        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")  # Password field
        password_confirm = st.text_input("Confirm Password", type="password")


        if st.button("Register"):
            if name and email and password and password == password_confirm:
                self.user = self.support_service.register_user(name, email, password)
                st.success(f"User {self.user.name} registered!")
                st.experimental_rerun() # Refresh to show the main menu
            elif password != password_confirm:
                st.error("Passwords do not match.")
            else:
                st.error("Please enter all the required information.")

    def show_main_menu(self):
        st.sidebar.title("Menu")
        selection = st.sidebar.radio("Choose an action", ("Resources", "Support", "History", "Preferences", "Panic Attack", "Logout"))

        if selection == "Resources":
            self.show_resources()
        elif selection == "Support":
            self.request_support()
        elif selection == "History":
            self.show_history()
        elif selection == "Preferences":
            self.edit_preferences()
        elif selection == "Panic Attack":
            self.handle_panic_attack()
        elif selection == "Logout":
            self.user = None
            st.experimental_rerun()

    def show_resources(self):
        category = st.selectbox("Select a resource category", ["Coping Strategies", "Hotlines", "Therapists"])
        resources = self.support_service.get_resources_by_category(category)
        for resource in resources:
            st.write(f"**{resource.name}**")
            st.write(resource.description)
            if resource.link:
                st.write(f"[Link]({resource.link})")
            st.write("---")

    def request_support(self):
        support_type = st.selectbox("Select support type", ["Guided Meditation", "Crisis Hotline", "Chat with a Therapist"])
        if st.button("Request Support"):
            self.support_service.provide_support(self.user.user_id, support_type)
            st.success(f"Support request for {support_type} sent.")

    def show_history(self):
        st.subheader("Support History")
        if self.user.support_history:
            for interaction in self.user.support_history:
                st.write(f"{interaction['timestamp']}: {interaction['type']}")
                if interaction.get('details'):
                    st.write(f"Details: {interaction['details']}")
                st.write("---")
        else:
            st.write("No support history yet.")

    def edit_preferences(self):
        st.subheader("Preferences")
        notification_time = st.time_input("Notification Time", value=datetime.time(8, 00))
        reminder_frequency = st.selectbox("Reminder Frequency", ["Daily", "Weekly"])

        if st.button("Save Preferences"):
            self.user.update_preferences(notification_time=notification_time.strftime("%H:%M"), reminder_frequency=reminder_frequency)
            st.success("Preferences updated!")
            st.write(self.user.preferences)

    # New Panic Attack Feature
    def handle_panic_attack(self):
        st.subheader("Panic Attack Coping Mechanisms")
        
        # Button for random coping mechanism
        if st.button("Get Coping Mechanism"):
            coping_mechanism = get_random_coping_mechanism()
            st.write(f"Here's a coping mechanism to try: {coping_mechanism}")

        # Chatbox for users to express how they feel
        user_feelings = st.text_area("How do you feel?", placeholder="Type your thoughts here...")
        if st.button("Submit Feelings"):
            if user_feelings:
                st.write(f"Your feelings: {user_feelings}")
                # You can log the feelings or do any processing here
                st.success("Feelings submitted. You're not alone!")
            else:
                st.error("Please enter something to share your feelings.")

if __name__ == "__main__":
    support_app = SupportService()

    # Add some initial users (for testing)
    support_app.register_user("Test User", "test@example.com", "password")
    support_app.register_user("Another User", "another@example.com", "another_password")

    ui = MentalHealthAppUI(support_app)
    ui.run()
