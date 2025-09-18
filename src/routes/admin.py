from flask import Blueprint, request, jsonify
from services.admin_service import AdminService

admin_bp = Blueprint('admin', __name__)

admin_service = AdminService()

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

@admin_bp.route('/capteurs', methods=['GET'])
def get_all_capteurs_admin():
    """GET /api/admin/capteurs - Récupérer tous les capteurs avec leur statut"""
    try:
        capteurs = admin_service.get_all_capteurs()
        
        total = len(capteurs)
        actifs = len([c for c in capteurs if c.get('is_active', True)])
        inactifs = total - actifs
        
        return create_response(
            data={
                'capteurs': capteurs,
                'statistiques': {
                    'total': total,
                    'actifs': actifs,
                    'inactifs': inactifs
                }
            },
            message=f'{total} capteur(s) récupéré(s) ({actifs} actifs, {inactifs} inactifs)'
        )
    except Exception as e:
        return handle_exception(e)

@admin_bp.route('/capteurs', methods=['POST'])
def ajouter_capteur():
    """POST /api/admin/capteurs - Ajouter un nouveau capteur"""
    try:
        if not request.is_json:
            return create_response(
                success=False,
                message='Content-Type doit être application/json',
                status_code=400
            )
            
        data = request.get_json()
        
        if not data:
            return create_response(
                success=False,
                message='Données JSON requises',
                status_code=400
            )
        
        nom = data.get('nom')
        type_capteur = data.get('type_capteur')
        id_salle = data.get('id_salle')
        
        if not all([nom, type_capteur, id_salle]):
            return create_response(
                success=False,
                message='Champs requis: nom, type_capteur, id_salle',
                status_code=400
            )
        
        types_valides = ['temperature', 'humidite', 'pression']
        if type_capteur not in types_valides:
            return create_response(
                success=False,
                message=f'Type de capteur invalide. Types autorisés: {", ".join(types_valides)}',
                status_code=400
            )
        
        capteur_cree = admin_service.ajouter_capteur(nom, type_capteur, id_salle)
        
        return create_response(
            data=capteur_cree,
            message=f'Capteur {type_capteur} "{nom}" ajouté avec succès',
            status_code=201
        )
    except Exception as e:
        return handle_exception(e)

@admin_bp.route('/capteurs/<int:capteur_id>/desactiver', methods=['PUT'])
def desactiver_capteur(capteur_id):
    """PUT /api/admin/capteurs/{id}/desactiver - Désactiver un capteur"""
    try:
        capteur_desactive = admin_service.desactiver_capteur(capteur_id)
        
        return create_response(
            data=capteur_desactive,
            message=f'Capteur {capteur_id} désactivé avec succès'
        )
    except Exception as e:
        return handle_exception(e)

@admin_bp.route('/capteurs/<int:capteur_id>/reactiver', methods=['PUT'])
def reactiver_capteur(capteur_id):
    """PUT /api/admin/capteurs/{id}/reactiver - Réactiver un capteur"""
    try:
        capteur_reactive = admin_service.reactiver_capteur(capteur_id)
        
        return create_response(
            data=capteur_reactive,
            message=f'Capteur {capteur_id} réactivé avec succès'
        )
    except Exception as e:
        return handle_exception(e)

@admin_bp.route('/capteurs/<int:capteur_id>', methods=['DELETE'])
def supprimer_capteur(capteur_id):
    """DELETE /api/admin/capteurs/{id} - Supprimer définitivement un capteur"""
    try:
        confirmer = request.args.get('confirmer', '').lower()
        if confirmer != 'true':
            return create_response(
                success=False,
                message='Suppression non confirmée. Ajoutez ?confirmer=true pour confirmer la suppression définitive',
                status_code=400
            )
        
        success = admin_service.supprimer_capteur(capteur_id)
        
        if success:
            return create_response(
                message=f'Capteur {capteur_id} supprimé définitivement avec toutes ses données'
            )
        else:
            return create_response(
                success=False,
                message=f'Échec de la suppression du capteur {capteur_id}',
                status_code=500
            )
    except Exception as e:
        return handle_exception(e)

@admin_bp.route('/capteurs/<int:capteur_id>/changer-salle', methods=['PUT'])
def changer_salle_capteur(capteur_id):
    """PUT /api/admin/capteurs/{id}/changer-salle - Changer la salle d'un capteur"""
    try:
        data = request.get_json()
        
        if not data or 'nouvelle_salle_id' not in data:
            return create_response(
                success=False,
                message='Champ requis: nouvelle_salle_id',
                status_code=400
            )
        
        nouvelle_salle_id = data['nouvelle_salle_id']
        
        if not isinstance(nouvelle_salle_id, int):
            return create_response(
                success=False,
                message='nouvelle_salle_id doit être un entier',
                status_code=400
            )
        
        result = admin_service.changer_salle_capteur(capteur_id, nouvelle_salle_id)
        
        return create_response(
            data=result,
            message=result['message']
        )
    except Exception as e:
        return handle_exception(e)

@admin_bp.route('/capteurs/<int:capteur_id>/dissocier', methods=['PUT'])
def dissocier_capteur(capteur_id):
    """PUT /api/admin/capteurs/{id}/dissocier - Dissocier un capteur de sa salle"""
    try:
        result = admin_service.dissocier_capteur_salle(capteur_id)
        
        return create_response(
            data=result,
            message=result['message']
        )
    except Exception as e:
        return handle_exception(e)