from flask import Blueprint, request, jsonify
from sqlalchemy import text, bindparam
from app.database import engine

filters_bp = Blueprint("filters", __name__, url_prefix="/api")

def create_response(success=True, data=None, message="", status_code=200):
    payload = {"success": success, "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status_code

@filters_bp.get("/filter")
def filter_salles():
    batiments = request.args.getlist("batiment")
    etages    = request.args.getlist("etage", type=int)
    capacite  = request.args.get("capacite", type=int)
    only_with_conformite = request.args.get("only_with_conformite", "false").lower() == "true"

    limit   = request.args.get("limit", 20, type=int)
    offset  = request.args.get("offset", 0, type=int)
    order_by = (request.args.get("order_by") or "nom").strip()
    order    = (request.args.get("order") or "asc").strip().lower()

    allowed_cols = {"id","nom","batiment","etage","capacite","date_creation","etat"}
    if order_by not in allowed_cols: order_by = "nom"
    if order not in {"asc","desc"}: order = "asc"

    join_conformite = """
      LEFT JOIN conformite c
        ON c.salle_id = s.id
       AND (c.date_fin IS NULL OR NOW() BETWEEN c.date_debut AND c.date_fin)
    """

    sql =  f"""
      SELECT 
        s.id, s.nom, s.batiment, s.etage, s.capacite, s.etat, s.date_creation,
        c.id AS conformite_id,
        c.temperature_haute, c.temperature_basse,
        c.humidite_haute,   c.humidite_basse,
        c.pression_haute,   c.pression_basse,
        c.date_debut,       c.date_fin
      FROM salle s
      {join_conformite}
      WHERE 1=1
    """

    params = {}
    if batiments:
        sql += " AND s.batiment IN :batiments"
        params["batiments"] = tuple(batiments)
    if etages:
        sql += " AND s.etage IN :etages"
        params["etages"] = tuple(etages)
    if capacite is not None:
        sql += " AND s.capacite >= :capacite"
        params["capacite"] = capacite
    if only_with_conformite:
        sql += " AND c.id IS NOT NULL"

    sql += f" ORDER BY s.{order_by} {order} LIMIT :limit OFFSET :offset"
    params["limit"]  = limit
    params["offset"] = offset

    with engine.connect() as conn:
        stmt = text(sql)
        if "batiments" in params:
            stmt = stmt.bindparams(bindparam("batiments", expanding=True))
        if "etages" in params:
            stmt = stmt.bindparams(bindparam("etages", expanding=True))
        rows = conn.execute(stmt, params).fetchall()

    data = [dict(r._mapping) for r in rows]
    return create_response(True, data=data, message="Filtres appliqués")
