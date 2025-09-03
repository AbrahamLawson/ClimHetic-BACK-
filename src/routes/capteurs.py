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

@capteurs_bp.route('/conformite', methods=['GET'])
def get_conformite_salles():
    """GET /api/capteurs/conformite - Vérifier la conformité de toutes les salles"""
    try:
        # Récupérer le paramètre limit (nombre de mesures pour la moyenne)
        limit = request.args.get('limit', 10, type=int)
        
        # Vérifier la conformité de toutes les salles
        resultats = capteur_service.verifier_conformite_salles(limit)
        
        # Calculer des statistiques globales
        total_salles = len(resultats)
        salles_conformes = len([r for r in resultats if r['statut'] == 'CONFORME'])
        salles_non_conformes = len([r for r in resultats if r['statut'] == 'NON_CONFORME'])
        salles_sans_donnees = len([r for r in resultats if r['statut'] == 'AUCUNE_DONNEE'])
        salles_sans_seuils = len([r for r in resultats if r['statut'] == 'SEUILS_NON_DEFINIS'])
        
        # Statistiques de scoring
        salles_avec_score = [r for r in resultats if r.get('details_verification', {}).get('score_conformite')]
        scores_distribution = {1: 0, 2: 0, 3: 0, 4: 0}
        niveaux_distribution = {"EXCELLENT": 0, "BON": 0, "MOYEN": 0, "MAUVAIS": 0}
        score_moyen = 0
        
        if salles_avec_score:
            for resultat in salles_avec_score:
                score = resultat['details_verification']['score_conformite']
                niveau = resultat['details_verification']['niveau_conformite']
                scores_distribution[score] += 1
                niveaux_distribution[niveau] += 1
            
            score_moyen = sum([r['details_verification']['score_conformite'] for r in salles_avec_score]) / len(salles_avec_score)
        
        # Compter les alertes par type
        alertes_temperature = []
        alertes_humidite = []
        alertes_pression = []
        
        for resultat in resultats:
            if resultat['alertes']:
                for alerte in resultat['alertes']:
                    if 'Température' in alerte:
                        alertes_temperature.append({
                            'salle': resultat['salle']['nom'],
                            'message': alerte
                        })
                    elif 'Humidité' in alerte:
                        alertes_humidite.append({
                            'salle': resultat['salle']['nom'],
                            'message': alerte
                        })
                    elif 'Pression' in alerte:
                        alertes_pression.append({
                            'salle': resultat['salle']['nom'],
                            'message': alerte
                        })
        
        return create_response(
            data={
                'salles': resultats,
                'statistiques': {
                    'total': total_salles,
                    'conformes': salles_conformes,
                    'non_conformes': salles_non_conformes,
                    'sans_donnees': salles_sans_donnees,
                    'sans_seuils': salles_sans_seuils,
                    'pourcentage_conformite': round((salles_conformes / total_salles * 100) if total_salles > 0 else 0, 2)
                },
                'scoring': {
                    'score_moyen': round(score_moyen, 2),
                    'distribution_scores': scores_distribution,
                    'distribution_niveaux': niveaux_distribution,
                    'salles_evaluees': len(salles_avec_score)
                },
                'alertes_par_type': {
                    'temperature': alertes_temperature,
                    'humidite': alertes_humidite,
                    'pression': alertes_pression
                },
                'parametres': {
                    'limite_mesures': limit
                }
            },
            message=f'Vérification de conformité effectuée pour {total_salles} salle(s) - {salles_conformes} conforme(s), {salles_non_conformes} non conforme(s)'
        )
    except Exception as e:
        return handle_exception(e)

@capteurs_bp.route('/salles/<int:salle_id>/conformite', methods=['GET'])
def get_conformite_salle(salle_id):
    """GET /api/capteurs/salles/:id/conformite - Vérifier la conformité d'une salle spécifique"""
    try:
        # Récupérer le paramètre limit
        limit = request.args.get('limit', 10, type=int)
        
        # Calculer les moyennes pour cette salle
        moyennes = capteur_service.get_moyennes_dernieres_donnees_by_salle(salle_id, limit)
        
        if not moyennes:
            return create_response(
                success=False,
                message=f'Aucune donnée trouvée pour la salle {salle_id}',
                status_code=404
            )
        
        # Récupérer les seuils de conformité
        conformite = capteur_service.get_seuils_conformite_by_salle(salle_id)
        
        if not conformite:
            return create_response(
                data={
                    'salle_id': salle_id,
                    'moyennes': moyennes,
                    'conformite': None,
                    'statut': 'SEUILS_NON_DEFINIS',
                    'alertes': ['Seuils de conformité non définis pour cette salle']
                },
                message=f'Moyennes calculées mais aucun seuil de conformité défini pour la salle {salle_id}'
            )
        
        # Vérifier la conformité
        verification = capteur_service.verifier_seuils(moyennes, conformite)
        
        return create_response(
            data={
                'salle_id': salle_id,
                'moyennes': moyennes,
                'conformite': conformite,
                'statut': verification['statut'],
                'alertes': verification['alertes'],
                'details_verification': verification['details'],
                'parametres': {
                    'limite_mesures': limit
                }
            },
            message=f'Vérification de conformité pour la salle {salle_id}: {verification["statut"]}'
        )
    except Exception as e:
        return handle_exception(e)

 