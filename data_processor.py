import pandas as pd
import numpy as np
import os
import re
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class NFLDataProcessor:
    def __init__(self, data_folder: str = "data"):
        self.data_folder = data_folder
        self.combined_data = None
        self.column_mappings = {
            # Name variations
            'name': ['name', 'player_name', 'player', 'full_name', 'fullname'],
            # Position variations
            'position': ['position', 'pos', 'position_group', 'pos_group'],
            # College variations
            'college': ['college', 'school', 'university', 'team', 'college_team'],
            # Draft year variations
            'draft_year': ['draft_year', 'year', 'season', 'draft_season', 'combine_year'],
            # Height variations
            'height': ['height', 'ht', 'height_inches', 'ht_in'],
            # Weight variations
            'weight': ['weight', 'wt', 'weight_lbs', 'wt_lbs'],
            # 40-yard dash variations
            'forty_yard': ['forty_yard', '40_yard', '40yd', 'forty', '40_time', '40_yard_dash'],
            # Vertical jump variations
            'vertical_jump': ['vertical_jump', 'vertical', 'vert', 'vertical_inches', 'vert_in'],
            # Broad jump variations
            'broad_jump': ['broad_jump', 'broad', 'broad_inches', 'broad_jump_inches'],
            # Bench press variations
            'bench_press': ['bench_press', 'bench', 'bench_reps', 'bench_press_reps'],
            # Shuttle variations
            'shuttle': ['shuttle', 'shuttle_time', '20_yard_shuttle', '20_shuttle'],
            # 3-cone variations
            'cone': ['cone', '3_cone', 'three_cone', '3cone', 'three_cone_drill']
        }
    
    def load_csv_files(self) -> pd.DataFrame:
        """Load and combine all CSV files from the data folder"""
        all_data = []
        
        if not os.path.exists(self.data_folder):
            print(f"❌ Data folder '{self.data_folder}' not found!")
            return pd.DataFrame()
        
        # Look for files with pattern 20XXDraftClass.csv
        csv_files = [f for f in os.listdir(self.data_folder) if f.endswith('DraftClass.csv')]
        
        if not csv_files:
            print(f"❌ No DraftClass CSV files found in '{self.data_folder}'")
            return pd.DataFrame()
        
        print(f"📁 Found {len(csv_files)} DraftClass CSV files to process...")
        
        for csv_file in sorted(csv_files):
            file_path = os.path.join(self.data_folder, csv_file)
            try:
                # Extract year from filename (e.g., "2024DraftClass.csv" -> 2024)
                year_match = re.search(r'(\d{4})DraftClass\.csv', csv_file)
                if year_match:
                    year = int(year_match.group(1))
                else:
                    print(f"⚠️  Could not extract year from filename: {csv_file}")
                    continue
                
                # Load CSV
                df = pd.read_csv(file_path)
                print(f"✅ Loaded {csv_file} with {len(df)} players")
                
                # Standardize column names
                df = self._standardize_columns(df)
                
                # Add draft year if not present
                if 'draft_year' not in df.columns:
                    df['draft_year'] = year
                
                # Clean and validate data
                df = self._clean_data(df)
                
                all_data.append(df)
                
            except Exception as e:
                print(f"❌ Error processing {csv_file}: {e}")
                continue
        
        if all_data:
            self.combined_data = pd.concat(all_data, ignore_index=True)
            print(f"🎉 Successfully combined {len(self.combined_data)} total players")
            return self.combined_data
        else:
            print("❌ No data could be loaded")
            return pd.DataFrame()
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map various column names to standard format"""
        # Create mapping from original to standard column names
        column_mapping = {}
        
        # Map the specific columns from your CSV format
        column_mapping.update({
            'Player': 'name',
            'Pos': 'position',
            'School': 'college',
            'Ht': 'height',
            'Wt': 'weight',
            '40yd': 'forty_yard',
            'Vertical': 'vertical_jump',
            'Bench': 'bench_press',
            'Broad Jump': 'broad_jump',
            '3Cone': 'cone',
            'Shuttle': 'shuttle'
        })
        
        # Rename columns
        if column_mapping:
            df = df.rename(columns=column_mapping)
        
        return df
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize data formats"""
        # Handle height conversions (various formats to inches)
        if 'height' in df.columns:
            df['height'] = df['height'].apply(self._convert_height_to_inches)
        
        # Handle weight (ensure it's numeric)
        if 'weight' in df.columns:
            df['weight'] = pd.to_numeric(df['weight'], errors='coerce')
        
        # Handle 40-yard dash times
        if 'forty_yard' in df.columns:
            df['forty_yard'] = df['forty_yard'].apply(self._clean_time)
        
        # Handle other numeric fields
        numeric_fields = ['vertical_jump', 'broad_jump', 'bench_press', 'shuttle', 'cone']
        for field in numeric_fields:
            if field in df.columns:
                df[field] = pd.to_numeric(df[field], errors='coerce')
        
        # Clean position names
        if 'position' in df.columns:
            df['position'] = df['position'].apply(self._standardize_position)
        
        return df
    
    def _convert_height_to_inches(self, height_val) -> Optional[float]:
        """Convert various height formats to inches"""
        if pd.isna(height_val):
            return None
        
        height_str = str(height_val).strip()
        
        # Already in inches (numeric)
        if height_str.replace('.', '').isdigit():
            return float(height_str)
        
        # Format: 6'2" or 6'2 or 6-2
        feet_inches_pattern = r'(\d+)[\'\-](\d+)'
        match = re.search(feet_inches_pattern, height_str)
        if match:
            feet = int(match.group(1))
            inches = int(match.group(2))
            return feet * 12 + inches
        
        # Handle Excel date format (e.g., "4-Jun" = 6'4")
        excel_pattern = r'(\d+)-([A-Za-z]+)'
        match = re.search(excel_pattern, height_str)
        if match:
            feet = int(match.group(1))
            month = match.group(2).lower()
            # Map months to inches (Jan=1, Feb=2, etc.)
            month_to_inches = {
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
            }
            if month in month_to_inches:
                inches = month_to_inches[month]
                return feet * 12 + inches
        
        return None
    
    def _clean_time(self, time_val) -> Optional[float]:
        """Clean time values (remove quotes, convert to float)"""
        if pd.isna(time_val):
            return None
        
        time_str = str(time_val).strip().replace('"', '').replace("'", '')
        
        # Handle format like "4.45" or "4.4"
        if re.match(r'^\d+\.\d+$', time_str):
            return float(time_str)
        
        return None
    
    def _standardize_position(self, pos) -> str:
        """Standardize position names"""
        if pd.isna(pos):
            return "Unknown"
        
        pos_str = str(pos).strip().upper()
        
        # Position mappings
        position_map = {
            'QB': 'QB', 'QUARTERBACK': 'QB',
            'RB': 'RB', 'RUNNING BACK': 'RB', 'HB': 'RB', 'TB': 'RB',
            'WR': 'WR', 'WIDE RECEIVER': 'WR',
            'TE': 'TE', 'TIGHT END': 'TE',
            'OT': 'OT', 'OFFENSIVE TACKLE': 'OT', 'T': 'OT',
            'OG': 'OG', 'OFFENSIVE GUARD': 'OG', 'G': 'OG',
            'C': 'C', 'CENTER': 'C',
            'DE': 'EDGE', 'DEFENSIVE END': 'EDGE', 'EDGE': 'EDGE',
            'DT': 'DT', 'DEFENSIVE TACKLE': 'DT', 'NT': 'DT',
            'LB': 'LB', 'LINEBACKER': 'LB', 'ILB': 'LB', 'OLB': 'LB',
            'CB': 'CB', 'CORNERBACK': 'CB',
            'S': 'S', 'SAFETY': 'S', 'FS': 'S', 'SS': 'S', 'SAF': 'S',
            'K': 'K', 'KICKER': 'K',
            'P': 'P', 'PUNTER': 'P'
        }
        
        return position_map.get(pos_str, pos_str)
    
    def handle_missing_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing combine data using intelligent imputation"""
        print("🔧 Handling missing data...")
        
        # Create a copy to work with
        df_clean = df.copy()
        
        # Calculate position-specific averages for missing data
        combine_stats = ['height', 'weight', 'forty_yard', 'vertical_jump', 
                        'broad_jump', 'bench_press', 'shuttle', 'cone']
        
        for stat in combine_stats:
            if stat in df_clean.columns:
                # Calculate position averages
                pos_averages = df_clean.groupby('position')[stat].mean()
                
                # Fill missing values with position averages
                for pos in pos_averages.index:
                    mask = (df_clean['position'] == pos) & (df_clean[stat].isna())
                    df_clean.loc[mask, stat] = pos_averages[pos]
        
        # Add a flag for players with complete vs. partial data
        df_clean['has_complete_data'] = df_clean[combine_stats].notna().all(axis=1)
        
        print(f"📊 Data completeness:")
        print(f"   - Players with complete data: {df_clean['has_complete_data'].sum()}")
        print(f"   - Players with partial data: {(~df_clean['has_complete_data']).sum()}")
        
        return df_clean
    
    def get_data_summary(self) -> Dict:
        """Get summary statistics of the loaded data"""
        if self.combined_data is None:
            return {}
        
        summary = {
            'total_players': len(self.combined_data),
            'years_covered': sorted(self.combined_data['draft_year'].unique()),
            'positions': sorted(self.combined_data['position'].unique()),
            'data_completeness': {}
        }
        
        # Check data completeness for each stat
        combine_stats = ['height', 'weight', 'forty_yard', 'vertical_jump', 
                        'broad_jump', 'bench_press', 'shuttle', 'cone']
        
        for stat in combine_stats:
            if stat in self.combined_data.columns:
                complete_count = self.combined_data[stat].notna().sum()
                summary['data_completeness'][stat] = {
                    'complete': complete_count,
                    'missing': len(self.combined_data) - complete_count,
                    'percentage': round(complete_count / len(self.combined_data) * 100, 1)
                }
        
        return summary
    
    def save_processed_data(self, output_file: str = "data/processed_combine_data.csv"):
        """Save the processed data to a CSV file"""
        if self.combined_data is not None:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            self.combined_data.to_csv(output_file, index=False)
            print(f"💾 Processed data saved to {output_file}")
            return True
        return False

def main():
    """Main function to process all CSV files"""
    processor = NFLDataProcessor()
    
    # Load and process all CSV files
    data = processor.load_csv_files()
    
    if data.empty:
        print("❌ No data loaded. Please check your CSV files.")
        return
    
    # Handle missing data
    processed_data = processor.handle_missing_data(data)
    
    # Get summary
    summary = processor.get_data_summary()
    
    print("\n📈 Data Summary:")
    print(f"Total Players: {summary['total_players']}")
    print(f"Years Covered: {summary['years_covered']}")
    print(f"Positions: {summary['positions']}")
    
    print("\n📊 Data Completeness:")
    for stat, info in summary['data_completeness'].items():
        print(f"  {stat}: {info['complete']}/{summary['total_players']} ({info['percentage']}%)")
    
    # Save processed data
    processor.save_processed_data()
    
    print("\n✅ Data processing complete!")

if __name__ == "__main__":
    main() 