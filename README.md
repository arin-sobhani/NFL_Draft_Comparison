# 🏈 NFL Player Comparison Tool

A web application that allows users to search and compare NFL players from 2000-2025 based on their combine statistics. Find similar players using advanced similarity algorithms and explore comprehensive player data.

## 🌟 Features

- **Player Search**: Search through 8,650+ NFL players from 2000-2025
- **Similarity Analysis**: Find 2 most similar players using weighted Euclidean distance
- **Position-Specific Comparisons**: Only compare players within the same position for meaningful results
- **Advanced Filtering**: Filter by position, draft year, and sort by any combine metric
- **Tiered Data Handling**: Intelligent handling of players with missing combine data
- **Dual Position Support**: Players like Travis Hunter (CB/WR) can be compared in both positions
- **Modern UI**: Clean, responsive web interface built with Streamlit

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd NflPlayerComp
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run simple_app.py
   ```

4. **Open your browser** to `http://localhost:8501`

### Deployment Options

#### Option 1: Streamlit Cloud (Recommended)

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository and set the path to `simple_app.py`
   - Click "Deploy"

#### Option 2: Heroku

1. **Create a Procfile**
   ```
   web: streamlit run simple_app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Deploy to Heroku**
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

#### Option 3: Railway

1. **Connect your GitHub repository to Railway**
2. **Set the start command**: `streamlit run simple_app.py --server.port=$PORT --server.address=0.0.0.0`
3. **Deploy automatically**

## 📊 Data Sources

The application uses processed NFL combine data from 2000-2025, including:
- Height, Weight
- 40-yard dash time
- Vertical jump
- Broad jump
- Bench press
- 3-cone drill
- Shuttle run

## 🧠 Technical Details

### Similarity Algorithm
- **Weighted Euclidean Distance**: Different weights for different positions
- **Position-Specific Weighting**: Speed matters more for CBs, strength for linemen
- **Tiered Comparisons**: Match players with similar data completeness

### Data Processing
- **Intelligent Imputation**: Uses position-based averages and ML predictions
- **Dual Position Expansion**: Players with multiple positions get separate entries
- **Data Validation**: Ensures data quality and consistency

### Performance
- **Caching**: Efficient data loading with Streamlit caching
- **Optimized Queries**: Fast player searches and comparisons
- **Responsive Design**: Works on desktop and mobile devices

## 🛠️ Project Structure

```
NflPlayerComp/
├── simple_app.py              # Main Streamlit application
├── nfl_player_data.py         # Data loading and management
├── player_similarity.py       # Similarity analysis algorithms
├── data_processor.py          # Data processing and cleaning
├── enhanced_data_imputation.py # ML-based data imputation
├── requirements.txt           # Python dependencies
├── .streamlit/config.toml     # Streamlit configuration
├── data/                      # Data files
│   └── processed_combine_data.csv
└── README.md                  # This file
```

## 🔧 Configuration

### Environment Variables
- `STREAMLIT_SERVER_PORT`: Port for the web server (default: 8501)
- `STREAMLIT_SERVER_ADDRESS`: Server address (default: localhost)

### Customization
- Modify position weights in `player_similarity.py`
- Add new data sources in `data_processor.py`
- Customize UI styling in `simple_app.py`

## 📈 Future Enhancements

- [ ] Pro Day data integration
- [ ] College statistics comparison
- [ ] Draft position analysis
- [ ] Player clustering and archetypes
- [ ] Advanced visualizations
- [ ] API endpoints for external access

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- NFL combine data sources
- Streamlit for the web framework
- Scikit-learn for machine learning algorithms
- The NFL community for inspiration

---

**Made with ❤️ for NFL fans and analysts** 