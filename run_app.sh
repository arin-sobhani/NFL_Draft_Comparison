#!/bin/bash

# NFL Player Comparison Tool - Quick Start Script

echo "🏈 NFL Player Comparison Tool"
echo "=============================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi

echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
    echo ""
    echo "🚀 Starting the web application..."
    echo "📱 The app will open in your browser at: http://localhost:8501"
    echo "🛑 Press Ctrl+C to stop the application"
    echo ""
    
    # Run the Streamlit app
    streamlit run app.py
else
    echo "❌ Failed to install dependencies. Please check your Python environment."
    exit 1
fi 