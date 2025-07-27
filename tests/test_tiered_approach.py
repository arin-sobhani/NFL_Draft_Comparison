#!/usr/bin/env python3
"""
Test script to demonstrate the tiered approach for handling players with limited combine data
"""

from nfl_player_data import NFLPlayerData
from player_similarity import PlayerSimilarityAnalyzer

def test_tiered_approach():
    """Test the tiered approach for different data completeness levels"""
    print("🧪 Testing Tiered Approach for Limited Combine Data...")
    
    # Load data
    player_data = NFLPlayerData()
    analyzer = PlayerSimilarityAnalyzer(player_data)
    
    # Test cases representing different data tiers
    test_cases = [
        ("Adrian McPherson", "QB", "Tier 1 - Complete combine data"),
        ("Chris Chaloupka", "QB", "Tier 2 - Partial combine data (40-yard only)"),
        ("Cam Ward", "QB", "Tier 3 - Height/weight only"),
    ]
    
    for player_name, position, description in test_cases:
        print(f"\n{'='*60}")
        print(f"📊 Testing {player_name} ({position})")
        print(f"   {description}")
        print(f"{'='*60}")
        
        # Get player stats
        player_stats = player_data.get_player_stats(player_name)
        if not player_stats:
            print(f"   ❌ Player {player_name} not found")
            continue
        
        # Show available stats
        print(f"\n📋 Available Stats:")
        stats_to_show = ['height', 'weight', 'forty_yard', 'vertical_jump', 'broad_jump', 'bench_press', 'shuttle', 'cone']
        for stat in stats_to_show:
            value = player_stats.get(stat)
            if pd.isna(value):
                print(f"   {stat}: ❌ Missing")
            else:
                print(f"   {stat}: ✅ {value}")
        
        # Find similar players
        similar_players = analyzer.find_similar_players(
            player_name, 
            num_similar=5, 
            same_position_only=True
        )
        
        if similar_players:
            print(f"\n🎯 Similar Players Found:")
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
                    explanation = analyzer.get_similarity_explanation(player_name, player)
                    print(f"      💡 {explanation}")
        else:
            print(f"   ⚠️  No similar players found")
    
    print(f"\n🎉 Tiered approach test completed!")
    print(f"\n📈 Summary:")
    print(f"   - Tier 1: Players with 4+ athletic tests (most accurate comparisons)")
    print(f"   - Tier 2: Players with 1-3 athletic tests (moderate accuracy)")
    print(f"   - Tier 3: Players with only height/weight (basic comparisons)")
    print(f"   - System automatically matches players with similar data completeness")

if __name__ == "__main__":
    import pandas as pd
    test_tiered_approach() 