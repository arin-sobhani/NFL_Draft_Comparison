import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
import os

class NFLPlayerData:
    def __init__(self, data_file: str = "data/processed_combine_data.csv"):
        self.data_file = data_file
        self.players = self._load_data()
    
    def _load_data(self) -> pd.DataFrame:
        """Load player data from processed CSV file"""
        if os.path.exists(self.data_file):
            try:
                print(f"📊 Loading data from {self.data_file}")
                players = pd.read_csv(self.data_file)
                print(f"✅ Loaded {len(players)} players from processed data")
                
                # Handle dual position players
                players = self._expand_dual_positions(players)
                print(f"📈 Expanded to {len(players)} total entries (including dual positions)")
                
                return players
            except Exception as e:
                print(f"❌ Error loading data file: {e}")
                raise FileNotFoundError(f"Failed to load data from {self.data_file}: {e}")
        else:
            print(f"📁 Data file {self.data_file} not found")
            print("❌ No data available. Please ensure the processed CSV file exists.")
            print("💡 Run 'python3 data_processor.py' to process your CSV files first.")
            raise FileNotFoundError(f"Data file {self.data_file} not found. Please process your CSV files first.")
    
    def _expand_dual_positions(self, players_df: pd.DataFrame) -> pd.DataFrame:
        """Expand dual position players into separate entries for each position"""
        expanded_players = []
        
        for _, player in players_df.iterrows():
            position = player['position']
            
            # Check if player has dual positions (e.g., "CB/WR")
            if '/' in str(position):
                positions = [pos.strip() for pos in position.split('/')]
                print(f"🔄 Expanding {player['name']}: {position} → {positions}")
                
                # Create separate entry for each position
                for pos in positions:
                    player_copy = player.copy()
                    player_copy['position'] = pos
                    player_copy['original_position'] = position  # Keep track of original
                    expanded_players.append(player_copy)
            else:
                # Single position player
                player_copy = player.copy()
                player_copy['original_position'] = position
                expanded_players.append(player_copy)
        
        return pd.DataFrame(expanded_players)
    

    
    def get_players_by_position(self, position: str = None) -> pd.DataFrame:
        """Get players filtered by position"""
        if position:
            return self.players[self.players['position'] == position]
        return self.players
    
    def get_player_names(self, position: str = None) -> List[str]:
        """Get list of player names, optionally filtered by position"""
        players = self.get_players_by_position(position)
        return players['name'].tolist()
    
    def get_player_stats(self, player_name: str) -> Dict:
        """Get statistics for a specific player"""
        player = self.players[self.players['name'] == player_name]
        if player.empty:
            return None
        return player.iloc[0].to_dict()
    
    def get_all_positions(self) -> List[str]:
        """Get list of all available positions"""
        return sorted(self.players['position'].unique().tolist())
    
    def get_player_positions(self, player_name: str) -> List[str]:
        """Get all positions for a specific player (handles dual positions)"""
        player_entries = self.players[self.players['name'] == player_name]
        if player_entries.empty:
            return []
        
        # Return unique positions for this player
        return player_entries['position'].unique().tolist()
    
    def get_data_summary(self) -> Dict:
        """Get summary of the loaded data"""
        return {
            'total_players': len(self.players),
            'years_covered': sorted(self.players['draft_year'].unique().tolist()),
            'positions': self.get_all_positions(),
            'data_source': 'processed_csv'
        } 