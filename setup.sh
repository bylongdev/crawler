
#!/bin/bash

echo "🌸 Setting up your ninja email crawler environment..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip just in case
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

echo "✅ Environment ready!"
echo "👉 Activate it with: source venv/bin/activate"
echo "👉 Then run: pytest tests/ or python your_main_script.py"
