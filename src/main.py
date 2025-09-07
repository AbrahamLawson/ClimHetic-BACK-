from flask import Flask, jsonify
from routes.capteurs import capteurs_bp
from routes.search import search_bp
from routes.admin_salle import admin_salle_bp

app = Flask(__name__)
app.register_blueprint(capteurs_bp)  # /api/capteurs/...
app.register_blueprint(search_bp)    # /api/search
app.register_blueprint(admin_salle_bp)

@app.get("/ping")
def ping():
    return jsonify({"ok": True})

if __name__ == "__main__":
    print("=== URL MAP ===")
    for r in app.url_map.iter_rules():
        print(r)
    print("===============")
    app.run(debug=True, use_reloader=False, port=5000)
