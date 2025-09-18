from flask import Blueprint, request, jsonify
from app.database import execute_query

def create_response(success=True, data=None, message="", status_code=200):
    payload = {"success": success, "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status_code

search_bp = Blueprint("search", __name__, url_prefix="/api")

@search_bp.get("/search")
def search():
    q        = (request.args.get("q") or "").strip()
    batiment = (request.args.get("batiment") or "").strip()
    salle    = (request.args.get("salle") or "").strip()
    etage    = (request.args.get("etage") or "").strip()
    capacite = (request.args.get("capacite") or "").strip()

    limit    = request.args.get("limit", 20, type=int)
    offset   = request.args.get("offset", 0, type=int)
    order_by = (request.args.get("order_by") or "nom").strip()
    order    = (request.args.get("order") or "asc").strip().lower()

    allowed_cols = {"nom","batiment","etage","capacite","date_creation","etat","id"}
    if order_by not in allowed_cols:
        order_by = "nom"
    if order not in {"asc","desc"}:
        order = "asc"

    sql = "SELECT * FROM salle WHERE 1=1"
    params = {}

    if q:
        sql += " AND nom LIKE :q"
        params["q"] = f"%{q}%"
    if batiment:
        sql += " AND batiment = :batiment"
        params["batiment"] = batiment
    if salle:
        sql += " AND nom = :salle"
        params["salle"] = salle
    if etage:
        try:
            params["etage"] = int(etage)
            sql += " AND etage = :etage"
        except ValueError:
            return create_response(False, message="etage doit être un entier", status_code=400)
    if capacite:
        try:
            params["capacite"] = int(capacite)
            sql += " AND capacite >= :capacite"
        except ValueError:
            return create_response(False, message="capacite doit être un entier", status_code=400)

    sql += f" ORDER BY {order_by} {order}"
    sql += " LIMIT :limit OFFSET :offset"
    params["limit"] = int(limit)
    params["offset"] = int(offset)

    try:
        rows = execute_query(sql, params)
        data = [dict(r._mapping) for r in rows]
        return create_response(True, data=data, message="Résultats trouvés")
    except Exception as e:
        return create_response(False, message=str(e), status_code=500)
