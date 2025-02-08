import streamlit as st
import datetime
import uuid
import os
import random
import hashlib

# Function to hash passwords securely (Not Needed Anymore)
def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)  # Generate a random salt
    salted_password = salt + password.encode('utf-8')
    hashed_password = hashlib.sha256(salted_password).hexdigest()
    return salt, hashed_password

# Function to verify passwords (Not Needed Anymore)
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

# Memory Game Functions
def init_game():
    emojis = ['🍀', '🌸', '🌙', '☀️', '🌊', '🍂'] * 2  # Matching pairs
    random.shuffle(emojis)
    return emojis, [False] * len(emojis)  # Cards and flipped states

def flip_card(i):
    if not st.session_state.flipped[i] and i not in st.session_state.matched:
        st.session_state.flipped[i] = True
        st.session_state.selected.append(i)

        if len(st.session_state.selected) == 2:
            idx1, idx2 = st.session_state.selected
            if st.session_state.cards[idx1] == st.session_state.cards[idx2]:
                st.session_state.matched.extend([idx1, idx2])  # Store matched indices
            else:
                st.session_state.flipped[idx1] = st.session_state.flipped[idx2] = False
            st.session_state.selected = []

# SupportService Class
class SupportService:
    def __init__(self):
        self.users = {}
        self.resources = {
            "resource1": Resource("resource1", "Calm Breathing Exercise", "A guided breathing exercise...", "Coping Strategies", "some_link"),
            "resource2": Resource("resource2", "National Suicide Prevention Lifeline", "Call or text 988", "Hotlines"),
            "resource3": Resource("resource3", "Find a Therapist", "Directory of therapists", "Therapists", "therapist_link")
        }

    def add_resource(self, name, description, category, link=None):
        resource_id = self._generate_unique_id()
        new_resource = Resource(resource_id, name, description, category, link)
        self.resources[resource_id] = new_resource

    def get_resources_by_category(self, category):
        return [resource for resource in self.resources.values() if resource.category == category]

    def find_resource_by_id(self, resource_id):
        return self.resources.get(resource_id)

    def _generate_unique_id(self):
        return str(uuid.uuid4())

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

class MentalHealthAppUI:
    def __init__(self, support_service):
        self.support_service = support_service

    def show_dashboard(self):
        st.title("Mental Health Support App")
        st.write("Welcome! Here are some resources and tools to support your mental well-being.")

    def show_resources(self):
        st.header("Mental Health Resources in Philadelphia")

        st.subheader("Community Resources")
        st.markdown("- [FIGHT Community Health Centers](https://fight.org/programs-services/community-health-centers/)")
        st.markdown("- [Penn Medicine Community Clinics](https://www.med.upenn.edu/fmch/community-clinics)")
        st.markdown("- [Community Legal Services - Health Centers in Philadelphia](https://clsphila.org/wp-content/uploads/2019/04/RESOURCE-Health-Centers_Philadelphia.pdf)")
        st.markdown("- [Philadelphia Department of Public Health](https://www.phila.gov/departments/department-of-public-health/health-centers/city-health-centers/)")

        st.subheader("Online Affordable Therapy Options")
        st.markdown("- [Open Path Collective](https://openpathcollective.org) -  Sessions range from $30-$70")
        st.markdown("- [A Better Life Therapy](https://abetterlifetherapy.com/lowfeetherapy) - Sessions range from $20-$90")
        st.markdown("- [Thriveworks Philadelphia](https://thriveworks.com/philadelphia-counseling/philadelphia-pa-online-counseling-therapy/)")
        st.markdown("- [Move Forward Counseling LLC](https://moveforwardpa.com/office/online-therapy-in-pennsylvania/)")
        st.markdown("- [The Better You Institute](https://thebetteryouinstitute.com/online-therapy/)")

        st.subheader("Other Mental Health Resources")
        st.markdown("- [Healthy Minds Philly](https://healthymindsphilly.org) - Offers free mental health screenings and resources")
        st.markdown("- [NAMI Philadelphia](https://namiphilly.org/resources/local-resources/) - Provides support groups and local resources")
        st.markdown("- Mental Health Crisis Hotline: 215-685-6440 (Available 24/7)")
        st.markdown("- Suicide and Crisis Lifeline: 988 (Available 24/7)")
        st.markdown("- NET Access Point for Opioid Treatment: 844-533-8200 or 215-408-4987")
        st.markdown("- Intellectual Disability Services: 215-685-5900")

    def show_coping_mechanisms(self):
        st.header("Coping Mechanisms")
        if st.button("Get a Coping Mechanism"):
            mechanism = get_random_coping_mechanism()
            st.write(mechanism)

    def show_memory_game(self):
        st.title("🧠 Memory Game for Anxiety Relief")
        st.write("Find all the matching pairs!")

        if 'cards' not in st.session_state:
            st.session_state.cards, st.session_state.flipped = init_game()
            st.session_state.selected = []
            st.session_state.matched = []

        cols = st.columns(4)  # Create a 4-column grid

        for i, emoji in enumerate(st.session_state.cards):
            with cols[i % 4]:  # Distribute cards in grid
                if st.session_state.flipped[i] or i in st.session_state.matched:
                    st.button(emoji, key=f'card_{i}', disabled=True)
                else:
                    st.button("❓", key=f'card_{i}', on_click=flip_card, args=(i,))

        if len(st.session_state.matched) == len(st.session_state.cards):
            st.success("🎉 You found all the pairs! Great job!")
            if st.button("Restart Game"):
                st.session_state.cards, st.session_state.flipped = init_game()
                st.session_state.selected = []
                st.session_state.matched = []
                st.rerun()

    def run(self):
        # Add a selectbox in the sidebar for navigation
        page = st.sidebar.selectbox("Navigate to", ["Dashboard", "Resources", "Coping Mechanisms", "Games"])

        if page == "Dashboard":
            self.show_dashboard()
        elif page == "Resources":
            self.show_resources()
        elif page == "Coping Mechanisms":
            self.show_coping_mechanisms()
        elif page == "Games":
            self.show_memory_game()

if __name__ == "__main__":
    support_app = SupportService()

    ui = MentalHealthAppUI(support_app)
    ui.run()
