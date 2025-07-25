import streamlit as st
import pandas as pd
import numpy as np
from nfl_player_data import NFLPlayerData
from player_similarity import PlayerSimilarityAnalyzer

# Page configuration
st.set_page_config(
    page_title="NFL Player Comparison Tool",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean, modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .player-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .similarity-score {
        font-size: 1.1rem;
        font-weight: bold;
        color: #28a745;
        background-color: #d4edda;
        padding: 0.3rem 0.6rem;
        border-radius: 15px;
        display: inline-block;
    }
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 0.5rem;
        margin-top: 1rem;
    }
    .stat-item {
        background-color: #e9ecef;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
    }
    .stat-label {
        font-size: 0.8rem;
        color: #666;
        font-weight: bold;
    }
    .stat-value {
        font-size: 1rem;
        color: #1f77b4;
        font-weight: bold;
    }
    .search-container {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .filter-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_data():
    """Load player data and analyzer"""
    try:
        player_data = NFLPlayerData()
        analyzer = PlayerSimilarityAnalyzer(player_data)
        return player_data, analyzer
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

def format_player_name(name):
    """Format player name for display"""
    return name.title()

def display_player_card(player_data, title="Player", player_name=None):
    """Display a player card with stats"""
    # Handle different data structures
    if player_name is None:
        player_name = player_data.get('name', 'Unknown Player')
    
    position = player_data.get('position', 'N/A')
    college = player_data.get('college', 'N/A')
    draft_year = player_data.get('draft_year', 'N/A')
    
    st.markdown(f"""
    <div class="player-card">
        <h3>{title}: {format_player_name(player_name)}</h3>
        <p><strong>Position:</strong> {position} | <strong>College:</strong> {college} | <strong>Draft Year:</strong> {draft_year}</p>
        <div class="stat-grid">
    """, unsafe_allow_html=True)
    
    # Display key stats
    stats_to_show = [
        ('Height', 'height', 'inches'),
        ('Weight', 'weight', 'lbs'),
        ('40-Yard', 'forty_yard', 'sec'),
        ('Vertical', 'vertical_jump', 'inches'),
        ('Broad Jump', 'broad_jump', 'inches'),
        ('Bench', 'bench_press', 'reps'),
        ('Shuttle', 'shuttle', 'sec'),
        ('Cone', 'cone', 'sec')
    ]
    
    for label, stat, unit in stats_to_show:
        value = player_data.get(stat)
        if pd.notna(value) and value is not None:
            if stat in ['forty_yard', 'shuttle', 'cone']:
                display_value = f"{value:.2f}"
            elif stat in ['height', 'weight', 'vertical_jump', 'broad_jump', 'bench_press']:
                display_value = f"{value:.0f}"
            else:
                display_value = str(value)
            
            st.markdown(f"""
            <div class="stat-item">
                <div class="stat-label">{label}</div>
                <div class="stat-value">{display_value} {unit}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🏈 NFL Player Comparison Tool</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Search and compare NFL players from 2000-2025</p>', unsafe_allow_html=True)
    
    # Load data
    player_data, analyzer = load_data()
    if player_data is None:
        st.error("Failed to load player data. Please check your data files.")
        return
    
    # Main search section
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    st.markdown("### 🔍 Search for a Player")
    
    # Get all player names for search
    all_players = player_data.get_player_names()
    all_players.sort()
    
    # Search bar with autocomplete-like functionality
    search_term = st.text_input("Enter player name:", placeholder="e.g., Caleb Williams, Travis Hunter...")
    
    # Filter players based on search term
    if search_term:
        filtered_players = [name for name in all_players if search_term.lower() in name.lower()]
    else:
        filtered_players = all_players[:50]  # Show first 50 players as suggestions
    
    # Player selection
    if filtered_players:
        selected_player = st.selectbox("Select a player:", filtered_players, index=0 if not search_term else None)
        
        if selected_player:
            # Get player stats
            player_stats = player_data.get_player_stats(selected_player)
            if player_stats:
                # Display selected player
                st.markdown("### 📊 Selected Player")
                display_player_card(player_stats, "Selected", selected_player)
                
                # Find similar players
                st.markdown("### 🔍 Finding Similar Players...")
                with st.spinner("Analyzing player similarities..."):
                    similar_players = analyzer.find_similar_players(
                        selected_player, 
                        num_similar=2, 
                        same_position_only=True
                    )
                
                if similar_players:
                    st.markdown("### 🎯 Similar Players")
                    for i, similar in enumerate(similar_players, 1):
                        st.markdown(f"<div class='similarity-score'>Similarity Score: {similar['similarity_score']:.2f}</div>", unsafe_allow_html=True)
                        display_player_card(similar['stats'], f"Similar Player {i}", similar['name'])
                else:
                    st.warning("No similar players found with the current criteria.")
            else:
                st.error("Could not load player statistics.")
        else:
            st.info("Please select a player to see their details and similar players.")
    else:
        st.warning("No players found matching your search.")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Filtering and sorting section
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.markdown("### 🔧 Advanced Search & Filtering")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Position filter
        positions = ['All Positions'] + player_data.get_all_positions()
        selected_position = st.selectbox("Position:", positions)
    
    with col2:
        # Year range
        years = list(range(2000, 2026))
        selected_year = st.selectbox("Draft Year:", ['All Years'] + years)
    
    with col3:
        # Sort by
        sort_options = ['Name', 'Draft Year', 'Height', 'Weight', '40-Yard Dash', 'Vertical Jump', 'Broad Jump', 'Bench Press']
        sort_by = st.selectbox("Sort by:", sort_options)
    
    # Apply filters and show results
    if st.button("🔍 Apply Filters"):
        # Get filtered players
        if selected_position != 'All Positions':
            filtered_players = player_data.get_player_names(selected_position)
        else:
            filtered_players = player_data.get_player_names()
        
        # Filter by year if selected
        if selected_year != 'All Years':
            all_players_data = player_data.get_players_by_position()
            year_filtered = all_players_data[all_players_data['draft_year'] == selected_year]
            filtered_players = [name for name in filtered_players if name in year_filtered['name'].values]
        
        # Sort players
        if sort_by != 'Name':
            # Get player data for sorting
            players_data = []
            for name in filtered_players:
                stats = player_data.get_player_stats(name)
                if stats:
                    players_data.append(stats)
            
            if players_data:
                df = pd.DataFrame(players_data)
                
                # Map sort options to column names
                sort_mapping = {
                    'Draft Year': 'draft_year',
                    'Height': 'height',
                    'Weight': 'weight',
                    '40-Yard Dash': 'forty_yard',
                    'Vertical Jump': 'vertical_jump',
                    'Broad Jump': 'broad_jump',
                    'Bench Press': 'bench_press'
                }
                
                if sort_by in sort_mapping:
                    sort_column = sort_mapping[sort_by]
                    if sort_column in df.columns:
                        df = df.sort_values(sort_column, na_last=True)
                        filtered_players = df['name'].tolist()
        
        # Display filtered results
        st.markdown(f"### 📋 Filtered Results ({len(filtered_players)} players)")
        
        # Show first 20 results with pagination
        if filtered_players:
            page_size = 20
            total_pages = (len(filtered_players) + page_size - 1) // page_size
            
            if total_pages > 1:
                page = st.selectbox("Page:", range(1, total_pages + 1)) - 1
            else:
                page = 0
            
            start_idx = page * page_size
            end_idx = min(start_idx + page_size, len(filtered_players))
            page_players = filtered_players[start_idx:end_idx]
            
            # Display players in a grid
            cols = st.columns(4)
            for i, player_name in enumerate(page_players):
                col_idx = i % 4
                with cols[col_idx]:
                    if st.button(f"📊 {player_name}", key=f"player_{i}"):
                        # Set the selected player for the main search
                        st.session_state.selected_player = player_name
                        st.rerun()
            
            if total_pages > 1:
                st.markdown(f"Showing {start_idx + 1}-{end_idx} of {len(filtered_players)} players")
        else:
            st.info("No players match the selected filters.")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>🏈 NFL Player Comparison Tool | Data: 2000-2025 NFL Combine Results</p>
        <p>Built with Streamlit • Powered by Machine Learning Similarity Analysis</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 