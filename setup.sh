#!/bin/bash

echo "🚀 Odin School EdTech Solutions Backend"
echo "======================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your settings before running the app"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌟 Available commands:"
echo "   fastapi dev main.py          # Start development server"
echo "   fastapi run main.py          # Start production server"
echo ""
echo "📖 API Documentation will be available at:"
echo "   http://localhost:8000/docs"
echo ""
echo "🎯 9 Problems ready for development:"
echo "   1. HotLead - Sales Lead Scoring"
echo "   2. CreatorFit - Influencer Marketing"
echo "   3. TrustDesk - Comment/Review Management"
echo "   4. AdLift - Marketing Optimization"
echo "   5. ReferMore - Referral System"
echo "   6. PriceSense - Pricing Optimization"
echo "   7. FirstTouch - Sales Automation"
echo "   8. OneTruth - Analytics Dashboard"
echo "   9. CloseMore - Sales Conversation Analysis"
