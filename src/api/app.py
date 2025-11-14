from flask import Flask, jsonify
from flask_cors import CORS
import logging
import os
import sqlite3

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('claims.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create claims table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS claims (
            id TEXT PRIMARY KEY,
            status TEXT DEFAULT 'pending',
            amount REAL,
            description TEXT,
            user_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP NULL,
            error_message TEXT NULL
        )
    ''')
    
    # Create users table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    
    # Enable CORS
    CORS(app)
    
    # Initialize database
    init_db()
    
    # Import and register blueprints - FIXED IMPORTS
    try:
        # Import from current directory (src/)
        from auth_routes import auth_bp
        from analytics_routes import analytics_bp
        from batch_routes import batch_bp
        
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
        app.register_blueprint(batch_bp, url_prefix='/api/claims')
        logger.info("✅ All blueprints registered successfully")
        
    except ImportError as e:
        logger.error(f"❌ Failed to import blueprints: {e}")
        # Register basic routes as fallback
        @app.route('/api/auth/login', methods=['POST'])
        def fallback_login():
            return jsonify({"message": "Auth routes not loaded", "error": str(e)}), 500
        
        @app.route('/api/analytics/overview', methods=['GET'])
        def fallback_analytics():
            return jsonify({"message": "Analytics routes not loaded"})
        
        @app.route('/api/claims/batch/process', methods=['POST'])
        def fallback_batch():
            return jsonify({"message": "Batch routes not loaded"})
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            conn.close()
            return jsonify({'status': 'healthy', 'database': 'connected'})
        except Exception as e:
            return jsonify({'status': 'unhealthy', 'error': str(e)}), 500
    
    # Root endpoint
    @app.route('/')
    def root():
        return jsonify({
            'message': 'Insurance Claims API',
            'status': 'running',
            'endpoints': {
                'auth': '/api/auth',
                'analytics': '/api/analytics',
                'claims': '/api/claims',
                'health': '/health'
            }
        })
    
    return app

if __name__ == '__main__':
    app = create_app()
    logger.info("🚀 Starting server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)