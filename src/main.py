from flask import Flask, jsonify
from flask_cors import CORS
from routes.admin import admin_bp
from routes.capteurs import capteurs_bp
from routes.search import search_bp
from routes.filters import filters_bp
from routes.admin_salle import admin_salle_bp

import os

def create_app():
    app = Flask(__name__)
    
    # Configuration CORS pour le développement
    CORS(app, origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Create React App
        "http://localhost:8080",  # Vue CLI
        "http://127.0.0.1:3000",  # Alternative localhost
        "http://127.0.0.1:5173",  # Alternative localhost
        "https://09.hetic.arcplex.dev"  # Frontend en production (HTTPS)
    ])
    
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(capteurs_bp, url_prefix='/api/capteurs')
    app.register_blueprint(search_bp),
    app.register_blueprint(filters_bp),
    app.register_blueprint(admin_salle_bp)
    
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'success',
            'message': 'ClimHetic Backend API is running',
            'version': '1.0.0'
        })
    
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Bienvenue sur ClimHetic API',
            'endpoints': {
                'health': '/api/health',
                'admin': '/api/admin/*',
                'capteurs': '/api/capteurs/*'
            }
        })
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Endpoint non trouvé',
            'error': 'Not Found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'message': 'Erreur interne du serveur',
            'error': 'Internal Server Error'
        }), 500
    
    return app

def main():
    if not os.getenv('DB_HOST'):
        print("Fichier .env non trouvé, utilisation des valeurs par défaut")
        os.environ.setdefault('DB_DIALECT', 'mysql')
        os.environ.setdefault('DB_USER', 'root')
        os.environ.setdefault('DB_PASSWORD', 'password')
        os.environ.setdefault('DB_HOST', 'localhost')
        os.environ.setdefault('DB_PORT', '3306')
        os.environ.setdefault('DB_NAME', 'climhetic')
        os.environ.setdefault('DB_SSL', '0')
    
    app = create_app()


    
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print("Démarrage du serveur ClimHetic Backend...")
    print(f"URL: http://{host}:{port}")
    print(f"Mode debug: {debug}")
    print("Endpoints disponibles:")
    print(f"  - Health check: http://{host}:{port}/api/health")
    print(f"  - Admin: http://{host}:{port}/api/admin/")
    print(f"  - Capteurs: http://{host}:{port}/api/capteurs/")
    
    print("=== URL MAP ===")
    for r in app.url_map.iter_rules():
        print(r)
    print("===============")


    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\nArrêt du serveur...")
    except Exception as e:
        print(f"Erreur lors du démarrage du serveur: {e}")

if __name__ == '__main__':
    main()
