#!/bin/bash

echo "🏈 Starting NFL Player Comparison Tool..."
echo "=========================================="

# Check if streamlit is installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "❌ Streamlit not found. Installing..."
    pip3 install streamlit
fi

# Check if other dependencies are available
if ! python3 -c "import pandas, numpy" 2>/dev/null; then
    echo "❌ Missing dependencies. Installing..."
    pip3 install pandas numpy
fi

echo "✅ Dependencies ready!"
echo "🌐 Starting web server..."
echo "📱 Open your browser to: http://localhost:8501"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Run the main app
streamlit run simple_app.py 