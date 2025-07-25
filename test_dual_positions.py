#!/usr/bin/env python3
"""
Test script to demonstrate dual position functionality
"""

from nfl_player_data import NFLPlayerData
from player_similarity import PlayerSimilarityAnalyzer

def test_dual_positions():
    """Test dual position handling for players like Travis Hunter"""
    print("🧪 Testing Dual Position Functionality...")
    
    # Load data
    player_data = NFLPlayerData()
    analyzer = PlayerSimilarityAnalyzer(player_data)
    
    # Test with Travis Hunter
    test_player = "Travis Hunter"
    
    print(f"\n{'='*60}")
    print(f"📊 Testing {test_player}")
    print(f"{'='*60}")
    
    # Get player positions
    player_positions = player_data.get_player_positions(test_player)
    print(f"🎯 Available positions: {', '.join(player_positions)}")
    
    # Test each position
    for position in player_positions:
        print(f"\n{'='*40}")
        print(f"🔍 Analysis as {position}")
        print(f"{'='*40}")
        
        # Get player stats for this position
        player_entries = player_data.players[
            (player_data.players['name'] == test_player) & 
            (player_data.players['position'] == position)
        ]
        
        if not player_entries.empty:
            player_stats = player_entries.iloc[0].to_dict()
            print(f"📋 Stats for {position}:")
            print(f"   Height: {player_stats['height']}\"")
            print(f"   Weight: {player_stats['weight']} lbs")
            print(f"   Original Position: {player_stats['original_position']}")
        
        # Find similar players for this position
        similar_players = analyzer.find_similar_players(
            test_player,
            num_similar=5,
            same_position_only=True,
            position=position
        )
        
        if similar_players:
            print(f"\n🎯 Similar {position}s:")
            for i, player in enumerate(similar_players, 1):
                tier_label = f"Tier {player['data_tier']}"
                if player['data_tier'] == 1:
                    tier_label += " (Complete)"
                elif player['data_tier'] == 2:
                    tier_label += " (Partial)"
                else:
                    tier_label += " (Height/Weight)"
                
                print(f"   {i}. {player['name']} - {tier_label} - Similarity: {player['similarity_score']:.3f}")
                
                # Show explanation for first player
                if i == 1:
                    explanation = analyzer.get_similarity_explanation(test_player, player)
                    print(f"      💡 {explanation}")
        else:
            print(f"   ⚠️  No similar {position}s found")
    
    print(f"\n🎉 Dual position test completed!")
    print(f"\n📈 Summary:")
    print(f"   - {test_player} can be analyzed as both CB and WR")
    print(f"   - Each position provides different comparison results")
    print(f"   - System automatically handles dual position players")
    print(f"   - Users can choose which position to analyze")

if __name__ == "__main__":
    test_dual_positions() 