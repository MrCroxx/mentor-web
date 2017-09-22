#!env/bin/python

# -*- coding:utf-8 -*-

from app import app, db
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
manager.run()
