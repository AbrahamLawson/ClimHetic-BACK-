from flask import Blueprint, request, jsonify
from services.admin_service import admin_service

# Créer le blueprint pour les routes d'administration
admin_bp = Blueprint('admin', __name__)

def create_response(success=True, data=None, message="", status_code=200):
    """Créer une réponse JSON standardisée"""
    return jsonify({
        'success': success,
        'data': data,
        'message': message
    }), status_code

def handle_exception(e, default_message="Erreur interne du serveur"):
    """Gérer les exceptions et retourner une réponse d'erreur"""
    return create_response(
        success=False,
        message=str(e) if str(e) else default_message,
        status_code=500
    )

# ============================================
# ROUTES DE CONSULTATION
# ============================================

@admin_bp.route('/capteurs', methods=['GET'])
def get_all_capteurs():
    """GET /api/admin/capteurs - Récupérer tous les capteurs avec leur statut"""
    try:
        capteurs = admin_service.get_all_capteurs()
        return create_response(
            data=capteurs,
            message=f'{len(capteurs)} capteurs récupérés avec succès'
        )
    except Exception as e:
        return handle_exception(e)

@admin_bp.route('/capteurs/disponibles', methods=['GET'])
def get_capteurs_disponibles():
    """GET /api/admin/capteurs/disponibles - Récupérer les capteurs disponibles (non affiliés)"""
    try:
        capteurs = admin_service.get_capteurs_disponibles()
        return create_response(
            data=capteurs,
            message=f'{len(capteurs)} capteurs disponibles'
        )
    except Exception as e:
        return handle_exception(e)

@admin_bp.route('/capteurs/indisponibles', methods=['GET'])
def get_capteurs_indisponibles():
    """GET /api/admin/capteurs/indisponibles - Récupérer les capteurs indisponibles (inactifs)"""
    try:
        capteurs = admin_service.get_capteurs_indisponibles()
        return create_response(
            data=capteurs,
            message=f'{len(capteurs)} capteurs indisponibles'
        )
    except Exception as e:
        return handle_exception(e)

@admin_bp.route('/salles/capteurs', methods=['GET'])
def get_capteurs_par_salle():
    """GET /api/admin/salles/capteurs - Récupérer les capteurs groupés par salle"""
    try:
        salles = admin_service.get_capteurs_par_salle()
        return create_response(
            data=salles,
            message=f'{len(salles)} salles récupérées avec leurs capteurs'
        )
    except Exception as e:
        return handle_exception(e)

@admin_bp.route('/statistiques', methods=['GET'])
def get_statistiques():
    """GET /api/admin/statistiques - Récupérer les statistiques générales"""
    try:
        stats = admin_service.get_statistiques()
        return create_response(
            data=stats,
            message='Statistiques récupérées avec succès'
        )
    except Exception as e:
        return handle_exception(e)

@admin_bp.route('/capteurs/<int:capteur_id>', methods=['GET'])
def get_capteur_details(capteur_id):
    """GET /api/admin/capteurs/<id> - Récupérer les détails d'un capteur"""
    try:
        capteur = admin_service.get_capteur_by_id(capteur_id)
        if not capteur:
            return create_response(
                success=False,
                message='Capteur introuvable',
                status_code=404
            )
        
        return create_response(
            data=capteur,
            message='Détails du capteur récupérés avec succès'
        )
    except Exception as e:
        return handle_exception(e)

# ============================================
# ROUTES DE MODIFICATION
# ============================================

@admin_bp.route('/capteurs/<int:capteur_id>/associer', methods=['POST'])
def associer_capteur(capteur_id):
    """POST /api/admin/capteurs/<id>/associer - Associer un capteur à une salle"""
    try:
        data = request.get_json()
        salle_id = data.get('salle_id')
        
        if not salle_id:
            return create_response(
                success=False,
                message='salle_id est requis dans le body',
                status_code=400
            )
        
        result = admin_service.associer_capteur_salle(capteur_id, salle_id)
        return create_response(
            data=result,
            message=result['message']
        )
        
    except Exception as e:
        return handle_exception(e)

@admin_bp.route('/capteurs/<int:capteur_id>/dissocier', methods=['POST'])
def dissocier_capteur(capteur_id):
    """POST /api/admin/capteurs/<id>/dissocier - Dissocier un capteur de sa salle"""
    try:
        result = admin_service.dissocier_capteur_salle(capteur_id)
        return create_response(
            data=result,
            message=result['message']
        )
        
    except Exception as e:
        return handle_exception(e)

@admin_bp.route('/capteurs/<int:capteur_id>/activer', methods=['POST'])
def activer_capteur(capteur_id):
    """POST /api/admin/capteurs/<id>/activer - Activer un capteur"""
    try:
        result = admin_service.activer_capteur(capteur_id)
        return create_response(
            data=result,
            message=result['message']
        )
        
    except Exception as e:
        return handle_exception(e)

@admin_bp.route('/capteurs/<int:capteur_id>/desactiver', methods=['POST'])
def desactiver_capteur(capteur_id):
    """POST /api/admin/capteurs/<id>/desactiver - Désactiver un capteur"""
    try:
        result = admin_service.desactiver_capteur(capteur_id)
        return create_response(
            data=result,
            message=result['message']
        )
        
    except Exception as e:
        return handle_exception(e)

# ============================================
# ROUTES BATCH (pour opérations multiples)
# ============================================

@admin_bp.route('/capteurs/batch/associer', methods=['POST'])
def associer_capteurs_batch():
    """POST /api/admin/capteurs/batch/associer - Associer plusieurs capteurs en une fois"""
    try:
        data = request.get_json()
        associations = data.get('associations', [])
        
        if not associations:
            return create_response(
                success=False,
                message='Liste d\'associations requise',
                status_code=400
            )
        
        resultats = []
        erreurs = []
        
        for assoc in associations:
            capteur_id = assoc.get('capteur_id')
            salle_id = assoc.get('salle_id')
            
            try:
                result = admin_service.associer_capteur_salle(capteur_id, salle_id)
                resultats.append({
                    'capteur_id': capteur_id,
                    'salle_id': salle_id,
                    'success': True,
                    'message': result['message']
                })
            except Exception as e:
                erreurs.append({
                    'capteur_id': capteur_id,
                    'salle_id': salle_id,
                    'success': False,
                    'message': str(e)
                })
        
        return create_response(
            data={
                'resultats': resultats,
                'erreurs': erreurs,
                'total_traites': len(associations),
                'total_reussis': len(resultats),
                'total_erreurs': len(erreurs)
            },
            message=f'Traitement terminé: {len(resultats)} réussies, {len(erreurs)} erreurs'
        )
        
    except Exception as e:
        return handle_exception(e)

@admin_bp.route('/capteurs/batch/dissocier', methods=['POST'])
def dissocier_capteurs_batch():
    """POST /api/admin/capteurs/batch/dissocier - Dissocier plusieurs capteurs en une fois"""
    try:
        data = request.get_json()
        capteur_ids = data.get('capteur_ids', [])
        
        if not capteur_ids:
            return create_response(
                success=False,
                message='Liste de capteur_ids requise',
                status_code=400
            )
        
        resultats = []
        erreurs = []
        
        for capteur_id in capteur_ids:
            try:
                result = admin_service.dissocier_capteur_salle(capteur_id)
                resultats.append({
                    'capteur_id': capteur_id,
                    'success': True,
                    'message': result['message']
                })
            except Exception as e:
                erreurs.append({
                    'capteur_id': capteur_id,
                    'success': False,
                    'message': str(e)
                })
        
        return create_response(
            data={
                'resultats': resultats,
                'erreurs': erreurs,
                'total_traites': len(capteur_ids),
                'total_reussis': len(resultats),
                'total_erreurs': len(erreurs)
            },
            message=f'Traitement terminé: {len(resultats)} réussies, {len(erreurs)} erreurs'
        )
        
    except Exception as e:
        return handle_exception(e)

# ============================================
# ROUTE DE RECHERCHE
# ============================================

@admin_bp.route('/capteurs/search', methods=['GET'])
def search_capteurs():
    """GET /api/admin/capteurs/search?q=terme - Rechercher des capteurs"""
    try:
        search_term = request.args.get('q', '').strip()
        
        if not search_term:
            return create_response(
                success=False,
                message='Terme de recherche requis (paramètre q)',
                status_code=400
            )
        
        # Pour l'instant, on récupère tous les capteurs et on filtre côté Python
        # Dans une vraie application, on ferait la recherche en SQL
        tous_capteurs = admin_service.get_all_capteurs()
        
        capteurs_filtres = []
        search_lower = search_term.lower()
        
        for capteur in tous_capteurs:
            if (search_lower in capteur['nom_capteur'].lower() or 
                search_lower in capteur['type_capteur'].lower() or 
                (capteur['salle_nom'] and search_lower in capteur['salle_nom'].lower())):
                capteurs_filtres.append(capteur)
        
        return create_response(
            data=capteurs_filtres,
            message=f'{len(capteurs_filtres)} capteurs trouvés pour "{search_term}"'
        )
        
    except Exception as e:
        return handle_exception(e)
