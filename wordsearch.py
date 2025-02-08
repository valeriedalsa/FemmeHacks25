import streamlit as st
import random

# Expanded list of affirmation words
affirmations = [
    "WORTHY", "STRONG", "LOVED", "BRAVE", "UNIQUE", "CAPABLE", "RESILIENT", 
    "BRILLIANT", "CREATIVE", "DETERMINED", "POWERFUL", "CONFIDENT", "AUTHENTIC", 
    "INSPIRING", "PASSIONATE", "TALENTED", "SUCCESSFUL", "BEAUTIFUL", "AMAZING", "JOYFUL"
]

def create_wordsearch(words, size=10):
    grid = [[' ' for _ in range(size)] for _ in range(size)]
    directions = [(0, 1), (1, 0), (1, 1), (-1, 1)]  # Right, Down, Diagonal Right-Down, Diagonal Right-Up
    placed_words = []
    
    for word in words:
        placed = False
        attempts = 0
        while not placed and attempts < 100:
            direction = random.choice(directions)
            dx, dy = direction
            x = random.randint(0, size - 1)
            y = random.randint(0, size - 1)
            
            if 0 <= x + dx * (len(word) - 1) < size and 0 <= y + dy * (len(word) - 1) < size:
                if all(grid[y + dy * i][x + dx * i] in (' ', word[i]) for i in range(len(word))):
                    for i in range(len(word)):
                        grid[y + dy * i][x + dx * i] = word[i]
                    placed_words.append((word, x, y, direction))
                    placed = True
            attempts += 1
    
    for i in range(size):
        for j in range(size):
            if grid[i][j] == ' ':
                grid[i][j] = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    
    return grid, placed_words

st.title("Affirmation Word Search")

# Generate new word search on each page load
if 'grid' not in st.session_state or st.button("New Word Search"):
    # Select 5 random words from the affirmations list
    selected_words = random.sample(affirmations, 5)
    st.session_state.grid, st.session_state.placed_words = create_wordsearch(selected_words)
    st.session_state.reveal = False

grid = st.session_state.grid
placed_words = st.session_state.placed_words

st.write("Word Search Grid:")

# Create a set of highlighted cells
highlighted_cells = set()
if st.session_state.reveal:
    for word, x, y, (dx, dy) in placed_words:
        for i in range(len(word)):
            highlighted_cells.add((y + dy * i, x + dx * i))

# CSS for the grid
st.markdown("""
<style>
    .word-search-grid {
        display: grid;
        grid-template-columns: repeat(10, 1fr);
        gap: 5px;
    }
    .grid-cell {
        width: 30px;
        height: 30px;
        display: flex;
        justify-content: center;
        align-items: center;
        font-weight: bold;
        border: 1px solid #ddd;
    }
    .highlighted {
        box-shadow: 0 0 10px rgba(0,0,255,0.5);
    }
</style>
""", unsafe_allow_html=True)

# Display the grid
grid_html = '<div class="word-search-grid">'
for i in range(10):
    for j in range(10):
        cell_value = grid[i][j]
        highlight_class = "highlighted" if (i, j) in highlighted_cells else ""
        grid_html += f'<div class="grid-cell {highlight_class}">{cell_value}</div>'
grid_html += '</div>'

st.markdown(grid_html, unsafe_allow_html=True)

st.subheader("Find These Words:")
for word, _, _, _ in placed_words:
    st.write(f"- {word}")

if st.button("Reveal Answers"):
    st.session_state.reveal = True
    st.rerun()

if st.session_state.reveal:
    st.subheader("Answers:")
    for word, x, y, (dx, dy) in placed_words:
        direction = 'Right' if dx == 0 else 'Down' if dy == 0 else 'Diagonal'
        st.write(f"{word}: Starts at ({x+1}, {y+1}), Direction: {direction}")