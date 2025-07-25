# NFL Combine Data Folder

## 📁 Folder Structure
```
data/
├── combine_csvs/          # Put your CSV files here
│   ├── 2024_combine.csv
│   ├── 2023_combine.csv
│   ├── 2022_combine.csv
│   └── ... (25 years of data)
└── README.md             # This file
```

## 📊 Expected CSV Format

Your CSV files should have these columns (column names can vary, we'll map them):

### Required Columns:
- **Player Name** (e.g., "name", "player_name", "player")
- **Position** (e.g., "pos", "position")
- **College** (e.g., "school", "college", "university")
- **Draft Year** (e.g., "year", "draft_year", "season")

### Combine Statistics (if available):
- **Height** (inches or feet/inches format)
- **Weight** (pounds)
- **40-Yard Dash** (seconds)
- **Vertical Jump** (inches)
- **Broad Jump** (inches)
- **Bench Press** (reps)
- **Shuttle** (seconds)
- **3-Cone Drill** (seconds)

## 📋 Example CSV Structure

```csv
name,position,college,draft_year,height,weight,forty_yard,vertical_jump,broad_jump,bench_press,shuttle,cone
Caleb Williams,QB,USC,2024,73,214,4.6,32,115,15,4.2,7.1
Marvin Harrison Jr.,WR,Ohio State,2024,75,209,4.4,36,125,12,4.0,6.8
```

## 🔧 Data Processing

The application will:
1. **Auto-detect** column names and map them to standard format
2. **Handle missing data** using intelligent imputation
3. **Normalize formats** (height, weight, times)
4. **Validate data quality** and flag any issues

## 📝 Notes

- **Missing data is OK** - Players without combine numbers will be handled
- **Different formats welcome** - We'll standardize height/weight/time formats
- **Partial data accepted** - Players with only some combine stats can still be compared
- **File naming** - Use format: `YYYY_combine.csv` (e.g., `2024_combine.csv`)

## 🚀 Next Steps

1. Place your CSV files in the `combine_csvs/` folder
2. Run the data import script to process all files
3. The application will automatically use the combined dataset 