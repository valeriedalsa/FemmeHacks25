import streamlit as st
import datetime
import uuid
import os
import random
import google.generativeai as genai
import re

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
def init_game(difficulty):
    """Initializes the memory game based on difficulty."""
    if difficulty == "easy":
        num_pairs = 3
        num_cols = 3
    elif difficulty == "medium":
        num_pairs = 6
        num_cols = 4
    else:  # difficult
        num_pairs = 10
        num_cols = 5

    emojis = ['🐶', '🐱', '🐰', '🐻', '🐼', '🦊', '🦁', '🐯', '🐸', '🐷', '🐨', '🐒', '🐳', '🐞', '🐝', '🦋', '🕷️', '🦂', '🦖', '🦕']
    selected_emojis = random.sample(emojis, num_pairs)
    cards = selected_emojis * 2
    random.shuffle(cards)
    return cards, [False] * len(cards), num_cols


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
        self.google_api_key = self.load_api_key()  # Load API key in the constructor

        if self.google_api_key:
            genai.configure(api_key=self.google_api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None  # Or some other default value
            st.error("Google API Key not found. Please configure it in Streamlit secrets or environment variables.")

        # ---------------------
        # Core: System Prompt
        # ---------------------
        self.SYSTEM_PROMPT = """
        You are a compassionate and supportive mental health chatbot. Your purpose is to provide understanding, encouragement, and resources to users who are experiencing emotional distress.

        Your responses should be:

        *   Empathetic and validating: Acknowledge the user's feelings and experiences.
        *   Supportive and encouraging: Offer hope and encouragement.
        *   Informative: Provide accurate information about mental health topics.
        *   Resourceful: Suggest helpful resources, such as websites, support groups, or crisis hotlines.
        *   Non-judgmental: Create a safe and welcoming space for users to share their feelings.
        *   Respectful:  Use the user's preferred language and tone.
        *   Action oriented :  Suggest coping strategies, but never prescribe medical advice.
        *   Never provide any medical advice. Refer users to qualified mental health professionals if they need it.
        *   If the user expresses suicidal thoughts or plans, immediately direct them to a crisis hotline or emergency services.  (e.g., "If you are in immediate danger, please call 911 or go to your nearest emergency room.").

        You are NOT a substitute for professional mental health care.

        If you are unsure about how to respond, say "I'm not qualified to answer that.  Please consult with a mental health professional."
        """

    # ---------------------
    # Core: Content Filtering (Example)
    # ---------------------
        def is_response_safe(response_text):
            """
            Example content filter (customize to your needs). This is a very basic example and you should refine it.

            Returns True if the response is considered safe, False otherwise.
            """
            # Check for specific keywords or phrases that are red flags.
            unsafe_patterns = [
                r"self-harm",
                r"suicide plan",
                r"harm yourself",
                r"commit suicide",
                r"how to kill myself",  # extremely important
                r"prescribe",  # Avoid giving medical advice
                r"diagnose",
            ]

            for pattern in unsafe_patterns:
                if re.search(pattern, response_text, re.IGNORECASE):  # Case-insensitive search
                    return False

            # Add more sophisticated checks as needed (e.g., sentiment analysis, toxicity detection).

            return True

        self.is_response_safe = is_response_safe # Needed to reference it outside this method.


    def load_api_key(self):
        """Loads the Google API key from Streamlit secrets or environment variable."""
        if "GOOGLE_API_KEY" in st.secrets:
            return st.secrets["GOOGLE_API_KEY"]
        elif "GOOGLE_API_KEY" in os.environ:
            return os.environ["GOOGLE_API_KEY"]
        else:
            return None

    def show_dashboard(self):
        st.title("Mental Health Support App")
        st.write("Welcome! Here are some resources and tools to support your mental well-being.")
        if not self.google_api_key:
            st.warning("Please configure your Google API key in Streamlit secrets or environment variables.")
            st.stop() #Stops the dashboard from loading fully

    def show_chatbot(self):
        if not self.model:
            st.warning("Chatbot is unavailable because the Google API Key is not configured. Please check your configuration.")
            return  # Or handle this case appropriately

        st.title("💬 Mental Health Support Chatbot")
        st.write(
            "This chatbot provides supportive and informative responses for mental health concerns.  "
            "Please remember that it is not a substitute for professional medical advice."
        )

        # Initialize chat history in session state (using only dictionaries)
        if "chat_history" not in st.session_state:  # Use a *separate* key
            st.session_state.chat_history = []  # Initialize as an empty list of dictionaries

        # Display the chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):  # Use the dictionary 'role'
                st.markdown(message["parts"]) # Use the dictionary 'parts'

        # Get the user's prompt
        if prompt := st.chat_input("How can I help you today?"):
            # Add user message to the chat
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get response from the model
            try:
                # Construct the full prompt, including system instructions
                full_prompt = f"{self.SYSTEM_PROMPT}\nUser: {prompt}" # Use self.SYSTEM_PROMPT

                response = self.model.generate_content(full_prompt) #Use generate_content instead

                #Add prompt to the chat history
                st.session_state.chat_history.append({"role": "user", "parts": prompt})

                # Apply content filtering
                if not self.is_response_safe(response.text): # Use self.is_response_safe
                    response.text = "I'm sorry, but I'm unable to respond to that. Please rephrase your question or seek help from a qualified mental health professional."

                 #add the AI response to the chat history
                st.session_state.chat_history.append({"role": "assistant", "parts": response.text})

                # Display the assistant's message
                with st.chat_message("assistant"):
                    st.markdown(response.text)

            except Exception as e:
                st.error(f"An error occurred: {e}")


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

        difficulty = st.radio("Select difficulty:", ["easy", "medium", "difficult"], horizontal=True)

        # Initialize the game based on the selected difficulty.
        if 'difficulty' not in st.session_state or st.session_state.difficulty != difficulty:
            st.session_state.difficulty = difficulty
            st.session_state.cards, st.session_state.flipped, st.session_state.num_cols = init_game(st.session_state.difficulty)
            st.session_state.selected = []
            st.session_state.matched = []

        num_cols = st.session_state.num_cols

        cols = st.columns(num_cols)  # Create columns

        # Custom CSS to make buttons larger
        st.markdown("""
        <style>
        .stButton>button {
            width: 100px;
            height: 100px;
            font-size: 40px;
        }
        </style>
        """, unsafe_allow_html=True)

        for i, emoji in enumerate(st.session_state.cards):
            col_index = i % num_cols
            with cols[col_index]:
                if st.session_state.flipped[i] or i in st.session_state.matched:
                    st.button(emoji, key=f'card_{i}', disabled=True)
                else:
                    st.button("⭐", key=f'card_{i}', on_click=flip_card, args=(i,))

        if len(st.session_state.matched) == len(st.session_state.cards):
            st.success("🎉 You found all the pairs! Great job!")
            #st_confetti(duration=3, key="confetti")  # Trigger confetti #Comment this out if the confetti doesn't work
            st.balloons()

            if st.button("Restart Game"):
                st.session_state.cards, st.session_state.flipped, st.session_state.num_cols = init_game(st.session_state.difficulty)
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
            if not self.model:
                st.warning("Chatbot is unavailable because the Google API Key is not configured. Please check your configuration.")
            else:
                self.show_chatbot()

if __name__ == "__main__":
    support_app = SupportService()

    ui = MentalHealthAppUI(support_app)
    ui.run()