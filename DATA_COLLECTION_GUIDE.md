# NFL Combine Data Collection Guide (25 Years)

## 🎯 Goal: Collect NFL Combine Data from 2000-2025

### **Data Sources for Each Year:**

## **📊 Primary Sources (Most Reliable)**

### **1. Pro Football Reference**
- **URL**: https://www.pro-football-reference.com/draft/
- **Years Available**: 2000-2024
- **Format**: Web tables, downloadable
- **Data Quality**: ⭐⭐⭐⭐⭐ (Best)
- **Cost**: Free

### **2. NFL.com Official Combine Results**
- **URL**: https://www.nfl.com/combine/results
- **Years Available**: 2003-2024
- **Format**: Web tables
- **Data Quality**: ⭐⭐⭐⭐⭐ (Official)
- **Cost**: Free

### **3. ESPN Draft Database**
- **URL**: https://www.espn.com/nfl/draft
- **Years Available**: 2000-2024
- **Format**: Web tables
- **Data Quality**: ⭐⭐⭐⭐
- **Cost**: Free

## **🔧 Secondary Sources**

### **4. WalterFootball.com**
- **URL**: https://walterfootball.com/combine.php
- **Years Available**: 2000-2024
- **Format**: Web tables
- **Data Quality**: ⭐⭐⭐⭐
- **Cost**: Free

### **5. NFLDraftScout.com**
- **URL**: https://www.nfldraftscout.com/
- **Years Available**: 2000-2024
- **Format**: Web tables
- **Cost**: Subscription required

### **6. DraftCountdown.com**
- **URL**: https://www.draftcountdown.com/
- **Years Available**: 2000-2024
- **Format**: Web tables
- **Cost**: Free

## **📋 Data Collection Strategy**

### **Phase 1: Quick Collection (1-2 hours)**
1. **Pro Football Reference** - Download 2000-2024 (25 years)
2. **Format**: CSV export available
3. **Columns needed**: Name, Position, College, Height, Weight, 40-yard, Vertical, Broad Jump, Bench Press, Shuttle, 3-Cone

### **Phase 2: Data Cleaning (30 minutes)**
1. **Standardize column names**
2. **Convert height formats** (6'2" → 74 inches)
3. **Handle missing data**
4. **Validate data quality**

### **Phase 3: Import into System (5 minutes)**
1. **Place CSV files in `data/combine_csvs/`**
2. **Run `python3 data_processor.py`**
3. **Verify data loaded correctly**

## **🚀 Step-by-Step Collection Process**

### **Step 1: Pro Football Reference (Recommended)**
```bash
# For each year 2000-2024:
1. Go to https://www.pro-football-reference.com/draft/YYYY-combine.htm
2. Click "Export" → "CSV"
3. Save as "YYYY_combine.csv"
4. Place in data/combine_csvs/
```

### **Step 2: Data Format Standardization**
Each CSV should have these columns:
```csv
name,position,college,draft_year,height,weight,forty_yard,vertical_jump,broad_jump,bench_press,shuttle,cone
```

### **Step 3: Quick Data Validation**
```python
# Check data quality
import pandas as pd
df = pd.read_csv("2024_combine.csv")
print(f"Players: {len(df)}")
print(f"Complete data: {df.dropna().shape[0]}")
```

## **📊 Expected Data Volume**

### **Per Year:**
- **Combine Invitees**: ~330 players
- **Complete Data**: ~250-280 players
- **Partial Data**: ~50-80 players

### **25 Years Total:**
- **Total Players**: ~8,250
- **Complete Data**: ~6,500
- **Partial Data**: ~1,750

## **🔍 Data Quality Checklist**

### **Required Fields:**
- ✅ **Name** (Player full name)
- ✅ **Position** (QB, RB, WR, TE, OT, OG, C, DE, DT, LB, CB, S)
- ✅ **College** (University name)
- ✅ **Draft Year** (Year of draft)

### **Combine Statistics (if available):**
- ✅ **Height** (inches or feet/inches)
- ✅ **Weight** (pounds)
- ✅ **40-Yard Dash** (seconds)
- ✅ **Vertical Jump** (inches)
- ✅ **Broad Jump** (inches)
- ✅ **Bench Press** (reps)
- ✅ **Shuttle** (seconds)
- ✅ **3-Cone Drill** (seconds)

## **⚡ Quick Start Commands**

### **1. Create Data Directory**
```bash
mkdir -p data/combine_csvs
```

### **2. Download Sample Year**
```bash
# Download 2024 data from Pro Football Reference
# Save as data/combine_csvs/2024_combine.csv
```

### **3. Test Data Processing**
```bash
python3 data_processor.py
```

### **4. Run Application**
```bash
./run_app.sh
```

## **🎯 Priority Order for Collection**

### **High Priority (Start Here):**
1. **2024** - Most recent, complete data
2. **2023** - Recent, good data
3. **2022** - Recent, good data
4. **2021** - Recent, good data
5. **2020** - Recent, good data

### **Medium Priority:**
6. **2019-2015** - Good historical data
7. **2014-2010** - Decent historical data

### **Lower Priority:**
8. **2009-2005** - Older data, may be incomplete
9. **2004-2000** - Oldest data, may have gaps

## **🔧 Data Conversion Tools**

### **For Different Formats:**
- **Height**: `6'2"` → `74` inches
- **Weight**: `215 lbs` → `215`
- **Times**: `4.45` → `4.45`
- **Jumps**: `32.5"` → `32.5`

### **Position Standardization:**
- **QB**: Quarterback
- **RB**: Running Back, Halfback, Tailback
- **WR**: Wide Receiver
- **TE**: Tight End
- **OT**: Offensive Tackle, T
- **OG**: Offensive Guard, G
- **C**: Center
- **DE**: Defensive End, EDGE
- **DT**: Defensive Tackle, Nose Tackle
- **LB**: Linebacker, ILB, OLB
- **CB**: Cornerback
- **S**: Safety, FS, SS

## **📈 Success Metrics**

### **Target Goals:**
- ✅ **25 years of data** (2000-2024)
- ✅ **8,000+ total players**
- ✅ **6,000+ with complete data**
- ✅ **All positions represented**
- ✅ **Data quality >90%**

### **Timeline:**
- **Day 1**: Collect 2020-2024 (5 years)
- **Day 2**: Collect 2015-2019 (5 years)
- **Day 3**: Collect 2010-2014 (5 years)
- **Day 4**: Collect 2005-2009 (5 years)
- **Day 5**: Collect 2000-2004 (5 years)

## **🚨 Common Issues & Solutions**

### **Missing Data:**
- **Problem**: Some players missing combine stats
- **Solution**: Our system handles missing data with imputation

### **Format Variations:**
- **Problem**: Different CSV formats
- **Solution**: Our data processor auto-detects and converts

### **Position Variations:**
- **Problem**: Different position naming
- **Solution**: Our system standardizes position names

### **Height/Weight Formats:**
- **Problem**: Different measurement formats
- **Solution**: Our converter handles all common formats

## **🎉 Next Steps**

1. **Start with Pro Football Reference** - Download 2024 data
2. **Test the conversion** - Run data processor
3. **Verify results** - Check data quality
4. **Scale up** - Collect remaining years
5. **Enjoy your 25-year dataset!**

This approach will give you a comprehensive NFL combine database spanning 25 years with thousands of players for comparison analysis! 