#!/bin/bash
# AgentOps Safety Ecosystem - Environment Setup Script

set -e

echo "======================================================================"
echo "  AgentOps Safety Ecosystem - Environment Setup"
echo "======================================================================"
echo ""

# Check if .env already exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists!"
    read -p "   Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "   Skipping .env creation..."
        exit 0
    fi
fi

# Copy .env.example to .env
echo "📋 Creating .env file from .env.example..."
cp .env.example .env

echo ""
echo "🔑 Please enter your API keys:"
echo ""

# Prompt for OpenAI API Key
read -p "OpenAI API Key (get from https://platform.openai.com/api-keys): " OPENAI_KEY
if [ ! -z "$OPENAI_KEY" ]; then
    # Escape special characters for sed
    OPENAI_KEY_ESCAPED=$(printf '%s\n' "$OPENAI_KEY" | sed 's/[[\.*^$()+?{|]/\\&/g')
    sed -i.bak "s/OPENAI_API_KEY=.*/OPENAI_API_KEY=$OPENAI_KEY_ESCAPED/" .env
fi

# Prompt for Anthropic API Key
read -p "Anthropic API Key (get from https://console.anthropic.com/): " ANTHROPIC_KEY
if [ ! -z "$ANTHROPIC_KEY" ]; then
    ANTHROPIC_KEY_ESCAPED=$(printf '%s\n' "$ANTHROPIC_KEY" | sed 's/[[\.*^$()+?{|]/\\&/g')
    sed -i.bak "s/ANTHROPIC_API_KEY=.*/ANTHROPIC_API_KEY=$ANTHROPIC_KEY_ESCAPED/" .env
fi

# Generate secret key
echo ""
echo "🔐 Generating secret key for cryptographic signatures..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)
sed -i.bak "s/AGENTOPS_SECRET_KEY=.*/AGENTOPS_SECRET_KEY=$SECRET_KEY/" .env

# Clean up backup files
rm -f .env.bak

echo ""
echo "✅ Environment setup complete!"
echo ""
echo "📝 Your API keys have been saved to .env"
echo "   (This file is excluded from git via .gitignore)"
echo ""
echo "🚀 Next steps:"
echo "   1. Start services: docker compose up -d"
echo "   2. Run demo: python3 training/integrated_safety_demo.py"
echo "   3. View dashboard: http://localhost:5173"
echo ""
echo "📖 For more information, see:"
echo "   - Quick Start: training/QUICKSTART.md"
echo "   - Full Guide: SAFETY_ECOSYSTEM_README.md"
echo ""
