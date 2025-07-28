import streamlit as st
import pandas as pd
import numpy as np
from src.nfl_player_data import NFLPlayerData
from src.player_similarity import PlayerSimilarityAnalyzer
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(
    page_title="NFL Player Similarity Leaderboard",
    page_icon="🏆",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f2937;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        text-align: center;
        color: #6b7280;
        font-size: 1.1rem;
        margin-bottom: 0.1rem;
        margin-top: 0;
    }
    
    .leaderboard-card {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .similarity-score {
        background: #3b82f6;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 1rem;
        display: inline-block;
    }
    
    .player-pair {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 1rem 0;
        padding: 1rem;
        background: #f9fafb;
        border-radius: 8px;
    }
    
    .player-info {
        text-align: center;
        flex: 1;
    }
    
    .player-name {
        font-size: 1.1rem;
        font-weight: bold;
        color: #1f2937;
        margin-bottom: 0.25rem;
    }
    
    .player-details {
        color: #6b7280;
        font-size: 0.9rem;
    }
    
    .vs-divider {
        font-size: 1.5rem;
        font-weight: bold;
        color: #3b82f6;
        margin: 0 2rem;
    }
    
    .filter-section {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 2rem;
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

def calculate_all_similarities(player_data, analyzer, max_players=100):
    """Calculate similarity scores for all player pairs"""
    all_players = player_data.get_player_names()
    
    # Limit to max_players for performance
    if len(all_players) > max_players:
        all_players = all_players[:max_players]
    
    similarities = []
    
    with st.spinner("Calculating similarity scores for all player pairs..."):
        progress_bar = st.progress(0)
        total_pairs = len(all_players) * (len(all_players) - 1) // 2
        pair_count = 0
        
        for i, player1 in enumerate(all_players):
            for j, player2 in enumerate(all_players[i+1:], i+1):
                # Get player stats
                stats1 = player_data.get_player_stats(player1)
                stats2 = player_data.get_player_stats(player2)
                
                if stats1 and stats2:
                    # Only compare players of the same position
                    if stats1.get('position') == stats2.get('position'):
                        # Find similarity using the analyzer
                        similar_players = analyzer.find_similar_players(
                            player1, 
                            num_similar=len(all_players), 
                            same_position_only=True
                        )
                        
                        # Find player2 in the similar players list
                        for similar in similar_players:
                            if similar['name'] == player2:
                                similarities.append({
                                    'player1': player1,
                                    'player2': player2,
                                    'position': stats1.get('position', 'Unknown'),
                                    'similarity_score': similar['similarity_score'],
                                    'player1_stats': stats1,
                                    'player2_stats': stats2
                                })
                                break
                
                pair_count += 1
                progress_bar.progress(pair_count / total_pairs)
    
    return similarities

def main():
    # Header
    st.markdown('<h1 class="main-header">🏆 NFL Player Similarity Leaderboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Discover the most similar NFL prospects based on combine statistics</p>', unsafe_allow_html=True)
    
    # Back to main app button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏈 Back to Player Comparison", type="secondary", use_container_width=True):
            st.switch_page("simple_app.py")
    
    # Load data
    player_data, analyzer = load_data()
    if player_data is None:
        st.error("Failed to load player data. Please check your data files.")
        return
    
    # Filters section
    st.markdown('<div class="filter-section">', unsafe_allow_html=True)
    st.markdown("### 🔧 Filters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Position filter
        positions = ['All Positions'] + sorted(player_data.get_all_positions())
        filter_position = st.selectbox("Position:", positions)
    
    with col2:
        # Minimum similarity threshold
        min_similarity = st.slider("Minimum Similarity Score:", 0.0, 1.0, 0.7, 0.05)
    
    with col3:
        # Number of results
        num_results = st.slider("Number of Results:", 10, 100, 50)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Calculate similarities button
    if st.button("🏆 Calculate Similarity Leaderboard", type="primary"):
        # Calculate all similarities
        similarities = calculate_all_similarities(player_data, analyzer, max_players=200)
        
        if similarities:
            # Convert to DataFrame for easier filtering
            df = pd.DataFrame(similarities)
            
            # Apply filters
            if filter_position != 'All Positions':
                df = df[df['position'] == filter_position]
            
            df = df[df['similarity_score'] >= min_similarity]
            
            # Sort by similarity score (highest first)
            df = df.sort_values('similarity_score', ascending=False).head(num_results)
            
            if not df.empty:
                st.markdown("### 🏅 Top Similarity Scores")
                
                for idx, row in df.iterrows():
                    similarity_percent = row['similarity_score'] * 100
                    
                    st.markdown(f"""
                    <div class="leaderboard-card">
                        <div style="text-align: center; margin-bottom: 1rem;">
                            <span class="similarity-score">{similarity_percent:.1f}% Similar</span>
                            <div style="color: #6b7280; font-size: 0.9rem; margin-top: 0.5rem;">
                                {row['position']} • #{idx + 1} on Leaderboard
                            </div>
                        </div>
                        
                        <div class="player-pair">
                            <div class="player-info">
                                <div class="player-name">{row['player1']}</div>
                                <div class="player-details">
                                    {row['player1_stats'].get('college', 'N/A')} • 
                                    {row['player1_stats'].get('draft_year', 'N/A')}
                                </div>
                            </div>
                            
                            <div class="vs-divider">VS</div>
                            
                            <div class="player-info">
                                <div class="player-name">{row['player2']}</div>
                                <div class="player-details">
                                    {row['player2_stats'].get('college', 'N/A')} • 
                                    {row['player2_stats'].get('draft_year', 'N/A')}
                                </div>
                            </div>
                        </div>
                        
                        <div style="text-align: center; margin-top: 1rem;">
                            <button onclick="window.open('https://nfldraftcomparison.streamlit.app/?player={row['player1']}', '_blank')" 
                                    style="background: #3b82f6; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer; margin-right: 1rem;">
                                Compare {row['player1']}
                            </button>
                            <button onclick="window.open('https://nfldraftcomparison.streamlit.app/?player={row['player2']}', '_blank')" 
                                    style="background: #3b82f6; color: white; border: none; padding: 0.5rem 1rem; border-radius: 5px; cursor: pointer;">
                                Compare {row['player2']}
                            </button>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No player pairs found matching your criteria.")
        else:
            st.warning("No similarities calculated. Try adjusting your filters.")
    
    # Add explanation
    st.markdown("""
    <div style="text-align: center; color: #6b7280; font-size: 0.9rem; margin: 1rem 0; padding: 0.5rem; background: #f9fafb; border-radius: 8px;">
        📊 Similarity scores are calculated using position-specific weighted combine statistics<br>
        📊 Data used from Pro Football Reference
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 