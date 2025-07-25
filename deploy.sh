#!/bin/bash

echo "🚀 NFL Player Comparison Tool - Deployment Script"
echo "=================================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git repository not found. Initializing..."
    git init
    git add .
    git commit -m "Initial commit"
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository found"
fi

# Check if remote origin exists
if ! git remote get-url origin > /dev/null 2>&1; then
    echo ""
    echo "📝 To deploy your app, you need to:"
    echo "1. Create a GitHub repository"
    echo "2. Add it as remote origin:"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git"
    echo "3. Push your code:"
    echo "   git push -u origin main"
    echo ""
    echo "🌐 Then deploy on Streamlit Cloud:"
    echo "1. Go to https://share.streamlit.io"
    echo "2. Sign in with GitHub"
    echo "3. Click 'New app'"
    echo "4. Select your repository"
    echo "5. Set main file path to: simple_app.py"
    echo "6. Click 'Deploy'"
    echo ""
    echo "🎉 Your app will be live at: https://your-app-name.streamlit.app"
else
    echo "✅ Remote origin configured"
    echo ""
    echo "📤 Pushing to GitHub..."
    git add .
    git commit -m "Update for deployment"
    git push origin main
    echo "✅ Code pushed to GitHub"
    echo ""
    echo "🌐 Next steps:"
    echo "1. Go to https://share.streamlit.io"
    echo "2. Sign in with GitHub"
    echo "3. Click 'New app'"
    echo "4. Select your repository"
    echo "5. Set main file path to: simple_app.py"
    echo "6. Click 'Deploy'"
fi

echo ""
echo "📚 For detailed instructions, see DEPLOYMENT.md"
echo "🔧 For configuration help, see README.md" 