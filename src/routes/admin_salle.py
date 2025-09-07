from flask import Blueprint, request, jsonify
from app.database import execute_query, execute_write

admin_salle_bp = Blueprint("admin_salle", __name__, url_prefix="/api/admin/salles")

def create_response(success=True, data=None, message="", status_code=200):
    payload = {"success": success, "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status_code

# -----------------------
# GET /api/admin/salles?limit=&offset=
# -----------------------
@admin_salle_bp.get("/")
def list_salles():
    limit  = request.args.get("limit", 50, type=int)
    offset = request.args.get("offset", 0, type=int)

    rows = execute_query(
        "SELECT * FROM salle ORDER BY date_creation DESC LIMIT :limit OFFSET :offset",
        {"limit": limit, "offset": offset},
    )
    data = [dict(r._mapping) for r in rows]
    return create_response(True, data=data, message="Liste des salles")

# -----------------------
# GET /api/admin/salles/<id>
# -----------------------
@admin_salle_bp.get("/<int:salle_id>")
def get_salle(salle_id):
    rows = execute_query("SELECT * FROM salle WHERE id = :id", {"id": salle_id})
    if not rows:
        return create_response(False, message="Salle introuvable", status_code=404)
    return create_response(True, data=dict(rows[0]._mapping), message="Salle trouvée")

# -----------------------
# POST /api/admin/salles
# Body JSON: { nom, batiment, etage, capacite, etat?, niveau_confort? }
# -----------------------
@admin_salle_bp.post("/")
def create_salle():
    data = request.get_json(force=True, silent=True) or {}
    required = ["nom", "batiment", "etage", "capacite"]
    missing = [k for k in required if data.get(k) in (None, "")]
    if missing:
        return create_response(False, message=f"Champs requis manquants: {', '.join(missing)}", status_code=400)

    try:
        etage = int(data.get("etage"))
        capacite = int(data.get("capacite"))
    except ValueError:
        return create_response(False, message="etage et capacite doivent être des entiers", status_code=400)

    etat = data.get("etat", "active")

    # Construire dynamiquement selon les colonnes présentes
    cols = ["nom","batiment","etage","capacite","etat"]
    params = {
        "nom": data["nom"].strip(),
        "batiment": data["batiment"].strip(),
        "etage": etage,
        "capacite": capacite,
        "etat": etat
    }

    placeholders = ", ".join(f":{c}" for c in cols)
    colnames = ", ".join(cols)
    sql = f"INSERT INTO salle ({colnames}) VALUES ({placeholders})"

    new_id = execute_write(sql, params)
    # récupérer la salle créée
    row = execute_query("SELECT * FROM salle WHERE id = LAST_INSERT_ID()", {})[0]
    return create_response(True, data=dict(row._mapping), message="Salle créée", status_code=201)

# -----------------------
# PATCH /api/admin/salles/<id>
# Body JSON: champs partiels à modifier
# -----------------------
@admin_salle_bp.patch("/<int:salle_id>")
def update_salle(salle_id):
    data = request.get_json(force=True, silent=True) or {}
    if not data:
        return create_response(False, message="Aucune donnée à mettre à jour", status_code=400)

    # Colonnes autorisées
    allowed = {"nom","batiment","etage","capacite","etat"}
    updates = {}
    for k,v in data.items():
        if k in allowed:
            updates[k] = v

    if not updates:
        return create_response(False, message="Aucun champ autorisé fourni", status_code=400)

    # validations
    if "etage" in updates:
        try: updates["etage"] = int(updates["etage"])
        except ValueError: return create_response(False, message="etage doit être un entier", status_code=400)
    if "capacite" in updates:
        try: updates["capacite"] = int(updates["capacite"])
        except ValueError: return create_response(False, message="capacite doit être un entier", status_code=400)

    set_clause = ", ".join([f"{k} = :{k}" for k in updates.keys()])
    updates["id"] = salle_id

    execute_write(f"UPDATE salle SET {set_clause} WHERE id = :id", updates)

    rows = execute_query("SELECT * FROM salle WHERE id = :id", {"id": salle_id})
    if not rows:
        return create_response(False, message="Salle introuvable après mise à jour", status_code=404)
    return create_response(True, data=dict(rows[0]._mapping), message="Salle mise à jour")

# -----------------------
# DELETE /api/admin/salles/<id>?hard=true|false
# hard=false => soft delete (etat='inactive')
# hard=true  => suppression physique (⚠️ FK conformite)
# -----------------------
@admin_salle_bp.delete("/<int:salle_id>")
def delete_salle(salle_id):
    hard = request.args.get("hard", "false").lower() == "true"

    if hard:
        # ⚠️ échouera si FK conformite non CASCADE ou si données liées existent
        try:
            execute_write("DELETE FROM salle WHERE id = :id", {"id": salle_id})
            return create_response(True, message="Salle supprimée (hard)")
        except Exception as e:
            return create_response(False, message=f"Impossible de supprimer (FK ?): {e}", status_code=409)
    else:
        execute_write("UPDATE salle SET etat = 'inactive' WHERE id = :id", {"id": salle_id})
        rows = execute_query("SELECT * FROM salle WHERE id = :id", {"id": salle_id})
        if not rows:
            return create_response(False, message="Salle introuvable", status_code=404)
        return create_response(True, data=dict(rows[0]._mapping), message="Salle désactivée (soft delete)")
