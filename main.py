import streamlit as st
import datetime
import uuid
import hashlib
import os

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



class User:
    def __init__(self, user_id, name, email, password_salt, password_hash, preferences=None):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password_salt = password_salt # Store the salt
        self.password_hash = password_hash # Store the hashed password
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


class SupportService:
    def __init__(self):
        self.users = {}

        # Example Resources for testing
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
            # Implement the actual support logic here
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
        selection = st.sidebar.radio("Choose an action", ("Resources", "Support", "History", "Preferences", "Logout"))

        if selection == "Resources":
            self.show_resources()
        elif selection == "Support":
            self.request_support()
        elif selection == "History":
            self.show_history()
        elif selection == "Preferences":
            self.edit_preferences()
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


if __name__ == "__main__":
    support_app = SupportService()

    # Add some initial users (for testing)
    support_app.register_user("Test User", "test@example.com", "password")
    support_app.register_user("Another User", "another@example.com", "another_password")


    ui = MentalHealthAppUI(support_app)
    ui.run()