from app.database import engine
from sqlalchemy import text

def execute_query(query, params=None):
    """
    Exécuter une requête qui retourne plusieurs résultats
    
    Args:
        query (str): Requête SQL
        params (tuple): Paramètres de la requête
        
    Returns:
        list: Liste des résultats sous forme de dictionnaires
    """
    try:
        with engine.connect() as conn:
            # Convertir params en tuple si c'est une liste ou autre
            if params is not None:
                if not isinstance(params, (tuple, list)):
                    params = (params,)
                else:
                    params = tuple(params) if not isinstance(params, tuple) else params
            
            if params:
                # Convertir les paramètres tuple en dictionnaire pour SQLAlchemy 2.0
                if isinstance(params, (tuple, list)):
                    param_dict = {f'param_{i}': param for i, param in enumerate(params)}
                    # Remplacer les %s par des paramètres nommés
                    query_with_params = query
                    for i in range(len(params)):
                        query_with_params = query_with_params.replace('%s', f':param_{i}', 1)
                    result = conn.execute(text(query_with_params), param_dict)
                else:
                    result = conn.execute(text(query), params)
            else:
                result = conn.execute(text(query))
            
            columns = result.keys()
            rows = result.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"Erreur SQL: {query}")
        print(f"Paramètres: {params}")
        raise e

def execute_single_query(query, params=None):
    """
    Exécuter une requête qui retourne un seul résultat
    
    Args:
        query (str): Requête SQL
        params (tuple): Paramètres de la requête
        
    Returns:
        dict: Résultat sous forme de dictionnaire ou None si aucun résultat
    """
    try:
        with engine.connect() as conn:
            # Convertir params en tuple si c'est une liste ou autre
            if params is not None:
                if not isinstance(params, (tuple, list)):
                    params = (params,)
                else:
                    params = tuple(params) if not isinstance(params, tuple) else params
            
            if params:
                # Convertir les paramètres tuple en dictionnaire pour SQLAlchemy 2.0
                if isinstance(params, (tuple, list)):
                    param_dict = {f'param_{i}': param for i, param in enumerate(params)}
                    # Remplacer les %s par des paramètres nommés
                    query_with_params = query
                    for i in range(len(params)):
                        query_with_params = query_with_params.replace('%s', f':param_{i}', 1)
                    result = conn.execute(text(query_with_params), param_dict)
                else:
                    result = conn.execute(text(query), params)
            else:
                result = conn.execute(text(query))
                
            row = result.fetchone()
            if row:
                columns = result.keys()
                return dict(zip(columns, row))
            return None
    except Exception as e:
        print(f"Erreur SQL: {query}")
        print(f"Paramètres: {params}")
        raise e