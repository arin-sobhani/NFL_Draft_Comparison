import streamlit as st
import pandas as pd
import numpy as np
from src.nfl_player_data import NFLPlayerData
from src.player_similarity import PlayerSimilarityAnalyzer

# Page configuration
st.set_page_config(
    page_title="NFL Player Comparison Tool",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Reduce default Streamlit padding */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Reduce spacing around headers */
    .main h1, .main h2, .main h3 {
        margin-top: 0;
        margin-bottom: 0.5rem;
    }
    .main-header {
        text-align: center;
        color: #1f2937;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.25rem;
        margin-top: 0;
    }
    
    .sub-header {
        text-align: center;
        color: #6b7280;
        font-size: 1.1rem;
        margin-bottom: 1rem;
        margin-top: 0;
    }
    
    .search-container {
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    
    .player-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 1.5rem;
        margin-top: 2rem;
    }
    
    .player-card {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease;
    }
    
    .player-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    .player-card.selected {
        border-color: #10b981;
        background: #f0fdf4;
    }
    
    .player-card.similar {
        border-color: #3b82f6;
        background: #eff6ff;
    }
    
    .player-name {
        font-size: 1.25rem;
        font-weight: bold;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    
    .player-info {
        color: #6b7280;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    
    .stat-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.75rem;
    }
    
    .stat-item {
        background: #f9fafb;
        padding: 0.75rem;
        border-radius: 8px;
        text-align: center;
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: #6b7280;
        font-weight: 500;
        margin-bottom: 0.25rem;
    }
    
    .stat-value {
        font-size: 1rem;
        font-weight: bold;
        color: #1f2937;
    }
    
    .similarity-score {
        background: #3b82f6;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .filter-section {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        margin-top: 1rem;
    }
    
    .filter-row {
        display: flex;
        gap: 1rem;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .filter-item {
        flex: 1;
    }
    
    .no-results {
        text-align: center;
        color: #6b7280;
        font-style: italic;
        padding: 2rem;
    }
    
    .stSelectbox > div > div {
        background: white;
    }
    
    .stTextInput > div > div > input {
        background: white;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_data():
    """Load player data and similarity analyzer"""
    try:
        player_data = NFLPlayerData()
        analyzer = PlayerSimilarityAnalyzer(player_data)
        return player_data, analyzer
    except Exception as e:
        st.error(f"Failed to load data: {str(e)}")
        return None, None

def format_player_name(name):
    """Format player name for display"""
    if not name:
        return "Unknown Player"
    return name.title()

def display_player_card(player_data, title="Player", player_name=None, card_type="default", player_metadata=None, analyzer=None):
    """Display a player card with stats and percentiles"""
    # Handle different data structures
    if player_name is None:
        player_name = player_data.get('name', 'Unknown Player')
    
    # Use metadata if provided (for similar players), otherwise use player_data
    if player_metadata:
        position = player_metadata.get('position', 'N/A')
        college = player_metadata.get('college', 'N/A')
        draft_year = player_metadata.get('draft_year', 'N/A')
        draft_info = player_metadata.get('draft_info', '')
    else:
        position = player_data.get('position', 'N/A')
        college = player_data.get('college', 'N/A')
        draft_year = player_data.get('draft_year', 'N/A')
        draft_info = player_data.get('Drafted (tm/rnd/yr)', '')
    
    # Format draft year with team information
    draft_display = str(draft_year) if draft_year != 'N/A' else 'N/A'
    if draft_info and isinstance(draft_info, str) and draft_info.strip():
        # Extract team name from draft info (format: "Team Name / Round / Pick / Year")
        team_part = draft_info.split(' / ')[0] if ' / ' in draft_info else draft_info
        draft_display += f' ({team_part})'
    elif draft_year != 'N/A':
        # If we have a draft year but no draft info, they're likely undrafted
        draft_display += ' (Undrafted)'
    
    # Get percentiles if analyzer is provided
    percentiles = {}
    ras_score = None
    if analyzer and player_name != 'Unknown Player':
        try:
            percentiles = analyzer.get_player_percentiles(player_name, position)
            ras_score = analyzer.get_ras_score(player_name, position)
        except:
            pass
    
    card_class = f"player-card {card_type}"
    
    st.markdown(f"""
    <div class="{card_class}">
        <div class="player-name">{format_player_name(player_name)}</div>
        <div class="player-info">{position} • {college} • {draft_display}</div>
    """, unsafe_allow_html=True)
    
    # Show Athlete Score if available
    if ras_score is not None:
        st.markdown(f"""
        <div style="background: #3b82f6; color: white; padding: 0.5rem; border-radius: 8px; text-align: center; margin: 1rem 0; font-weight: bold;">
            Athlete Score: {ras_score}/100
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="stat-grid">', unsafe_allow_html=True)
    
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
        
        if pd.notna(value) and value is not None and value != '':
            # Player has this stat
            if stat == 'height':
                # Convert inches to feet/inches format
                feet = int(value // 12)
                inches = int(value % 12)
                display_value = f"{feet}'{inches}\""
            elif stat in ['forty_yard', 'shuttle', 'cone']:
                display_value = f"{value:.2f}"
            elif stat in ['weight', 'vertical_jump', 'broad_jump', 'bench_press']:
                display_value = f"{value:.0f}"
            else:
                display_value = str(value)
            
            # Don't show unit for height since it's already in the format
            unit_display = "" if stat == 'height' else f" {unit}"
            
            # Add percentile if available
            percentile_display = ""
            if stat in percentiles:
                percentile = percentiles[stat]
                # Color code based on percentile
                if percentile >= 80:
                    color = "#10b981"  # Green for high percentiles
                elif percentile >= 60:
                    color = "#3b82f6"  # Blue for good percentiles
                elif percentile >= 40:
                    color = "#f59e0b"  # Orange for average percentiles
                else:
                    color = "#ef4444"  # Red for low percentiles
                
                percentile_display = f'<div style="color: {color}; font-size: 0.8rem; font-weight: bold;">({percentile}%)</div>'
            
            st.markdown(f"""
            <div class="stat-item">
                <div class="stat-label">{label}</div>
                <div class="stat-value">{display_value}{unit_display}</div>
                {percentile_display}
            </div>
            """, unsafe_allow_html=True)
        else:
            # Player is missing this stat - show "Did not participate"
            st.markdown(f"""
            <div class="stat-item">
                <div class="stat-label">{label}</div>
                <div class="stat-value" style="color: #9ca3af; font-style: italic;">Did not participate</div>
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
    
    # Single autocomplete search bar
    search_term = st.text_input("Search players:", placeholder="Type a player name (e.g., Caleb Williams, Travis Hunter...)")
    
    # Filter players based on search term
    if search_term:
        filtered_players = [name for name in all_players if search_term.lower() in name.lower()]
        # Limit results for better performance
        if len(filtered_players) > 50:
            filtered_players = filtered_players[:50]
    else:
        filtered_players = all_players[:20]  # Show first 20 players when no search term
    
    # Player selection from filtered results
    if filtered_players:
        selected_player = st.selectbox("Select from results:", filtered_players, index=0, label_visibility="collapsed")
    else:
        selected_player = None
        st.warning("No players found matching your search.")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Display selected player and similar players
    if selected_player:
        # Get player stats
        player_stats = player_data.get_player_stats(selected_player)
        if player_stats:
            # Find similar players
            with st.spinner("Finding similar players..."):
                similar_players = analyzer.find_similar_players(
                    selected_player, 
                    num_similar=2, 
                    same_position_only=True
                )
            
            if similar_players:
                # Create side-by-side layout
                st.markdown("### 📊 Player Comparison")
                
                # Create three columns for the layout
                col1, col2, col3 = st.columns(3)
                
                # Selected player in left column
                with col1:
                    st.markdown('<div class="similarity-score">Selected Player</div>', unsafe_allow_html=True)
                    display_player_card(player_stats, "Selected", selected_player, "selected", analyzer=analyzer)
                
                # Similar players in right columns
                for i, similar in enumerate(similar_players):
                    if i == 0:
                        col = col2
                    else:
                        col = col3
                    
                    with col:
                        similarity_percent = similar['similarity_score'] * 100
                        st.markdown(f'<div class="similarity-score">{similarity_percent:.1f}% Similar</div>', unsafe_allow_html=True)
                        # Pass player metadata separately for similar players
                        player_metadata = {
                            'position': similar['position'],
                            'college': similar['college'],
                            'draft_year': similar.get('draft_year', 'N/A'),
                            'draft_info': similar.get('Drafted (tm/rnd/yr)', '')
                        }
                        display_player_card(similar['stats'], f"Similar Player {i+1}", similar['name'], "similar", player_metadata, analyzer=analyzer)
            else:
                st.warning("No similar players found with the current criteria.")
        else:
            st.error("Could not load player statistics.")
    
    # Advanced search section (collapsible)
    with st.expander("🔧 Advanced Search & Filters", expanded=False):
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        
        # Create filter columns
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            # Position filter
            positions = ['All Positions'] + sorted(player_data.get_all_positions())
            filter_position = st.selectbox("Position:", positions)
            
            # Draft year filter
            years = ['All Years'] + [str(year) for year in range(2025, 1999, -1)]
            filter_year = st.selectbox("Draft Year:", years)
        
        with filter_col2:
            # Height filter
            height_range = st.slider("Height Range (inches):", 60, 85, (70, 75))
            
            # Weight filter
            weight_range = st.slider("Weight Range (lbs):", 150, 400, (200, 250))
        
        with filter_col3:
            # 40-yard dash filter
            forty_range = st.slider("40-Yard Dash (seconds):", 4.0, 6.0, (4.5, 5.0), 0.1)
            
            # Sort options
            sort_options = ['Name', 'Draft Year', 'Height', 'Weight', '40-Yard Dash', 'Vertical Jump']
            sort_by = st.selectbox("Sort by:", sort_options)
        
        # Sort direction
        sort_direction = st.selectbox("Sort direction:", ['Ascending', 'Descending'])
        
        # Apply advanced filters
        if st.button("🔍 Apply Advanced Filters"):
            # Filter players based on advanced criteria
            filtered_players = []
            
            for player_name in all_players:
                stats = player_data.get_player_stats(player_name)
                if not stats:
                    continue
                
                # Apply filters
                if filter_position != 'All Positions' and stats.get('position') != filter_position:
                    continue
                
                if filter_year != 'All Years' and str(stats.get('draft_year', '')) != filter_year:
                    continue
                
                height = stats.get('height')
                if height and (height < height_range[0] or height > height_range[1]):
                    continue
                
                weight = stats.get('weight')
                if weight and (weight < weight_range[0] or weight > weight_range[1]):
                    continue
                
                forty = stats.get('forty_yard')
                if forty and (forty < forty_range[0] or forty > forty_range[1]):
                    continue
                
                filtered_players.append((player_name, stats))
            
            # Sort results
            if sort_by == 'Name':
                filtered_players.sort(key=lambda x: x[0])
            elif sort_by == 'Draft Year':
                filtered_players.sort(key=lambda x: x[1].get('draft_year', 0))
            elif sort_by == 'Height':
                filtered_players.sort(key=lambda x: x[1].get('height', 0))
            elif sort_by == 'Weight':
                filtered_players.sort(key=lambda x: x[1].get('weight', 0))
            elif sort_by == '40-Yard Dash':
                filtered_players.sort(key=lambda x: x[1].get('forty_yard', 10))
            elif sort_by == 'Vertical Jump':
                filtered_players.sort(key=lambda x: x[1].get('vertical_jump', 0))
            
            if sort_direction == 'Descending':
                filtered_players.reverse()
            
            # Display filtered results
            if filtered_players:
                st.markdown("### 📊 Filtered Results")
                st.markdown(f"Found **{len(filtered_players)}** players matching your criteria.")
                
                # Display results in a grid
                cols = st.columns(3)
                for i, (player_name, stats) in enumerate(filtered_players[:30]):  # Limit to 30 results
                    with cols[i % 3]:
                        if st.button(f"📋 {player_name}", key=f"filtered_{i}"):
                            st.session_state.selected_player = player_name
                            st.rerun()
                        display_player_card(stats, "Player", player_name, analyzer=analyzer)
            else:
                st.warning("No players found matching your advanced filter criteria.")
    
    # Add percentile explanation below advanced search
    st.markdown("""
    <div style="text-align: center; color: #6b7280; font-size: 0.9rem; margin: 1rem 0; padding: 0.5rem; background: #f9fafb; border-radius: 8px;">
        📊 Percentiles are position-specific comparisons
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 