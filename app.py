import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
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

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .player-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    .similarity-score {
        font-size: 1.2rem;
        font-weight: bold;
        color: #28a745;
    }
    .stat-comparison {
        background-color: #e9ecef;
        border-radius: 8px;
        padding: 0.5rem;
        margin: 0.25rem 0;
    }
    .metric-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-weight: bold;
        color: #495057;
    }
    .metric-value {
        color: #1f77b4;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_data():
    """Load player data and analyzer"""
    player_data = NFLPlayerData()
    analyzer = PlayerSimilarityAnalyzer(player_data)
    return player_data, analyzer

def create_radar_chart(target_player, similar_players):
    """Create a radar chart comparing player statistics"""
    # Prepare data for radar chart
    categories = ['Height', 'Weight', '40-Yard', 'Vertical', 'Broad Jump', 'Bench', 'Shuttle', 'Cone']
    
    # Normalize values for better visualization
    def normalize_stats(stats):
        # Create normalized values (0-100 scale)
        normalized = {}
        normalized['Height'] = (stats['height'] - 65) / (85 - 65) * 100  # 65-85 inches
        normalized['Weight'] = (stats['weight'] - 150) / (350 - 150) * 100  # 150-350 lbs
        normalized['40-Yard'] = (5.5 - stats['forty_yard']) / (5.5 - 4.0) * 100  # 4.0-5.5 seconds (inverted)
        normalized['Vertical'] = (stats['vertical_jump'] - 20) / (45 - 20) * 100  # 20-45 inches
        normalized['Broad Jump'] = (stats['broad_jump'] - 90) / (140 - 90) * 100  # 90-140 inches
        normalized['Bench'] = (stats['bench_press'] - 5) / (35 - 5) * 100  # 5-35 reps
        normalized['Shuttle'] = (5.5 - stats['shuttle']) / (5.5 - 3.5) * 100  # 3.5-5.5 seconds (inverted)
        normalized['Cone'] = (8.5 - stats['cone']) / (8.5 - 6.0) * 100  # 6.0-8.5 seconds (inverted)
        return normalized
    
    # Create radar chart
    fig = go.Figure()
    
    # Add target player
    target_normalized = normalize_stats(target_player['stats'])
    fig.add_trace(go.Scatterpolar(
        r=list(target_normalized.values()),
        theta=categories,
        fill='toself',
        name=target_player['name'],
        line_color='#1f77b4',
        fillcolor='rgba(31, 119, 180, 0.3)'
    ))
    
    # Add similar players
    colors = ['#ff7f0e', '#2ca02c', '#d62728']
    for i, player in enumerate(similar_players[:3]):
        player_normalized = normalize_stats(player['stats'])
        fig.add_trace(go.Scatterpolar(
            r=list(player_normalized.values()),
            theta=categories,
            fill='toself',
            name=f"{player['name']} ({player['similarity_score']:.2f})",
            line_color=colors[i],
            fillcolor=f'rgba{tuple(int(colors[i][1:][j:j+2], 16) for j in (0, 2, 4)) + (0.2,)}'
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="Player Statistics Comparison (Normalized)",
        height=600
    )
    
    return fig

def create_stat_comparison_chart(target_player, similar_players):
    """Create a bar chart comparing specific statistics"""
    stats_to_compare = ['height', 'weight', 'forty_yard', 'vertical_jump', 'broad_jump', 'bench_press']
    stat_labels = ['Height (in)', 'Weight (lbs)', '40-Yard (s)', 'Vertical (in)', 'Broad Jump (in)', 'Bench Press (reps)']
    
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=stat_labels,
        specs=[[{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}]]
    )
    
    players = [target_player] + similar_players[:3]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    for i, stat in enumerate(stats_to_compare):
        row = (i // 3) + 1
        col = (i % 3) + 1
        
        values = [player['stats'][stat] for player in players]
        names = [player['name'] for player in players]
        
        fig.add_trace(
            go.Bar(
                x=names,
                y=values,
                marker_color=colors[:len(players)],
                name=stat_labels[i],
                showlegend=False
            ),
            row=row, col=col
        )
    
    fig.update_layout(
        height=600,
        title_text="Statistical Comparison",
        showlegend=False
    )
    
    return fig

def main():
    # Load data
    player_data, analyzer = load_data()
    
    # Header
    st.markdown('<h1 class="main-header">🏈 NFL Player Comparison Tool</h1>', unsafe_allow_html=True)
    st.markdown("### Find the most similar NFL draft prospects based on combine statistics")
    
    # Sidebar for player selection
    st.sidebar.header("Player Selection")
    
    # Position filter
    positions = player_data.get_all_positions()
    selected_position = st.sidebar.selectbox(
        "Filter by Position:",
        ["All Positions"] + positions
    )
    
    # Player selection
    if selected_position == "All Positions":
        player_names = player_data.get_player_names()
    else:
        player_names = player_data.get_player_names(selected_position)
    
    selected_player = st.sidebar.selectbox(
        "Select a Player:",
        player_names,
        index=0
    )
    
    # Check if selected player has dual positions
    player_positions = player_data.get_player_positions(selected_player)
    analysis_position = selected_position
    
    if len(player_positions) > 1:
        st.sidebar.info(f"🔄 **{selected_player}** has multiple positions: {', '.join(player_positions)}")
        analysis_position = st.sidebar.selectbox(
            "Analyze as which position?",
            player_positions,
            help="Choose which position to use for comparison analysis"
        )
    
    # Analysis options
    st.sidebar.header("Analysis Options")
    num_similar = st.sidebar.slider("Number of similar players:", 2, 5, 3)
    st.sidebar.markdown("### 🔒 Comparison Settings")
    same_position_only = st.sidebar.checkbox(
        "Compare within same position only (Recommended)", 
        value=True,
        help="Only compare players within the same position for meaningful results. Cross-position comparisons may not be accurate due to different physical requirements."
    )
    
    # Main content
    if selected_player:
        # Get player stats
        player_stats = player_data.get_player_stats(selected_player)
        
        # Display selected player info
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"""
            <div class="player-card">
                <h3>{player_stats['name']}</h3>
                <p><strong>Position:</strong> {player_stats['position']}</p>
                <p><strong>College:</strong> {player_stats['college']}</p>
                <p><strong>Draft Year:</strong> {player_stats['draft_year']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Player statistics
            st.subheader("Player Statistics")
            stats_col1, stats_col2 = st.columns(2)
            
            with stats_col1:
                st.metric("Height", f"{player_stats['height']}\"")
                st.metric("Weight", f"{player_stats['weight']} lbs")
                st.metric("40-Yard Dash", f"{player_stats['forty_yard']}s")
                st.metric("Vertical Jump", f"{player_stats['vertical_jump']}\"")
            
            with stats_col2:
                st.metric("Broad Jump", f"{player_stats['broad_jump']}\"")
                st.metric("Bench Press", f"{player_stats['bench_press']} reps")
                st.metric("Shuttle", f"{player_stats['shuttle']}s")
                st.metric("3-Cone", f"{player_stats['cone']}s")
        
        # Find similar players
        st.markdown("---")
        st.subheader("🔍 Similar Players Analysis")
        
        similar_players = analyzer.find_similar_players(
            selected_player, 
            num_similar=num_similar,
            same_position_only=same_position_only,
            position=analysis_position if len(player_positions) > 1 else None
        )
        
        if similar_players:
            # Display similar players
            st.markdown("### Most Similar Players")
            
            for i, player in enumerate(similar_players):
                col1, col2, col3 = st.columns([2, 1, 3])
                
                with col1:
                    # Determine data tier label
                    tier = player.get('data_tier', 1)
                    if tier == 1:
                        tier_label = "🟢 Complete Data"
                    elif tier == 2:
                        tier_label = "🟡 Partial Data"
                    else:
                        tier_label = "🔴 Height/Weight Only"
                    
                    st.markdown(f"""
                    <div class="player-card">
                        <h4>{player['name']}</h4>
                        <p><strong>Position:</strong> {player['position']}</p>
                        <p><strong>College:</strong> {player['college']}</p>
                        <p><strong>Data Quality:</strong> {tier_label}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="similarity-score">
                        {player['similarity_score']:.3f}
                    </div>
                    <p style="text-align: center; font-size: 0.8rem;">Similarity Score</p>
                    """, unsafe_allow_html=True)
                
                with col3:
                    explanation = analyzer.get_similarity_explanation(selected_player, player)
                    st.markdown(f"""
                    <div class="stat-comparison">
                        <p><strong>Why they're similar:</strong></p>
                        <p>{explanation}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Visualization section
            st.markdown("---")
            st.subheader("📊 Statistical Comparisons")
            
            # Create comparison summary
            comparison_summary = analyzer.get_comparison_summary(selected_player, similar_players)
            
            # Radar chart
            st.markdown("### Athletic Profile Comparison")
            radar_fig = create_radar_chart(comparison_summary['target_player'], similar_players)
            st.plotly_chart(radar_fig, use_container_width=True)
            
            # Bar chart comparison
            st.markdown("### Individual Stat Comparison")
            bar_fig = create_stat_comparison_chart(comparison_summary['target_player'], similar_players)
            st.plotly_chart(bar_fig, use_container_width=True)
            
            # Detailed comparison table
            st.markdown("### Detailed Statistics Comparison")
            
            # Create comparison dataframe
            comparison_data = []
            target_stats = comparison_summary['target_player']['stats']
            
            for stat in ['height', 'weight', 'forty_yard', 'vertical_jump', 'broad_jump', 'bench_press', 'shuttle', 'cone']:
                row = {
                    'Statistic': stat.replace('_', ' ').title(),
                    f"{selected_player}": target_stats[stat]
                }
                
                for player in similar_players:
                    row[player['name']] = player['stats'][stat]
                
                comparison_data.append(row)
            
            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, use_container_width=True)
            
        else:
            st.warning("No similar players found with the current criteria.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.8rem;">
        <p>NFL Player Comparison Tool | Data includes 2024 NFL Draft prospects</p>
        <p>Statistics based on NFL Combine and Pro Day measurements</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 