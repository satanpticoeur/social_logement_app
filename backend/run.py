from app import create_app, db
from flask.cli import with_appcontext
# from flask_migrate import MigrateCommand
import click

app = create_app()

@app.shell_context_processor
def make_shell_context():
    # Rend les objets db et models disponibles dans le shell Flask
    from app import models
    return {'db': db, 'models': models}

# Ajoute les commandes de migration (facultatif mais utile pour CLI)
# Si tu as besoin de commandes custom pour CLI, tu peux les définir ici.
# @app.cli.command('seed-db')
# @with_appcontext
# def seed_db():
#     """Seeds the database with initial data."""
#     # Your seeding logic here
#     click.echo('Database seeded!')

if __name__ == '__main__':
    app.run(
        debug=True
    )