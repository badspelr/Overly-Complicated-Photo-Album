#!/bin/bash
# Celery Development Startup Helper
# This script helps you start Celery worker and beat scheduler for development

cd photo_album

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Starting Celery for Photo Album Development"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if Redis is running
echo "Checking Redis connection..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is running (PONG received)"
else
    echo "❌ Redis is NOT running!"
    echo "   Start your Docker Redis container first."
    exit 1
fi

echo ""
echo "Select what to start:"
echo "  1) Celery Worker only (processes tasks)"
echo "  2) Celery Beat only (scheduler for 2 AM tasks)"
echo "  3) Both Worker + Beat (in background)"
echo "  4) Run test task"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "Starting Celery Worker..."
        echo "Press Ctrl+C to stop"
        echo ""
        celery -A photo_album worker --loglevel=info
        ;;
    2)
        echo ""
        echo "Starting Celery Beat..."
        echo "Press Ctrl+C to stop"
        echo ""
        celery -A photo_album beat --loglevel=info
        ;;
    3)
        echo ""
        echo "Starting both Worker and Beat in background..."
        
        # Start worker in background
        celery -A photo_album worker --loglevel=info --logfile=logs/celery-worker.log --detach
        
        # Start beat in background
        celery -A photo_album beat --loglevel=info --logfile=logs/celery-beat.log --detach
        
        echo "✅ Started!"
        echo ""
        echo "To monitor:"
        echo "  Worker logs: tail -f logs/celery-worker.log"
        echo "  Beat logs:   tail -f logs/celery-beat.log"
        echo ""
        echo "To stop:"
        echo "  pkill -f 'celery worker'"
        echo "  pkill -f 'celery beat'"
        ;;
    4)
        echo ""
        echo "Running test task..."
        python manage.py shell -c "
from photo_album.celery import app
from album.tasks import debug_task

print('Testing Celery connection...')
result = app.control.inspect().active()
if result:
    print('✅ Worker is active!')
    print('Sending test task...')
    task = debug_task.delay()
    print(f'✅ Task sent! ID: {task.id}')
    print('Check your worker logs to see if it processed.')
else:
    print('❌ No active workers found!')
    print('Start the worker first.')
"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
