import streamlit as st
import datetime
import uuid

class User:
    def __init__(self, user_id, name, email, preferences=None):
        self.user_id = user_id
        self.name = name
        self.email = email
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
        self.resources = {}

    def register_user(self, name, email):
        user_id = self._generate_unique_id()
        new_user = User(user_id, name, email)
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
        if st.button("Login"):
            for user in self.support_service.users.values():
                if user.email == email:
                    self.user = user
                    st.success(f"Logged in as {user.name}!")
                    break
            else:
                st.error("Invalid email.")

    def handle_registration(self):
        name = st.text_input("Name")
        email = st.text_input("Email")
        if st.button("Register"):
            if name and email:
                self.user = self.support_service.register_user(name, email)
                st.success(f"User {self.user.name} registered!")
            else:
                st.error("Please enter name and email.")

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

    # Add some initial resources (for testing)
    support_app.add_resource("Calm Breathing Exercise", "A guided breathing exercise...", "Coping Strategies", "some_link")
    support_app.add_resource("National Suicide Prevention Lifeline", "Call or text 988", "Hotlines")
    support_app.add_resource("Find a Therapist", "Directory of therapists", "Therapists", "therapist_link")

    ui = MentalHealthAppUI(support_app)
    ui.run()