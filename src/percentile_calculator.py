import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

class PercentileCalculator:
    """
    Calculate position-specific percentiles for NFL combine statistics.
    Handles "lower is better" metrics (40-yard, shuttle, cone) by inverting percentiles.
    """
    
    def __init__(self, players_df: pd.DataFrame):
        self.players_df = players_df.copy()
        self.percentile_cache = {}
        
        # Define which metrics are "lower is better"
        self.lower_is_better = ['forty_yard', 'shuttle', 'cone']
        
        # All combine metrics
        self.combine_metrics = [
            'height', 'weight', 'forty_yard', 'vertical_jump', 
            'broad_jump', 'bench_press', 'shuttle', 'cone'
        ]
        
        # Calculate percentiles for all positions
        self._calculate_all_percentiles()
    
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
        elif position in ['LB', 'ILB', 'OLB']:
            weights.update({
                'forty_yard': 1.3,  # Speed important for coverage
                'vertical_jump': 1.2,  # Explosiveness
                'broad_jump': 1.1,  # Agility
            })
        elif position in ['CB', 'S', 'FS', 'SS']:
            weights.update({
                'forty_yard': 1.4,  # Speed crucial for DBs
                'vertical_jump': 1.2,  # Jumping ability
                'broad_jump': 1.1,  # Explosiveness
                'height': 0.9,  # Height less important for DBs
            })
        
        return weights
    
    def _calculate_all_percentiles(self):
        """Calculate position-specific percentiles for all metrics"""
        positions = self.players_df['position'].unique()
        
        for position in positions:
            pos_data = self.players_df[self.players_df['position'] == position]
            self.percentile_cache[position] = {}
            
            for metric in self.combine_metrics:
                if metric in pos_data.columns:
                    # Get non-null values for this metric and position
                    metric_data = pos_data[metric].dropna()
                    
                    if len(metric_data) > 0:
                        # Calculate percentiles
                        percentiles = metric_data.rank(pct=True) * 100
                        
                        # For "lower is better" metrics, invert the percentile
                        if metric in self.lower_is_better:
                            percentiles = 100 - percentiles
                        
                        # Store the percentile mapping
                        self.percentile_cache[position][metric] = {
                            'values': metric_data.values,
                            'percentiles': percentiles.values,
                            'min_value': metric_data.min(),
                            'max_value': metric_data.max(),
                            'mean_value': metric_data.mean(),
                            'std_value': metric_data.std()
                        }
    
    def get_player_percentiles(self, player_name: str, position: str = None) -> Dict[str, float]:
        """
        Get position-specific percentiles for a player
        
        Args:
            player_name: Name of the player
            position: Position to use (if None, will use player's position)
            
        Returns:
            Dictionary with metric names as keys and percentiles as values
        """
        # Get player data
        player_data = self.players_df[self.players_df['name'] == player_name]
        
        if player_data.empty:
            return {}
        
        player = player_data.iloc[0]
        if position is None:
            position = player['position']
        
        if position not in self.percentile_cache:
            return {}
        
        percentiles = {}
        
        for metric in self.combine_metrics:
            if metric in player and not pd.isna(player[metric]):
                player_value = player[metric]
                
                # Find the percentile for this value
                metric_cache = self.percentile_cache[position].get(metric)
                if metric_cache:
                    # Find closest value and get its percentile
                    values = metric_cache['values']
                    percs = metric_cache['percentiles']
                    
                    # Find the index of the closest value
                    closest_idx = np.argmin(np.abs(values - player_value))
                    percentile = percs[closest_idx]
                    
                    percentiles[metric] = round(percentile, 1)
        
        return percentiles
    
    def get_ras_score(self, player_name: str, position: str = None) -> float:
        """
        Calculate weighted Athlete Score for a player using position-specific weights
        
        Args:
            player_name: Name of the player
            position: Position to use (if None, will use player's position)
            
        Returns:
            Weighted Athlete Score (weighted average of available percentiles)
        """
        percentiles = self.get_player_percentiles(player_name, position)
        
        if not percentiles:
            return 0.0
        
        # Get player position for weights
        if position is None:
            player_data = self.players_df[self.players_df['name'] == player_name]
            if player_data.empty:
                return 0.0
            position = player_data.iloc[0]['position']
        
        # Get position-specific weights
        weights = self._calculate_position_weights(position)
        
        # Calculate weighted average
        weighted_sum = 0.0
        total_weight = 0.0
        
        for metric, percentile in percentiles.items():
            weight = weights.get(metric, 1.0)
            weighted_sum += percentile * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        # Calculate weighted Athlete Score
        athlete_score = weighted_sum / total_weight
        return round(athlete_score, 1)
    
    def get_percentile_explanation(self, player_name: str, position: str = None) -> str:
        """
        Get a human-readable explanation of a player's percentiles
        
        Args:
            player_name: Name of the player
            position: Position to use (if None, will use player's position)
            
        Returns:
            String explanation of the player's athletic profile
        """
        percentiles = self.get_player_percentiles(player_name, position)
        ras_score = self.get_ras_score(player_name, position)
        
        if not percentiles:
            return "No percentile data available for this player."
        
        # Find strengths and weaknesses
        strengths = [metric for metric, pct in percentiles.items() if pct >= 80]
        weaknesses = [metric for metric, pct in percentiles.items() if pct <= 20]
        
        explanation = f"Overall RAS Score: {ras_score}/100\n\n"
        
        if strengths:
            explanation += f"Strengths: {', '.join(strengths).replace('_', ' ').title()}\n"
        if weaknesses:
            explanation += f"Areas for improvement: {', '.join(weaknesses).replace('_', ' ').title()}\n"
        
        explanation += "\nPosition-specific percentiles:\n"
        for metric, pct in sorted(percentiles.items()):
            metric_name = metric.replace('_', ' ').title()
            explanation += f"  {metric_name}: {pct}th percentile\n"
        
        return explanation
    
    def get_position_stats(self, position: str) -> Dict[str, Dict]:
        """
        Get statistical summary for a position
        
        Args:
            position: Position to analyze
            
        Returns:
            Dictionary with metric statistics for the position
        """
        if position not in self.percentile_cache:
            return {}
        
        stats = {}
        for metric, cache in self.percentile_cache[position].items():
            stats[metric] = {
                'min': cache['min_value'],
                'max': cache['max_value'],
                'mean': cache['mean_value'],
                'std': cache['std_value'],
                'count': len(cache['values'])
            }
        
        return stats
    
    def get_similar_percentile_players(self, player_name: str, position: str = None, 
                                     num_similar: int = 5) -> List[Dict]:
        """
        Find players with similar percentile profiles
        
        Args:
            player_name: Name of the target player
            position: Position to use (if None, will use player's position)
            num_similar: Number of similar players to return
            
        Returns:
            List of similar players with their percentile profiles
        """
        target_percentiles = self.get_player_percentiles(player_name, position)
        
        if not target_percentiles:
            return []
        
        if position is None:
            player_data = self.players_df[self.players_df['name'] == player_name]
            if not player_data.empty:
                position = player_data.iloc[0]['position']
        
        if position not in self.percentile_cache:
            return []
        
        # Get all players in the same position
        pos_players = self.players_df[self.players_df['position'] == position]
        
        similarities = []
        
        for _, player in pos_players.iterrows():
            if player['name'] == player_name:
                continue
            
            player_percentiles = self.get_player_percentiles(player['name'], position)
            
            if not player_percentiles:
                continue
            
            # Calculate similarity based on shared metrics
            shared_metrics = set(target_percentiles.keys()) & set(player_percentiles.keys())
            
            if len(shared_metrics) < 2:  # Need at least 2 metrics to compare
                continue
            
            # Calculate average absolute difference in percentiles
            total_diff = 0
            for metric in shared_metrics:
                diff = abs(target_percentiles[metric] - player_percentiles[metric])
                total_diff += diff
            
            avg_diff = total_diff / len(shared_metrics)
            similarity_score = max(0, 100 - avg_diff)  # Convert to similarity score
            
            similarities.append({
                'name': player['name'],
                'position': player['position'],
                'college': player.get('college', 'N/A'),
                'draft_year': player.get('draft_year', 'N/A'),
                'similarity_score': similarity_score,
                'percentiles': player_percentiles,
                'ras_score': self.get_ras_score(player['name'], position),
                'shared_metrics': len(shared_metrics)
            })
        
        # Sort by similarity score and return top results
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similarities[:num_similar] 