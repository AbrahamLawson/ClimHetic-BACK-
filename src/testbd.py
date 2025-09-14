from app.database import ping, get_session
from sqlalchemy import text

def main():
    # ping test  de la bd
    try:
        ping()
        print("✅ Connexion DB OK (SELECT 1)")
    except Exception as e:
        print("❌ Connexion DB KO:", repr(e))
        return

    # teste de requête 
    try:
        with get_session() as s:
            
            r = s.execute(text("SELECT COUNT(*) FROM salle"))
            print("Compteur salle:", r.scalar())
    except Exception as e:
        print("ℹ️ Requête salle échouée (->", repr(e))

if __name__ == "__main__":
    main()
