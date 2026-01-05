#!/usr/bin/env python3
"""
Infinite Story Web - Application Entry Point

This is the main entry point for running the Infinite Story Web application.
It initializes the Flask server with WebSocket support.
"""

import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.backend.server import app, socketio


def main():
    """Run the Infinite Story Web application.

    Initializes and starts the Flask server with WebSocket support.
    Server configuration is read from environment variables.

    Environment Variables:
        HOST: The host address to bind to. Defaults to '0.0.0.0'.
        PORT: The port number to listen on. Defaults to 5000.
        FLASK_DEBUG: Set to '1' to enable debug mode. Defaults to '0'.

    Returns:
        None
    """
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║           Infinite Story Web - Starting Server           ║
    ╠══════════════════════════════════════════════════════════╣
    ║  Host: {host:<50} ║
    ║  Port: {port:<50} ║
    ║  Debug: {str(debug):<49} ║
    ║                                                          ║
    ║  Open http://localhost:{port} in your browser             ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    socketio.run(app, host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
