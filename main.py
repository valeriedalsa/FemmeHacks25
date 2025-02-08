import streamlit as st
import datetime
import uuid
import os
import random
import google.generativeai as genai

# Coping Mechanisms List (for panic attacks)
COPING_MECHANISMS = [
    "Write down three things you’re grateful for.",
    "Tense and relax each muscle group, starting from your toes to your head.",
    " Repeat, 'I choose to focus on what I can control.' You got this.",
    "Let go of worry by repeating the phrase: 'I release what I cannot change.'",
    "Visualize the best-case scenario. Reminder: your anxious thoughts may be overwhelming but may not be as real as they feel.",
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
    if 'flipped' not in st.session_state:
        st.session_state['flipped'] = [False] * len(st.session_state.get('cards', [])) # Ensure flipped is initialized
    if 'selected' not in st.session_state:
        st.session_state['selected'] = []
    if 'matched' not in st.session_state:
        st.session_state['matched'] = []

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
        self.resources = {
            "resource1": Resource("resource1", "Calming Breathing Exercise", "A guided breathing exercise...", "Calming Breathing Exercise", """4-7-8 Technique: 
Sit or lie in a comfortable position.
Inhale through your nose for 4 seconds.
Hold your breath for 7 seconds.
Exhale slowly through your mouth for 8 seconds.
Repeat for several rounds. """),
            "resource2": Resource("resource2", "National Suicide Prevention Lifeline", "Call or text 988", "Hotlines"),
            "resource3": Resource("resource3", "Find a Therapist", "Directory of therapists", "Therapists")
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

        # Load Google API key from Streamlit secrets (recommended) or environment variable
        if "GOOGLE_API_KEY" in st.secrets:
            google_api_key = st.secrets["GOOGLE_API_KEY"]
        elif "GOOGLE_API_KEY" in os.environ:
            google_api_key = os.environ["GOOGLE_API_KEY"]
        else:
            google_api_key = st.text_input("Google API Key", type="password")  # Ask for key

            if not google_api_key:
                st.info(
                    "Please enter your Google API key.  You can find it at https://makersuite.google.com/app/apikey."
                )
                st.stop()  # Stop execution if no key is provided

        # Configure the Google Generative AI API
        genai.configure(api_key=google_api_key)

        # Select the Gemini model
        model = genai.GenerativeModel('gemini-pro')

        # Show title and description for Chatbot
        st.title("💬 Chatbot")
        st.write(
            "This is a simple chatbot that uses Google's Gemini Pro model to generate responses. "
            "To use this app, you need to provide a Google API key, which you can get [here](https://makersuite.google.com/app/apikey)."
        )

        # Initialize the chat session if it doesn't exist
        if "chat_session" not in st.session_state:
            st.session_state.chat_session = model.start_chat(history=[])

        # Display the existing chat messages
        for message in st.session_state.chat_session.history:
            with st.chat_message(message.role):
                st.markdown(message.parts[0].text)

        # Get the user's prompt
        if prompt := st.chat_input("What is up?"):
            # Add user message to the chat
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get response from the model
            try:
                response = st.session_state.chat_session.send_message(prompt)

                # Display the assistant's message
                with st.chat_message("assistant"):
                    st.markdown(response.text)

            except Exception as e:
                st.error(f"An error occurred: {e}")


    def show_resources(self):
        st.header("Mental Health Resources")
        categories = set(resource.category for resource in self.support_service.resources.values())
        selected_category = st.selectbox("Select a category:", categories)
        resources = self.support_service.get_resources_by_category(selected_category)
        for resource in resources:
            st.subheader(resource.name)
            st.write(resource.description)
            if resource.link:
                st.markdown(f"[Learn more]({resource.link})")

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
        if 'flipped' not in st.session_state:
            st.session_state['flipped'] = [False] * len(st.session_state.get('cards', [])) # Ensure flipped is initialized
        if 'selected' not in st.session_state:
            st.session_state['selected'] = []
        if 'matched' not in st.session_state:
            st.session_state['matched'] = []


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
        page = st.sidebar.selectbox("Navigate to", ["Dashboard", "Resources", "Coping Mechanisms", "Games", "Chatbot"])

        if page == "Dashboard":
            self.show_dashboard()
        elif page == "Resources":
            self.show_resources()
        elif page == "Coping Mechanisms":
            self.show_coping_mechanisms()
        elif page == "Games":
            self.show_memory_game()
        elif page == "Chatbot":
            self.show_dashboard() #Using dashboard to get the API Key.

if __name__ == "__main__":
    support_app = SupportService()

    ui = MentalHealthAppUI(support_app)
    ui.run()