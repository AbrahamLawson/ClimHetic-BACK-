from flask import Blueprint, request, jsonify
from sqlalchemy import text, bindparam
from typing import List, Optional
from services.capteur_service import capteur_service   
from app.database import engine                        

filters_bp = Blueprint("filters", __name__, url_prefix="/api")


def create_response(success: bool = True, data=None, message: str = "", status_code: int = 200):
    payload = {"success": success, "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status_code


#  -> filtre par batiment, etage, capacite

@filters_bp.get("/filter")
def filter_salles():
    """
    GET /api/filter
    Query params:
      - batiment: répétable (?batiment=A&batiment=B)
      - etage:    répétable, int (?etage=1&etage=2)
      - capacite: int minimal (?capacite=30)
      - limit: int (défaut 20, max 500)
      - offset: int (défaut 0)
      - order_by: id|nom|batiment|etage|capacite|date_creation|etat
      - order: asc|desc
    """
    try:
        batiments = request.args.getlist("batiment")
        etages    = request.args.getlist("etage", type=int)
        capacite  = request.args.get("capacite", type=int)

        limit   = request.args.get("limit", 20, type=int)
        offset  = request.args.get("offset", 0, type=int)
        order_by = (request.args.get("order_by") or "nom").strip()
        order    = (request.args.get("order") or "asc").strip().lower()

        
        limit   = max(1, min(limit, 500))
        offset  = max(0, offset)

        allowed_cols = {"id","nom","batiment","etage","capacite","date_creation","etat"}
        if order_by not in allowed_cols:
            order_by = "nom"
        if order not in {"asc","desc"}:
            order = "asc"

        sql =  f"""
          SELECT 
            s.id, s.nom, s.batiment, s.etage, s.capacite, s.etat, s.date_creation
          FROM salle s
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
    except Exception as e:
        return create_response(False, message=str(e), status_code=500)


# /api/filters/confort
NIVEAUX_VALIDES = {"EXCELLENT", "BON", "MOYEN", "MAUVAIS"}

def _filtrer_par_niveau(niveaux: Optional[List[str]] = None,
                        tri: str = "score",
                        ordre: str = "asc",
                        limit_mesures: int = 10):
    # Normalisation
    niveaux = [n.upper() for n in (niveaux or []) if n and n.upper() in NIVEAUX_VALIDES] or None
    tri = (tri or "score").lower()
    ordre = (ordre or "asc").lower()
    reverse = (ordre == "desc")

    resultats = capteur_service.verifier_conformite_salles(limit=limit_mesures) or []

    if niveaux:
        resultats = [r for r in resultats if r.get("niveau_conformite") in niveaux]

    def key_score(r):
        return (r.get("score_conformite") is None, r.get("score_conformite", 99), r["salle"]["nom"])

    def key_pourcentage(r):
        return (r.get("pourcentage_conformite") is None, r.get("pourcentage_conformite", -1), r["salle"]["nom"])

    def key_nom(r):
        s = r.get("salle") or {}
        return (s.get("batiment") or "", s.get("etage") or 0, s.get("nom") or "")

    if tri == "pourcentage":
        resultats.sort(key=key_pourcentage, reverse=reverse)
    elif tri == "nom":
        resultats.sort(key=key_nom, reverse=reverse)
    else:
        resultats.sort(key=key_score, reverse=reverse)

    payload = []
    for r in resultats:
        s = r.get("salle") or {}
        payload.append({
            "salle_id": s.get("id"),
            "salle_nom": s.get("nom"),
            "batiment": s.get("batiment"),
            "etage": s.get("etage"),
            "niveau_confort": r.get("niveau_conformite"),
            "statut": r.get("statut"),
            "score": r.get("score_conformite"),
            "pourcentage_conformite": r.get("pourcentage_conformite"),
            "moyennes": r.get("moyennes"),
            "alertes": r.get("alertes", []),
        })
    return payload

@filters_bp.get("/filters/confort")
def get_salles_par_confort():
    """
    GET /api/filters/confort
    Query params:
      - niveau: répétable (EXCELLENT|BON|MOYEN|MAUVAIS)
      - tri: score|pourcentage|nom (défaut: score)
      - ordre: asc|desc (défaut: asc)
      - limit_mesures: int (défaut: 10, max 500)
    """
    try:
        niveaux = request.args.getlist("niveau") or None
        tri = (request.args.get("tri") or "score").lower()
        ordre = (request.args.get("ordre") or "asc").lower()
        limit_mesures_str = request.args.get("limit_mesures", "10")

        try:
            limit_mesures = max(1, min(int(limit_mesures_str), 500))
        except ValueError:
            return create_response(False, message="limit_mesures doit être un entier", status_code=400)

        data = _filtrer_par_niveau(
            niveaux=niveaux,
            tri=tri,
            ordre=ordre,
            limit_mesures=limit_mesures,
        )
        return create_response(True, data={"items": data, "count": len(data)}, message="Filtre confort appliqué")
    except Exception as e:
        return create_response(False, message=str(e), status_code=500)
