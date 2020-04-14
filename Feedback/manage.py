from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import app, db
# this file never changes.
# flask app starts the flask app from app.py 
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()


# python manage.py db init: run 1 time 
# python manage.py db migrate: run on every change made to schema
# python manage.py db upgrade: run on every change made to schema