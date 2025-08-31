#!/usr/bin/env python3
"""
Test du service capteur pour vérifier la récupération des données
"""
import sys
import os

# Ajouter le répertoire src au PATH
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_database_connection():
    """Test de connexion à la base de données"""
    try:
        from app.database import ping
        ping()
        print("✅ Connexion à la base de données OK")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        return False

def test_salles_actives():
    """Test de récupération des salles actives"""
    try:
        from services.capteur_service import capteur_service
        
        print("\n🔍 Test: Récupération des salles actives")
        salles = capteur_service.get_salles_actives()
        
        if salles:
            print(f"✅ {len(salles)} salle(s) trouvée(s)")
            for salle in salles[:3]:  # Afficher les 3 premières
                print(f"   - ID: {salle['id']}, Nom: {salle['nom']}, Bâtiment: {salle['batiment']}, Étage: {salle['etage']}")
            return salles
        else:
            print("ℹ️ Aucune salle active trouvée")
            return []
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des salles: {e}")
        return []

def test_capteurs_by_salle(salle_id):
    """Test de récupération des capteurs d'une salle"""
    try:
        from services.capteur_service import capteur_service
        
        print(f"\n🔍 Test: Récupération des capteurs de la salle {salle_id}")
        capteurs = capteur_service.get_capteurs_by_salle(salle_id)
        
        if capteurs:
            print(f"✅ {len(capteurs)} capteur(s) trouvé(s)")
            for capteur in capteurs:
                print(f"   - ID: {capteur['id']}, Nom: {capteur['nom_capteur']}, Type: {capteur['type_capteur']}")
            return capteurs
        else:
            print(f"ℹ️ Aucun capteur trouvé pour la salle {salle_id}")
            return []
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des capteurs: {e}")
        return []

def test_moyennes_by_salle(salle_id):
    """Test de récupération des moyennes d'une salle"""
    try:
        from services.capteur_service import capteur_service
        
        print(f"\n🔍 Test: Récupération des moyennes de la salle {salle_id}")
        moyennes = capteur_service.get_moyennes_dernieres_donnees_by_salle(salle_id, 5)
        
        if moyennes:
            print("✅ Moyennes récupérées:")
            print(f"   - Température: {moyennes.get('moyenne_temperature')} {moyennes.get('unite_temperature', '')}")
            print(f"   - Humidité: {moyennes.get('moyenne_humidite')} {moyennes.get('unite_humidite', '')}")
            print(f"   - Pression: {moyennes.get('moyenne_pression')} {moyennes.get('unite_pression', '')}")
            return moyennes
        else:
            print(f"ℹ️ Aucune donnée de moyenne trouvée pour la salle {salle_id}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des moyennes: {e}")
        return None

def test_temperature_by_salle(salle_id):
    """Test de récupération des températures d'une salle"""
    try:
        from services.capteur_service import capteur_service
        
        print(f"\n🔍 Test: Récupération des températures de la salle {salle_id}")
        temperatures = capteur_service.get_temperature_by_salle(salle_id, 3)
        
        if temperatures:
            print(f"✅ {len(temperatures)} mesure(s) de température trouvée(s)")
            for temp in temperatures:
                print(f"   - Capteur: {temp['nom_capteur']}, Valeur: {temp['valeur']} {temp['unite']}, Date: {temp['date_update']}")
            return temperatures
        else:
            print(f"ℹ️ Aucune température trouvée pour la salle {salle_id}")
            return []
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des températures: {e}")
        return []

def test_donnees_by_capteur(capteur_id):
    """Test de récupération des données d'un capteur spécifique"""
    try:
        from services.capteur_service import capteur_service
        
        print(f"\n🔍 Test: Récupération des données du capteur {capteur_id}")
        donnees = capteur_service.get_dernieres_donnees_by_capteur(capteur_id, 2)
        
        if donnees:
            print("✅ Données du capteur récupérées:")
            capteur = donnees['capteur']
            print(f"   - Capteur: {capteur['nom_capteur']} (Type: {capteur['type_capteur']})")
            print(f"   - Salle: {capteur['salle_nom']}")
            
            donnees_list = donnees['donnees']
            if donnees_list:
                print(f"   - {len(donnees_list)} mesure(s):")
                for mesure in donnees_list:
                    print(f"     * {mesure['valeur']} {mesure['unite']} - {mesure['date_update']}")
            
            return donnees
        else:
            print(f"ℹ️ Aucune donnée trouvée pour le capteur {capteur_id}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des données du capteur: {e}")
        return None

def main():
    """Fonction principale de test"""
    print("=== Test du Service Capteur ===\n")
    
    # Test de connexion DB
    if not test_database_connection():
        print("💥 Impossible de continuer sans connexion DB")
        return
    
    # Test des salles actives
    salles = test_salles_actives()
    
    if not salles:
        print("💥 Aucune salle trouvée, impossible de continuer les tests")
        return
    
    # Prendre la première salle pour les tests
    salle_test = salles[0]
    salle_id = salle_test['id']
    
    print(f"\n🎯 Tests avec la salle: {salle_test['nom']} (ID: {salle_id})")
    
    # Test des capteurs de cette salle
    capteurs = test_capteurs_by_salle(salle_id)
    
    # Test des moyennes
    test_moyennes_by_salle(salle_id)
    
    # Test des températures
    test_temperature_by_salle(salle_id)
    
    # Test des données d'un capteur spécifique si on en a trouvé
    if capteurs:
        capteur_test = capteurs[0]
        test_donnees_by_capteur(capteur_test['id'])
    
    print("\n🎉 Tests terminés !")

if __name__ == "__main__":
    main()
