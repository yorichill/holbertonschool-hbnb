from app import create_app
from app.services import facade  # <-- NOUVEAU : On importe la facade pour manipuler les données

# NOUVEAU : On lance l'application en lui précisant qu'on est en 'development'
app = create_app('development')

if __name__ == '__main__':
    # --- 👑 LA TRICHE : Création du Super-Admin au démarrage ---
    admin_data = {
        'first_name': 'Super',
        'last_name': 'Admin',
        'email': 'admin@hbnb.com',
        'password': 'adminpassword'
    }
    try:
        # On tente de créer l'utilisateur en mémoire
        admin_user = facade.create_user(admin_data)
        # On force son statut à Admin en accédant directement à l'attribut
        admin_user.is_admin = True
        print("✅ Super-Admin créé avec succès : admin@hbnb.com / adminpassword")
    except ValueError:
        # Si le serveur redémarre tout seul (auto-reload) et que l'admin y est déjà, on ignore l'erreur
        print("⚡ Le Super-Admin est déjà prêt en mémoire.")
    # -----------------------------------------------------------

    # NOUVEAU : Plus besoin d'écrire debug=True, la config s'en charge !
    app.run()