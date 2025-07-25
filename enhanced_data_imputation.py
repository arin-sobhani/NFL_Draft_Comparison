#!/usr/bin/env python3
"""
Enhanced Data Imputation System
Combines position-based averages with machine learning predictions
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

class EnhancedDataImputer:
    def __init__(self, player_data):
        self.player_data = player_data
        self.models = {}
        self.scalers = {}
        self.position_averages = {}
        self.feature_columns = ['height', 'weight', 'forty_yard', 'vertical_jump', 
                               'broad_jump', 'bench_press', 'shuttle', 'cone']
        
    def calculate_position_averages(self):
        """Calculate position-specific averages for all combine stats"""
        print("📊 Calculating position-specific averages...")
        
        for position in self.player_data.get_all_positions():
            pos_players = self.player_data.get_players_by_position(position)
            
            averages = {}
            for col in self.feature_columns:
                if col in pos_players.columns:
                    # Calculate mean excluding NaN values
                    valid_values = pos_players[col].dropna()
                    if len(valid_values) > 0:
                        averages[col] = valid_values.mean()
                    else:
                        averages[col] = np.nan
            
            self.position_averages[position] = averages
            
        print(f"✅ Calculated averages for {len(self.position_averages)} positions")
        
    def train_prediction_models(self):
        """Train machine learning models to predict missing stats"""
        print("🤖 Training prediction models...")
        
        # Get players with complete data for training
        complete_data = self.player_data.players[
            self.player_data.players[self.feature_columns].notna().all(axis=1)
        ].copy()
        
        if len(complete_data) < 100:
            print("⚠️  Insufficient complete data for training models")
            return
        
        print(f"📈 Training on {len(complete_data)} complete profiles")
        
        # Train models for each athletic stat
        athletic_stats = ['forty_yard', 'vertical_jump', 'broad_jump', 'bench_press', 'shuttle', 'cone']
        
        for stat in athletic_stats:
            if stat not in complete_data.columns:
                continue
                
            # Prepare features (exclude the target stat and use other available stats)
            feature_cols = [col for col in self.feature_columns if col != stat and col in complete_data.columns]
            
            if len(feature_cols) < 2:
                continue
                
            # Prepare training data
            X = complete_data[feature_cols].dropna()
            y = complete_data.loc[X.index, stat]
            
            if len(X) < 50:
                continue
                
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test_scaled)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            print(f"   {stat}: MAE={mae:.3f}, R²={r2:.3f}")
            
            # Store model and scaler
            self.models[stat] = model
            self.scalers[stat] = scaler
            
        print(f"✅ Trained {len(self.models)} prediction models")
    
    def predict_missing_stats(self, player_row):
        """Predict missing stats for a single player"""
        predictions = {}
        
        # Get available features for this player
        available_features = {}
        for col in self.feature_columns:
            if col in player_row and not pd.isna(player_row[col]):
                available_features[col] = player_row[col]
        
        if len(available_features) < 2:
            return predictions
        
        # Try to predict each missing stat
        for stat in self.models.keys():
            if stat in player_row and pd.isna(player_row[stat]):
                # Get the exact features used during training
                required_features = self.scalers[stat].feature_names_in_
                
                # Check if we have all required features
                missing_required = [f for f in required_features if f not in available_features]
                
                if len(missing_required) == 0:
                    # We have all required features
                    X_input = np.array([[available_features[col] for col in required_features]])
                    X_scaled = self.scalers[stat].transform(X_input)
                    
                    # Make prediction
                    prediction = self.models[stat].predict(X_scaled)[0]
                    
                    # Validate prediction (reasonable bounds)
                    if self._is_reasonable_prediction(stat, prediction):
                        predictions[stat] = prediction
                else:
                    # We're missing some required features, skip this prediction
                    continue
        
        return predictions
    
    def _is_reasonable_prediction(self, stat, value):
        """Check if prediction is within reasonable bounds"""
        bounds = {
            'forty_yard': (3.5, 6.0),      # 40-yard dash in seconds
            'vertical_jump': (20, 50),     # Vertical jump in inches
            'broad_jump': (80, 150),       # Broad jump in inches
            'bench_press': (5, 50),        # Bench press reps
            'shuttle': (3.5, 5.0),         # Shuttle in seconds
            'cone': (6.0, 8.5)             # 3-cone in seconds
        }
        
        if stat in bounds:
            min_val, max_val = bounds[stat]
            return min_val <= value <= max_val
        
        return True
    
    def enhance_player_data(self):
        """Enhance the dataset with imputed values"""
        print("🔄 Enhancing player data with imputed values...")
        
        enhanced_players = []
        total_enhanced = 0
        
        for _, player in self.player_data.players.iterrows():
            player_enhanced = player.copy()
            enhanced_stats = 0
            
            # First, fill with position averages where possible
            position = player['position']
            if position in self.position_averages:
                for stat, avg_value in self.position_averages[position].items():
                    if stat in player and pd.isna(player[stat]) and not pd.isna(avg_value):
                        player_enhanced[stat] = avg_value
                        enhanced_stats += 1
            
            # Then, use ML predictions for remaining missing stats
            ml_predictions = self.predict_missing_stats(player_enhanced)
            for stat, prediction in ml_predictions.items():
                if stat in player and pd.isna(player[stat]):
                    player_enhanced[stat] = prediction
                    enhanced_stats += 1
            
            # Add metadata about enhancement
            player_enhanced['original_missing_stats'] = enhanced_stats
            player_enhanced['data_enhanced'] = enhanced_stats > 0
            
            enhanced_players.append(player_enhanced)
            total_enhanced += enhanced_stats
        
        enhanced_df = pd.DataFrame(enhanced_players)
        
        print(f"✅ Enhanced {total_enhanced} missing stats across {len(enhanced_df)} players")
        print(f"📊 Players with enhanced data: {enhanced_df['data_enhanced'].sum()}")
        
        return enhanced_df
    
    def get_enhancement_summary(self):
        """Get summary of data enhancement"""
        print("\n📈 Data Enhancement Summary")
        print("=" * 50)
        
        # Position averages summary
        print("Position Averages Available:")
        for pos, averages in self.position_averages.items():
            available_stats = sum(1 for v in averages.values() if not pd.isna(v))
            print(f"   {pos}: {available_stats}/6 athletic stats")
        
        # Model summary
        print(f"\nPrediction Models Trained: {len(self.models)}")
        for stat in self.models.keys():
            print(f"   ✅ {stat}")
        
        # Data quality improvement
        original_complete = len(self.player_data.players[
            self.player_data.players[self.feature_columns].notna().all(axis=1)
        ])
        
        print(f"\nOriginal Complete Profiles: {original_complete}")
        print(f"Total Players: {len(self.player_data.players)}")
        print(f"Completion Rate: {original_complete/len(self.player_data.players)*100:.1f}%")

def main():
    """Test the enhanced data imputation system"""
    from nfl_player_data import NFLPlayerData
    
    print("🧪 Testing Enhanced Data Imputation...")
    
    # Load data
    player_data = NFLPlayerData()
    
    # Create imputer
    imputer = EnhancedDataImputer(player_data)
    
    # Calculate position averages
    imputer.calculate_position_averages()
    
    # Train prediction models
    imputer.train_prediction_models()
    
    # Get enhancement summary
    imputer.get_enhancement_summary()
    
    # Test on a few players
    print("\n🔍 Testing Enhancement on Sample Players:")
    
    sample_players = player_data.players[
        player_data.players[['forty_yard', 'vertical_jump', 'broad_jump', 'bench_press', 'shuttle', 'cone']].isna().any(axis=1)
    ].head(3)
    
    for _, player in sample_players.iterrows():
        print(f"\n📊 {player['name']} ({player['position']}):")
        
        # Show original missing stats
        missing_stats = []
        for stat in ['forty_yard', 'vertical_jump', 'broad_jump', 'bench_press', 'shuttle', 'cone']:
            if pd.isna(player[stat]):
                missing_stats.append(stat)
        
        print(f"   Missing: {', '.join(missing_stats) if missing_stats else 'None'}")
        
        # Show predictions
        predictions = imputer.predict_missing_stats(player)
        if predictions:
            print(f"   Predictions:")
            for stat, value in predictions.items():
                print(f"     {stat}: {value:.2f}")
        else:
            print(f"   No predictions possible (insufficient data)")

if __name__ == "__main__":
    main() 