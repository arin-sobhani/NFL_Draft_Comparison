#!/usr/bin/env python3
"""
NFL Player Comparison Tool - Command Line Interface
A simple CLI version for quick player comparisons
"""

import sys
from nfl_player_data import NFLPlayerData
from player_similarity import PlayerSimilarityAnalyzer

def print_header():
    """Print application header"""
    print("=" * 60)
    print("🏈 NFL PLAYER COMPARISON TOOL")
    print("=" * 60)
    print()

def print_player_stats(player_stats):
    """Print formatted player statistics"""
    print(f"📊 {player_stats['name']} - {player_stats['position']} ({player_stats['college']})")
    print("-" * 50)
    print(f"Height: {player_stats['height']}\"")
    print(f"Weight: {player_stats['weight']} lbs")
    print(f"40-Yard Dash: {player_stats['forty_yard']}s")
    print(f"Vertical Jump: {player_stats['vertical_jump']}\"")
    print(f"Broad Jump: {player_stats['broad_jump']}\"")
    print(f"Bench Press: {player_stats['bench_press']} reps")
    print(f"Shuttle: {player_stats['shuttle']}s")
    print(f"3-Cone: {player_stats['cone']}s")
    print()

def print_similar_players(similar_players, target_name):
    """Print similar players with explanations"""
    print(f"🔍 Most Similar Players to {target_name}:")
    print("=" * 60)
    
    for i, player in enumerate(similar_players, 1):
        print(f"\n{i}. {player['name']} - {player['position']} ({player['college']})")
        print(f"   Similarity Score: {player['similarity_score']:.3f}")
        print(f"   Height: {player['stats']['height']}\" | Weight: {player['stats']['weight']} lbs")
        print(f"   40-Yard: {player['stats']['forty_yard']}s | Vertical: {player['stats']['vertical_jump']}\"")
        print(f"   Bench: {player['stats']['bench_press']} reps | Shuttle: {player['stats']['shuttle']}s")
        print()

def get_user_choice(options, prompt):
    """Get user choice from a list of options"""
    while True:
        print(prompt)
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        
        try:
            choice = int(input("\nEnter your choice (number): ")) - 1
            if 0 <= choice < len(options):
                return options[choice]
            else:
                print("❌ Invalid choice. Please try again.\n")
        except ValueError:
            print("❌ Please enter a valid number.\n")

def main():
    """Main CLI application"""
    print_header()
    
    # Load data
    print("Loading player database...")
    player_data = NFLPlayerData()
    analyzer = PlayerSimilarityAnalyzer(player_data)
    print("✅ Database loaded successfully!\n")
    
    while True:
        try:
            # Get position filter
            positions = ["All Positions"] + player_data.get_all_positions()
            selected_position = get_user_choice(positions, "Select position to filter by:")
            
            # Get player list
            if selected_position == "All Positions":
                player_names = player_data.get_player_names()
            else:
                player_names = player_data.get_player_names(selected_position)
            
            # Get player selection
            selected_player = get_user_choice(player_names, f"Select a {selected_position.lower()} player:")
            
            # Check if selected player has dual positions
            player_positions = player_data.get_player_positions(selected_player)
            analysis_position = selected_position
            
            if len(player_positions) > 1:
                print(f"\n🔄 **{selected_player}** has multiple positions: {', '.join(player_positions)}")
                print("💡 You can analyze this player in different positions for different comparisons!")
                
                position_choice = get_user_choice(player_positions, "Analyze as which position?")
                analysis_position = position_choice
            
            # Get analysis options
            print("\n" + "=" * 40)
            print("ANALYSIS OPTIONS")
            print("=" * 40)
            
            num_similar = int(input("Number of similar players to find (2-5): "))
            if num_similar < 2 or num_similar > 5:
                num_similar = 3
                print(f"Using default value: {num_similar}")
            
            print("\n🔒 Comparison Settings:")
            print("   Cross-position comparisons may not be meaningful due to different physical requirements.")
            same_position_only = input("Compare within same position only? (y/n, default=y): ").lower()
            if same_position_only == '':
                same_position_only = 'y'
            same_position_only = same_position_only.startswith('y')
            
            # Perform analysis
            print(f"\n🔍 Analyzing similarities for {selected_player} as {analysis_position}...")
            similar_players = analyzer.find_similar_players(
                selected_player,
                num_similar=num_similar,
                same_position_only=same_position_only,
                position=analysis_position if len(player_positions) > 1 else None
            )
            
            # Display results
            print("\n" + "=" * 60)
            player_stats = player_data.get_player_stats(selected_player)
            print_player_stats(player_stats)
            
            if similar_players:
                print_similar_players(similar_players, selected_player)
                
                # Show detailed comparison
                print("📈 DETAILED COMPARISON")
                print("=" * 60)
                
                comparison_summary = analyzer.get_comparison_summary(selected_player, similar_players)
                
                # Print comparison table
                print(f"{'Statistic':<15} {selected_player:<20}", end="")
                for player in similar_players:
                    print(f"{player['name']:<20}", end="")
                print()
                print("-" * 80)
                
                stats_to_show = ['height', 'weight', 'forty_yard', 'vertical_jump', 'broad_jump', 'bench_press']
                for stat in stats_to_show:
                    stat_label = stat.replace('_', ' ').title()
                    target_val = player_stats[stat]
                    print(f"{stat_label:<15} {target_val:<20}", end="")
                    for player in similar_players:
                        val = player['stats'][stat]
                        print(f"{val:<20}", end="")
                    print()
                
            else:
                print("❌ No similar players found with the current criteria.")
            
            # Ask if user wants to continue
            print("\n" + "=" * 60)
            continue_choice = input("Would you like to compare another player? (y/n): ").lower()
            if not continue_choice.startswith('y'):
                print("\n👋 Thanks for using the NFL Player Comparison Tool!")
                break
            
            print("\n" + "=" * 60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Thanks for using the NFL Player Comparison Tool!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("Please try again.\n")

if __name__ == "__main__":
    main() 