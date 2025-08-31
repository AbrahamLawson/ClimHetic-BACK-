"""
Service de gestion du tunnel SSH pour la connexion à la base de données
"""
import os
import threading
import time
from sshtunnel import SSHTunnelForwarder
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Variable globale pour stocker le tunnel
_ssh_tunnel = None
_tunnel_lock = threading.Lock()

def get_ssh_config():
    """
    Récupère la configuration SSH depuis les variables d'environnement
    """
    return {
        'ssh_host': os.getenv('SSH_HOST'),
        'ssh_port': int(os.getenv('SSH_PORT', 22)),
        'ssh_username': os.getenv('SSH_USERNAME'),
        'ssh_password': os.getenv('SSH_PASSWORD'),
        'ssh_key_file': os.getenv('SSH_KEY_FILE'),
        'remote_db_host': os.getenv('REMOTE_DB_HOST', '127.0.0.1'),
        'remote_db_port': int(os.getenv('REMOTE_DB_PORT', 3306)),
        'local_bind_port': int(os.getenv('LOCAL_BIND_PORT', 3307))
    }

def create_ssh_tunnel():
    """
    Crée et démarre un tunnel SSH
    """
    global _ssh_tunnel
    
    if not should_use_ssh():
        return None
    
    config = get_ssh_config()
    
    try:
        # Déterminer le type d'authentification
        ssh_auth = {}
        if config['ssh_key_file'] and os.path.exists(config['ssh_key_file']):
            ssh_auth['ssh_pkey'] = config['ssh_key_file']
        elif config['ssh_password']:
            ssh_auth['ssh_password'] = config['ssh_password']
        else:
            raise ValueError("Aucune méthode d'authentification SSH configurée")
        
        # Créer le tunnel
        tunnel = SSHTunnelForwarder(
            (config['ssh_host'], config['ssh_port']),
            ssh_username=config['ssh_username'],
            **ssh_auth,
            remote_bind_address=(config['remote_db_host'], config['remote_db_port']),
            local_bind_address=('127.0.0.1', config['local_bind_port'])
        )
        
        tunnel.start()
        print(f"✅ Tunnel SSH créé : localhost:{config['local_bind_port']} -> {config['ssh_host']}:{config['remote_db_port']}")
        return tunnel
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du tunnel SSH : {e}")
        return None

def get_or_create_tunnel():
    """
    Récupère le tunnel existant ou en crée un nouveau
    """
    global _ssh_tunnel
    
    with _tunnel_lock:
        if not should_use_ssh():
            return None
            
        if _ssh_tunnel is None or not _ssh_tunnel.is_active:
            if _ssh_tunnel:
                try:
                    _ssh_tunnel.stop()
                except:
                    pass
            _ssh_tunnel = create_ssh_tunnel()
        
        return _ssh_tunnel

def should_use_ssh():
    """
    Vérifie si le tunnel SSH doit être utilisé
    """
    return os.getenv('USE_SSH_TUNNEL', 'false').lower() == 'true'

def get_tunnel_status():
    """
    Retourne le statut du tunnel SSH
    """
    global _ssh_tunnel
    
    if not should_use_ssh():
        return {
            'enabled': False,
            'active': False,
            'message': 'Tunnel SSH désactivé'
        }
    
    if _ssh_tunnel is None:
        return {
            'enabled': True,
            'active': False,
            'message': 'Tunnel SSH non initialisé'
        }
    
    return {
        'enabled': True,
        'active': _ssh_tunnel.is_active,
        'local_port': _ssh_tunnel.local_bind_port if _ssh_tunnel.is_active else None,
        'message': 'Tunnel SSH actif' if _ssh_tunnel.is_active else 'Tunnel SSH inactif'
    }

def stop_tunnel():
    """
    Arrête le tunnel SSH
    """
    global _ssh_tunnel
    
    with _tunnel_lock:
        if _ssh_tunnel and _ssh_tunnel.is_active:
            try:
                _ssh_tunnel.stop()
                print("🔌 Tunnel SSH fermé")
            except Exception as e:
                print(f"Erreur lors de la fermeture du tunnel SSH : {e}")
        _ssh_tunnel = None

def ensure_tunnel_connection():
    """
    S'assure que le tunnel SSH est actif si nécessaire
    """
    if should_use_ssh():
        tunnel = get_or_create_tunnel()
        if tunnel and tunnel.is_active:
            return True
        else:
            print("❌ Impossible d'établir le tunnel SSH")
            return False
    return True  # Pas de tunnel nécessaire

# Fonction pour nettoyer à la fermeture de l'application
import atexit
atexit.register(stop_tunnel)
