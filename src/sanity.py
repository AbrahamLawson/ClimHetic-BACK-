from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"ok": True})

if __name__ == "__main__":
    import os
    print("RUNNING:", os.path.abspath(__file__))
    print("=== URL MAP ===")
    for r in app.url_map.iter_rules():
        print(r)
    print("===============")

    app.run(debug=True, use_reloader=False, port=5050)
