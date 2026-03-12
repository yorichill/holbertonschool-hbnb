from app import create_app

# NOUVEAU : On lance l'application en lui précisant qu'on est en 'development'
app = create_app('development')

if __name__ == '__main__':
    # NOUVEAU : Plus besoin d'écrire debug=True, la config s'en charge !
    app.run()