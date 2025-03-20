#!/bin/bash
# Install dependencies
pip install -r requirements.txt

# Make sure gunicorn is installed
pip install gunicorn

# Start the application
if [ -z "$PORT" ]; then
  PORT=10000
fi

# Try to start with wsgi.py first, fall back to app.py if that fails
if python -c "import wsgi" 2>/dev/null; then
  exec gunicorn --bind 0.0.0.0:$PORT wsgi:app
else
  exec gunicorn --bind 0.0.0.0:$PORT app:app
fi