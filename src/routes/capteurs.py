from flask import Blueprint, request, jsonify
from services.capteur_service import capteur_service

# Créer le blueprint pour les routes des capteurs
capteurs_bp = Blueprint('capteurs', __name__)

def create_response(success=True, data=None, message="", status_code=200):
    """Créer une réponse standardisée"""
    response = {
        'success': success,
        'message': message
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), status_code

def handle_exception(e, default_message="Erreur interne du serveur"):
    """Gérer les exceptions et retourner une réponse d'erreur"""
    print(f"Erreur: {str(e)}")
    return create_response(
        success=False,
        message=str(e) if str(e) else default_message,
        status_code=500
    )

@capteurs_bp.route('/salles', methods=['GET'])
def get_salles():
    """GET /api/capteurs/salles - Récupérer toutes les salles actives"""
    try:
        salles = capteur_service.get_salles_actives()
        return create_response(
            data=salles,
            message='Salles récupérées avec succès'
        )
    except Exception as e:
        return handle_exception(e)

@capteurs_bp.route('/salles/<int:salle_id>/capteurs', methods=['GET'])
def get_capteurs_by_salle(salle_id):
    """GET /api/capteurs/salles/:id/capteurs - Récupérer les capteurs d'une salle"""
    try:
        capteurs = capteur_service.get_capteurs_by_salle(salle_id)
        return create_response(
            data=capteurs,
            message=f'Capteurs de la salle {salle_id} récupérés avec succès'
        )
    except Exception as e:
        return handle_exception(e)

@capteurs_bp.route('/salles/<int:salle_id>/moyennes', methods=['GET'])
def get_moyennes_by_salle(salle_id):
    """GET /api/capteurs/salles/:id/moyennes - Récupérer les moyennes des dernières données d'une salle"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        moyennes = capteur_service.get_moyennes_dernieres_donnees_by_salle(salle_id, limit)
        
        if not moyennes:
            return create_response(
                success=False,
                message=f'Aucune donnée trouvée pour la salle {salle_id}',
                status_code=404
            )
        
        return create_response(
            data=moyennes,
            message=f'Moyennes de la salle {salle_id} récupérées avec succès'
        )
    except Exception as e:
        return handle_exception(e)

@capteurs_bp.route('/<int:capteur_id>/donnees', methods=['GET'])
def get_donnees_by_capteur(capteur_id):
    """GET /api/capteurs/:id/donnees - Récupérer les dernières données d'un capteur"""
    try:
        limit = request.args.get('limit', 1, type=int)
        
        donnees = capteur_service.get_dernieres_donnees_by_capteur(capteur_id, limit)
        
        if not donnees:
            return create_response(
                success=False,
                message=f'Capteur {capteur_id} non trouvé ou inactif',
                status_code=404
            )
        
        return create_response(
            data=donnees,
            message=f'Données du capteur {capteur_id} récupérées avec succès'
        )
    except Exception as e:
        return handle_exception(e)

@capteurs_bp.route('/salles/<int:salle_id>/temperature', methods=['GET'])
def get_temperature_by_salle(salle_id):
    """GET /api/capteurs/salles/:id/temperature - Récupérer les données de température d'une salle"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        temperatures = capteur_service.get_temperature_by_salle(salle_id, limit)
        return create_response(
            data=temperatures,
            message=f'Températures de la salle {salle_id} récupérées avec succès'
        )
    except Exception as e:
        return handle_exception(e)

@capteurs_bp.route('/salles/<int:salle_id>/humidite', methods=['GET'])
def get_humidite_by_salle(salle_id):
    """GET /api/capteurs/salles/:id/humidite - Récupérer les données d'humidité d'une salle"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        humidites = capteur_service.get_humidite_by_salle(salle_id, limit)
        return create_response(
            data=humidites,
            message=f'Humidités de la salle {salle_id} récupérées avec succès'
        )
    except Exception as e:
        return handle_exception(e)

@capteurs_bp.route('/salles/<int:salle_id>/pression', methods=['GET'])
def get_pression_by_salle(salle_id):
    """GET /api/capteurs/salles/:id/pression - Récupérer les données de pression d'une salle"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        pressions = capteur_service.get_pression_by_salle(salle_id, limit)
        return create_response(
            data=pressions,
            message=f'Pressions de la salle {salle_id} récupérées avec succès'
        )
    except Exception as e:
        return handle_exception(e)

@capteurs_bp.route('/<int:capteur_id>/temperature', methods=['GET'])
def get_temperature_by_capteur(capteur_id):
    """GET /api/capteurs/:id/temperature - Récupérer les données de température d'un capteur"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        temperatures = capteur_service.get_temperature_by_capteur(capteur_id, limit)
        return create_response(
            data=temperatures,
            message=f'Températures du capteur {capteur_id} récupérées avec succès'
        )
    except Exception as e:
        return handle_exception(e) 