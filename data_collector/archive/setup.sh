#!/bin/bash

# Setup script for BeyondEscapism Data Collector

echo "🚀 Setting up BeyondEscapism Data Collector..."
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

echo ""
echo "📥 Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo ""
echo "⚙️  Setting up environment..."
if [ ! -f ".env" ]; then
    if [ -f "../backend/.env" ]; then
        echo "📋 Copying .env from backend..."
        cp ../backend/.env .env
        echo "✅ .env file created"
    else
        echo "📋 Creating .env from template..."
        cp .env.example .env
        echo "⚠️  Please edit .env and add your SUPABASE_URL and SUPABASE_KEY"
    fi
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🧪 Testing setup..."
python quickstart.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Make sure Ollama is installed and running"
echo "  2. Run: ollama pull llama-3.1-8b"
echo "  3. Deploy database schema (if not done)"
echo "  4. Start collecting: python collect_thailand.py"
echo ""
