import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import euclidean_distances, cosine_similarity
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

class PlayerSimilarityAnalyzer:
    def __init__(self, player_data):
        self.player_data = player_data
        self.scaler = StandardScaler()
        self.numeric_columns = [
            'height', 'weight', 'forty_yard', 'vertical_jump', 
            'broad_jump', 'bench_press', 'shuttle', 'cone'
        ]
        
    def _prepare_features(self, players_df: pd.DataFrame) -> np.ndarray:
        """Prepare and normalize features for similarity calculation"""
        # Select numeric features
        features = players_df[self.numeric_columns].copy()
        
        # Handle missing values with position-specific means
        for col in self.numeric_columns:
            if col in features.columns:
                # Calculate position-specific means
                pos_means = players_df.groupby('position')[col].mean()
                
                # Fill missing values with position-specific means
                for pos in pos_means.index:
                    mask = (players_df['position'] == pos) & (features[col].isna())
                    features.loc[mask, col] = pos_means[pos]
                
                # If still have NaN values, fill with overall mean
                if features[col].isna().any():
                    overall_mean = features[col].mean()
                    features[col].fillna(overall_mean, inplace=True)
        
        # Ensure no NaN values remain
        if features.isna().any().any():
            print("⚠️  Warning: NaN values detected, filling with zeros")
            features = features.fillna(0.0)
        
        # Normalize features
        features_scaled = self.scaler.fit_transform(features)
        
        return features_scaled
    
    def _calculate_position_weights(self, position: str) -> Dict[str, float]:
        """Calculate feature weights based on position importance"""
        weights = {
            'height': 1.0,
            'weight': 1.0,
            'forty_yard': 1.0,
            'vertical_jump': 1.0,
            'broad_jump': 1.0,
            'bench_press': 1.0,
            'shuttle': 1.0,
            'cone': 1.0
        }
        
        # Position-specific weight adjustments
        if position == 'QB':
            weights.update({
                'forty_yard': 1.2,  # Mobility is important for QBs
                'vertical_jump': 0.8,  # Less important for QBs
                'bench_press': 0.7,  # Less important for QBs
            })
        elif position == 'WR':
            weights.update({
                'forty_yard': 1.5,  # Speed is crucial for WRs
                'vertical_jump': 1.3,  # Jumping ability important
                'broad_jump': 1.2,  # Explosiveness
                'height': 1.1,  # Height can be advantageous
            })
        elif position == 'RB':
            weights.update({
                'forty_yard': 1.3,  # Speed important
                'bench_press': 1.2,  # Strength for breaking tackles
                'vertical_jump': 1.1,  # Explosiveness
            })
        elif position == 'TE':
            weights.update({
                'height': 1.3,  # Height is very important for TEs
                'weight': 1.2,  # Size matters
                'bench_press': 1.1,  # Strength for blocking
            })
        elif position in ['OT', 'OG', 'C']:
            weights.update({
                'height': 1.2,  # Height important for O-linemen
                'weight': 1.3,  # Size crucial
                'bench_press': 1.4,  # Strength very important
                'forty_yard': 0.6,  # Speed less important
            })
        elif position in ['EDGE', 'DE', 'DT']:
            weights.update({
                'forty_yard': 1.2,  # Speed important for pass rush
                'bench_press': 1.3,  # Strength important
                'weight': 1.1,  # Size matters
            })
        elif position in ['CB', 'S']:
            weights.update({
                'forty_yard': 1.4,  # Speed crucial for DBs
                'vertical_jump': 1.2,  # Jumping ability
                'cone': 1.3,  # Agility very important
                'shuttle': 1.2,  # Change of direction
            })
        
        return weights
    
    def find_similar_players(self, player_name: str, num_similar: int = 3, 
                           same_position_only: bool = True, position: str = None) -> List[Dict]:
        """
        Find the most similar players to the given player
        
        IMPORTANT: By default, this function only compares players within the same position
        for meaningful comparisons. Cross-position comparisons are not recommended as
        different positions have vastly different physical requirements and combine standards.
        
        The system uses a tiered approach:
        - Tier 1: Players with complete combine data (all 8 stats)
        - Tier 2: Players with partial combine data (some athletic tests)
        - Tier 3: Players with only height/weight data
        
        Args:
            player_name: Name of the player to find similarities for
            num_similar: Number of similar players to return
            same_position_only: Whether to only compare within same position (default: True)
            position: Specific position to use for dual position players (e.g., 'CB' or 'WR')
            
        Returns:
            List of dictionaries with player info and similarity scores
        """
        # Get the target player's data
        if position:
            # For dual position players, get the specific position entry
            player_entries = self.player_data.players[
                (self.player_data.players['name'] == player_name) & 
                (self.player_data.players['position'] == position)
            ]
            if player_entries.empty:
                return []
            target_player = player_entries.iloc[0].to_dict()
        else:
            target_player = self.player_data.get_player_stats(player_name)
            if not target_player:
                return []
        
        target_position = target_player['position']
        
        # Get all players to compare against
        if same_position_only:
            players_df = self.player_data.get_players_by_position(target_position)
            # Validate that we're only comparing within the same position
            if not players_df.empty and not all(players_df['position'] == target_position):
                print(f"⚠️  Warning: Found players with different positions. Filtering to {target_position} only.")
                players_df = players_df[players_df['position'] == target_position]
        else:
            players_df = self.player_data.players
            print("⚠️  Warning: Cross-position comparisons may not be meaningful due to different physical requirements.")
        
        # Remove the target player from comparison
        players_df = players_df[players_df['name'] != player_name].copy()
        
        if players_df.empty:
            return []
        
        # Determine target player's data tier
        target_tier = self._get_player_data_tier(target_player)
        print(f"📊 {player_name} data tier: {target_tier}")
        
        # Categorize comparison players by data tier
        tier_1_players = self._get_tier_1_players(players_df)
        tier_2_players = self._get_tier_2_players(players_df)
        tier_3_players = self._get_tier_3_players(players_df)
        
        print(f"📈 Available comparison players:")
        print(f"   Tier 1 (Complete): {len(tier_1_players)}")
        print(f"   Tier 2 (Partial): {len(tier_2_players)}")
        print(f"   Tier 3 (Height/Weight only): {len(tier_3_players)}")
        
        # Find similar players based on target tier
        if target_tier == 1 and len(tier_1_players) > 0:
            # Target has complete data, prefer complete data comparisons
            similar_players = self._find_similar_in_tier(target_player, tier_1_players, num_similar)
            if len(similar_players) < num_similar and len(tier_2_players) > 0:
                # Supplement with tier 2 players
                additional = self._find_similar_in_tier(target_player, tier_2_players, num_similar - len(similar_players))
                similar_players.extend(additional)
        elif target_tier == 2 and len(tier_2_players) > 0:
            # Target has partial data, prefer partial data comparisons
            similar_players = self._find_similar_in_tier(target_player, tier_2_players, num_similar)
            if len(similar_players) < num_similar and len(tier_1_players) > 0:
                # Supplement with tier 1 players
                additional = self._find_similar_in_tier(target_player, tier_1_players, num_similar - len(similar_players))
                similar_players.extend(additional)
        elif target_tier == 3 and len(tier_3_players) > 0:
            # Target has only height/weight, use height/weight only comparisons
            similar_players = self._find_similar_in_tier(target_player, tier_3_players, num_similar)
            if len(similar_players) < num_similar and len(tier_2_players) > 0:
                # Supplement with tier 2 players
                additional = self._find_similar_in_tier(target_player, tier_2_players, num_similar - len(similar_players))
                similar_players.extend(additional)
        else:
            # Fallback: use whatever data is available
            all_players = pd.concat([tier_1_players, tier_2_players, tier_3_players])
            similar_players = self._find_similar_in_tier(target_player, all_players, num_similar)
        
        # Sort by similarity score and return
        similar_players.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similar_players[:num_similar]
    
    def _get_player_data_tier(self, player: Dict) -> int:
        """Determine the data tier of a player based on available combine data"""
        combine_stats = ['forty_yard', 'vertical_jump', 'broad_jump', 'bench_press', 'shuttle', 'cone']
        
        # Count non-null athletic stats
        available_stats = sum(1 for stat in combine_stats if not pd.isna(player.get(stat)))
        
        if available_stats >= 4:  # Most athletic tests available
            return 1
        elif available_stats >= 1:  # Some athletic tests available
            return 2
        else:  # Only height/weight available
            return 3
    
    def _get_tier_1_players(self, players_df: pd.DataFrame) -> pd.DataFrame:
        """Get players with complete combine data (4+ athletic tests)"""
        combine_stats = ['forty_yard', 'vertical_jump', 'broad_jump', 'bench_press', 'shuttle', 'cone']
        available_stats = players_df[combine_stats].notna().sum(axis=1)
        return players_df[available_stats >= 4].copy()
    
    def _get_tier_2_players(self, players_df: pd.DataFrame) -> pd.DataFrame:
        """Get players with partial combine data (1-3 athletic tests)"""
        combine_stats = ['forty_yard', 'vertical_jump', 'broad_jump', 'bench_press', 'shuttle', 'cone']
        available_stats = players_df[combine_stats].notna().sum(axis=1)
        return players_df[(available_stats >= 1) & (available_stats < 4)].copy()
    
    def _get_tier_3_players(self, players_df: pd.DataFrame) -> pd.DataFrame:
        """Get players with only height/weight data"""
        combine_stats = ['forty_yard', 'vertical_jump', 'broad_jump', 'bench_press', 'shuttle', 'cone']
        available_stats = players_df[combine_stats].notna().sum(axis=1)
        return players_df[available_stats == 0].copy()
    
    def _find_similar_in_tier(self, target_player: Dict, players_df: pd.DataFrame, num_similar: int) -> List[Dict]:
        """Find similar players within a specific data tier"""
        if players_df.empty:
            return []
        
        # Determine which stats to use based on available data
        target_tier = self._get_player_data_tier(target_player)
        
        if target_tier == 1:
            # Use all combine stats
            self.numeric_columns = ['height', 'weight', 'forty_yard', 'vertical_jump', 
                                   'broad_jump', 'bench_press', 'shuttle', 'cone']
        elif target_tier == 2:
            # Use only the stats that the target player has
            self.numeric_columns = ['height', 'weight']
            combine_stats = ['forty_yard', 'vertical_jump', 'broad_jump', 'bench_press', 'shuttle', 'cone']
            for stat in combine_stats:
                if not pd.isna(target_player.get(stat)):
                    self.numeric_columns.append(stat)
        else:  # Tier 3
            # Use only height and weight
            self.numeric_columns = ['height', 'weight']
        
        # Prepare features for this tier
        features_scaled = self._prepare_features(players_df)
        
        # Get position-specific weights
        weights = self._calculate_position_weights(target_player['position'])
        weight_vector = np.array([weights[col] for col in self.numeric_columns])
        
        # Apply weights to features
        features_weighted = features_scaled * weight_vector
        
        # Get target player features
        target_features = np.array([target_player[col] for col in self.numeric_columns])
        
        # Handle NaN values in target player features
        if np.isnan(target_features).any():
            # Fill with position-specific means
            for i, col in enumerate(self.numeric_columns):
                if np.isnan(target_features[i]):
                    pos_mean = players_df[col].mean()
                    target_features[i] = pos_mean
        
        # Ensure no NaN values remain
        if np.isnan(target_features).any():
            target_features = np.nan_to_num(target_features, nan=0.0)
        
        target_features_scaled = self.scaler.transform([target_features])[0]
        target_features_weighted = target_features_scaled * weight_vector
        
        # Calculate distances
        distances = euclidean_distances([target_features_weighted], features_weighted)[0]
        
        # Calculate similarity scores (inverse of distance)
        similarity_scores = 1 / (1 + distances)
        
        # Create results
        results = []
        for i, (_, player) in enumerate(players_df.iterrows()):
            results.append({
                'name': player['name'],
                'position': player['position'],
                'college': player['college'],
                'draft_year': player.get('draft_year', 'N/A'),
                'similarity_score': similarity_scores[i],
                'data_tier': self._get_player_data_tier(player),
                'stats': {
                    'height': player['height'],
                    'weight': player['weight'],
                    'forty_yard': player['forty_yard'],
                    'vertical_jump': player['vertical_jump'],
                    'broad_jump': player['broad_jump'],
                    'bench_press': player['bench_press'],
                    'shuttle': player['shuttle'],
                    'cone': player['cone']
                }
            })
        
        # Sort by similarity score (highest first)
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return results[:num_similar]
    
    def get_comparison_summary(self, player_name: str, similar_players: List[Dict]) -> Dict:
        """Create a summary comparison between the target player and similar players"""
        target_player = self.player_data.get_player_stats(player_name)
        if not target_player:
            return {}
        
        summary = {
            'target_player': {
                'name': target_player['name'],
                'position': target_player['position'],
                'college': target_player['college'],
                'stats': {col: target_player[col] for col in self.numeric_columns}
            },
            'similar_players': similar_players,
            'comparison_metrics': {}
        }
        
        # Calculate average stats of similar players for comparison
        avg_stats = {}
        for col in self.numeric_columns:
            values = [player['stats'][col] for player in similar_players]
            avg_stats[col] = np.mean(values)
        
        summary['comparison_metrics']['average_similar_player_stats'] = avg_stats
        
        # Calculate differences
        differences = {}
        for col in self.numeric_columns:
            target_val = target_player[col]
            avg_val = avg_stats[col]
            differences[col] = {
                'target': target_val,
                'average': avg_val,
                'difference': target_val - avg_val,
                'percent_difference': ((target_val - avg_val) / avg_val) * 100 if avg_val != 0 else 0
            }
        
        summary['comparison_metrics']['differences'] = differences
        
        return summary
    
    def get_similarity_explanation(self, player_name: str, similar_player: Dict) -> str:
        """Generate a human-readable explanation of why players are similar"""
        target_player = self.player_data.get_player_stats(player_name)
        if not target_player:
            return ""
        
        explanations = []
        similarity_score = similar_player['similarity_score']
        
        # Overall similarity
        if similarity_score > 0.9:
            explanations.append(f"{similar_player['name']} is extremely similar to {player_name}")
        elif similarity_score > 0.8:
            explanations.append(f"{similar_player['name']} is very similar to {player_name}")
        elif similarity_score > 0.7:
            explanations.append(f"{similar_player['name']} is quite similar to {player_name}")
        else:
            explanations.append(f"{similar_player['name']} shows some similarities to {player_name}")
        
        # Specific stat comparisons
        stat_comparisons = []
        for col in self.numeric_columns:
            target_val = target_player[col]
            similar_val = similar_player['stats'][col]
            diff = abs(target_val - similar_val)
            
            # Determine if this stat is particularly similar
            if col == 'forty_yard' and diff < 0.1:
                stat_comparisons.append(f"Both have similar 40-yard dash times ({target_val:.1f}s vs {similar_val:.1f}s)")
            elif col == 'height' and diff <= 1:
                stat_comparisons.append(f"Similar height ({target_val}\" vs {similar_val}\")")
            elif col == 'weight' and diff <= 10:
                stat_comparisons.append(f"Similar weight ({target_val} lbs vs {similar_val} lbs)")
            elif col == 'vertical_jump' and diff <= 2:
                stat_comparisons.append(f"Similar vertical jump ({target_val}\" vs {similar_val}\")")
            elif col == 'bench_press' and diff <= 2:
                stat_comparisons.append(f"Similar bench press strength ({target_val} reps vs {similar_val} reps)")
        
        if stat_comparisons:
            explanations.append("Key similarities include: " + "; ".join(stat_comparisons[:3]))
        
        return " ".join(explanations) 