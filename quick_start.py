#!/usr/bin/env python3
"""
Quick Start Script for NFL Player Comparison Tool
Converts 2025 data and sets up the system
"""

import pandas as pd
import re
import os

def convert_2025_data(data_text):
    """Convert the 2025 data text to our CSV format"""
    
    lines = data_text.strip().split('\n')
    players = []
    
    for line in lines:
        if line.strip():
            fields = line.split(',')
            if len(fields) >= 13:
                player = {
                    'name': fields[0].strip(),
                    'position': standardize_position(fields[1].strip()),
                    'college': fields[2].strip(),
                    'draft_year': 2025,
                    'height': convert_height(fields[4]),
                    'weight': convert_weight(fields[5]),
                    'forty_yard': convert_time(fields[6]),
                    'vertical_jump': convert_vertical(fields[7]),
                    'bench_press': convert_bench(fields[8]),
                    'broad_jump': convert_broad(fields[9]),
                    'cone': convert_time(fields[10]),
                    'shuttle': convert_time(fields[11])
                }
                players.append(player)
    
    return pd.DataFrame(players)

def standardize_position(pos):
    """Standardize position names"""
    pos_map = {
        'QB': 'QB', 'QUARTERBACK': 'QB',
        'RB': 'RB', 'RUNNING BACK': 'RB',
        'WR': 'WR', 'WIDE RECEIVER': 'WR',
        'TE': 'TE', 'TIGHT END': 'TE',
        'OT': 'OT', 'OFFENSIVE TACKLE': 'OT', 'T': 'OT',
        'OG': 'OG', 'OFFENSIVE GUARD': 'OG', 'G': 'OG',
        'C': 'C', 'CENTER': 'C',
        'DE': 'EDGE', 'DEFENSIVE END': 'EDGE', 'EDGE': 'EDGE',
        'DT': 'DT', 'DEFENSIVE TACKLE': 'DT',
        'LB': 'LB', 'LINEBACKER': 'LB',
        'CB': 'CB', 'CORNERBACK': 'CB',
        'S': 'S', 'SAFETY': 'S', 'SAF': 'S'
    }
    return pos_map.get(pos.upper(), pos)

def convert_height(height_str):
    """Convert height from '6-2' format to inches"""
    if not height_str or height_str.strip() == '':
        return None
    match = re.match(r'(\d+)-(\d+)', height_str.strip())
    if match:
        feet, inches = int(match.group(1)), int(match.group(2))
        return feet * 12 + inches
    return None

def convert_weight(weight_str):
    """Convert weight to integer"""
    if not weight_str or weight_str.strip() == '':
        return None
    try:
        return int(weight_str.strip())
    except:
        return None

def convert_time(time_str):
    """Convert time to float"""
    if not time_str or time_str.strip() == '':
        return None
    try:
        return float(time_str.strip())
    except:
        return None

def convert_vertical(vert_str):
    """Convert vertical jump to float"""
    if not vert_str or vert_str.strip() == '':
        return None
    try:
        return float(vert_str.strip())
    except:
        return None

def convert_bench(bench_str):
    """Convert bench press to integer"""
    if not bench_str or bench_str.strip() == '':
        return None
    try:
        return int(bench_str.strip())
    except:
        return None

def convert_broad(broad_str):
    """Convert broad jump to integer"""
    if not broad_str or broad_str.strip() == '':
        return None
    try:
        return int(broad_str.strip())
    except:
        return None

def main():
    print("🏈 NFL Player Comparison Tool - Quick Start")
    print("=" * 50)
    
    # Your 2025 data (paste the full data here)
    data_2025 = """BJ Adams,CB,Central Florida,College Stats,6-2,182,4.53,32.5,,117,,,,AdamBr00
Tommy Akingbesote,DT,Maryland,College Stats,6-4,306,5.09,28.0,,103,,,Dallas Cowboys / 7th / 247th pick / 2025,AkinTo00
Darius Alexander,DT,Toledo,College Stats,6-4,305,4.95,31.5,28,111,7.60,4.79,New York Giants / 3rd / 65th pick / 2025,AlexDa01
Zy Alexander,CB,LSU,College Stats,6-1,187,4.56,31.5,,116,,,,AlexZy00
LeQuint Allen,RB,Syracuse,College Stats,6-0,204,,35.0,,120,,,Jacksonville Jaguars / 7th / 236th pick / 2025,AlleLe01
Trey Amos,CB,Mississippi,College Stats,6-1,195,4.43,32.5,13,126,,,Washington Commanders / 2nd / 61st pick / 2025,AmosTr00
Andrew Armstrong,WR,Arkansas,College Stats,6-4,202,4.51,37.5,11,124,6.97,4.18,,-9999
Elijah Arroyo,TE,Miami,College Stats,6-5,250,,,22,,,,Seattle Seahawks / 2nd / 50th pick / 2025,ArroEl00
Eugene Asante,LB,Auburn,College Stats,6-1,223,4.48,,21,,,,,AsanEu01
Elic Ayomanor,WR,Stanford,College Stats,6-2,206,4.44,38.5,,127,,,Tennessee Titans / 4th / 136th pick / 2025,AyomEl00"""
    
    print("📊 Converting 2025 data...")
    
    # Convert the data
    df = convert_2025_data(data_2025)
    
    # Create data directory
    os.makedirs("data/combine_csvs", exist_ok=True)
    
    # Save the converted data
    output_file = "data/combine_csvs/2025_combine.csv"
    df.to_csv(output_file, index=False)
    
    print(f"✅ Converted {len(df)} players to {output_file}")
    
    # Show data summary
    print(f"\n📈 Data Summary:")
    print(f"Total Players: {len(df)}")
    print(f"Positions: {sorted(df['position'].unique())}")
    print(f"Colleges: {len(df['college'].unique())}")
    
    # Show data completeness
    stats = ['height', 'weight', 'forty_yard', 'vertical_jump', 'broad_jump', 'bench_press', 'shuttle', 'cone']
    complete_data = df[stats].notna().all(axis=1).sum()
    print(f"Complete Data: {complete_data}/{len(df)} ({complete_data/len(df)*100:.1f}%)")
    
    print(f"\n🎯 Next Steps:")
    print(f"1. Add more CSV files to data/combine_csvs/")
    print(f"2. Run: python3 data_processor.py")
    print(f"3. Run: ./run_app.sh")
    
    # Show sample data
    print(f"\n📋 Sample Data:")
    print(df.head(3).to_string(index=False))

if __name__ == "__main__":
    main() 