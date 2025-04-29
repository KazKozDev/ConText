#!/bin/bash

# Helper script to run ConText macOS application

# Make sure Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama server..."
    ollama serve &
    sleep 2
else
    echo "Ollama server is already running."
fi

# Make sure backend is running
check_backend() {
    curl -s "http://localhost:5002/health" > /dev/null
    return $?
}

start_backend() {
    echo "Starting backend server..."
    cd backend
    source venv/bin/activate
    python -m backend.app &
    cd ..
    
    # Wait for backend to be ready
    echo "Waiting for backend to start..."
    for i in {1..20}; do
        if check_backend; then
            echo "Backend is now running."
            return 0
        fi
        sleep 1
    done
    echo "Warning: Backend did not start properly, but continuing anyway."
    return 1
}

# Check if backend is running, if not start it
if ! check_backend; then
    echo "Backend is not running."
    start_backend
else
    echo "Backend is already running."
fi

# Function to rebuild the application
rebuild_app() {
    echo "Rebuilding the application..."
    cd frontend
    npm run build
    cd ..
}

# Function to run in development mode
run_dev_mode() {
    echo "Starting ConText in development mode..."
    cd frontend

    # Kill any existing processes
    pkill -f "electron" || true
    pkill -f "node.*start" || true

    # Start in development mode
    npm start &
    cd ..
}

# Check command line arguments
if [ "$1" == "--rebuild" ]; then
    rebuild_app
elif [ "$1" == "--dev" ]; then
    run_dev_mode
    echo "ConText development mode started. Press Ctrl+C to stop."
    exit 0
fi

# If --dev was requested, don't continue to the app launch
if [ "$1" == "--dev" ]; then
    exit 0
fi

# Check if the application was built with the correct name
if [ -d "./frontend/dist/mac/ConText.app" ]; then
    echo "Launching ConText application..."
    open ./frontend/dist/mac/ConText.app
elif [ -d "./frontend/dist/mac-arm64/ConText.app" ]; then
    echo "Launching ConText application (ARM64)..."
    open ./frontend/dist/mac-arm64/ConText.app
# Check if the application was built but has the wrong name
elif [ -d "./frontend/dist/mac-arm64/Electron.app" ]; then
    echo "Found Electron.app - renaming to ConText.app..."
    # Make a copy with the correct name (safer than mv)
    cp -R ./frontend/dist/mac-arm64/Electron.app ./frontend/dist/mac-arm64/ConText.app
    echo "Launching ConText application (ARM64)..."
    open ./frontend/dist/mac-arm64/ConText.app
elif [ -d "./frontend/dist/mac/Electron.app" ]; then
    echo "Found Electron.app - renaming to ConText.app..."
    # Make a copy with the correct name (safer than mv)
    cp -R ./frontend/dist/mac/Electron.app ./frontend/dist/mac/ConText.app
    echo "Launching ConText application..."
    open ./frontend/dist/mac/ConText.app
else
    echo "ConText application not found. Building it now..."
    rebuild_app
    
    # Try to find and open the app again
    if [ -d "./frontend/dist/mac/ConText.app" ]; then
        echo "Launching ConText application..."
        open ./frontend/dist/mac/ConText.app
    elif [ -d "./frontend/dist/mac-arm64/ConText.app" ]; then
        echo "Launching ConText application (ARM64)..."
        open ./frontend/dist/mac-arm64/ConText.app
    elif [ -d "./frontend/dist/mac-arm64/Electron.app" ]; then
        echo "Found Electron.app - renaming to ConText.app..."
        # Make a copy with the correct name (safer than mv)
        cp -R ./frontend/dist/mac-arm64/Electron.app ./frontend/dist/mac-arm64/ConText.app
        echo "Launching ConText application (ARM64)..."
        open ./frontend/dist/mac-arm64/ConText.app
    elif [ -d "./frontend/dist/mac/Electron.app" ]; then
        echo "Found Electron.app - renaming to ConText.app..."
        # Make a copy with the correct name (safer than mv)
        cp -R ./frontend/dist/mac/Electron.app ./frontend/dist/mac/ConText.app
        echo "Launching ConText application..."
        open ./frontend/dist/mac/ConText.app
    else
        echo "Failed to find the built application. Try running in development mode instead:"
        echo "./run_context.sh --dev"
        exit 1
    fi
fi

echo "ConText has been launched successfully!" 