#!/usr/bin/env python

from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import os.path as p

from subprocess import call, check_call
from pprint import pprint

from flask import current_app as app
from flask.ext.script import Server, Manager
from tabutils import fntools as ft

from app import create_app, db, models, utils


manager = Manager(create_app)
manager.add_option(
    '-m', '--cfgmode', dest='config_mode', default='Development')
manager.add_option('-f', '--cfgfile', dest='config_file', type=p.abspath)
manager.main = manager.run  # Needed to do `manage <command>` from the cli


@manager.option('-h', '--host', help='The server host', default=None)
@manager.option('-p', '--port', help='The server port', default=None)
@manager.option(
    '-t', '--threaded', help='Run multiple threads', action='store_true')
def runserver(**kwargs):
    # Overriding the built-in `runserver` behavior
    """Runs the flask development server"""

    with app.app_context():
        skwargs = {
            'host': kwargs.get('host') or app.config['HOST'],
            'port': kwargs.get('port') or app.config['PORT'],
            'threaded': kwargs.get('threaded'),
        }

        server = Server(**skwargs)
        args = [
            app, server.host, server.port, server.use_debugger,
            server.use_reloader, server.threaded, server.processes,
            server.passthrough_errors]

        server(*args)


@manager.option('-h', '--host', help='The server host', default=None)
@manager.option('-p', '--port', help='The server port', default=None)
@manager.option(
    '-t', '--threaded', help='Run multiple threads', action='store_true')
def serve(**kwargs):
    # Alias for `runserver`
    """Runs the flask development server"""
    runserver(**kwargs)


@manager.command
def checkstage():
    """Checks staged with git pre-commit hook"""

    path = p.join(p.dirname(__file__), 'app', 'tests', 'test.sh')
    cmd = "sh %s" % path
    return call(cmd, shell=True)


@manager.option('-F', '--file', help='Lint file', default='')
def lint(file):
    """Check style with flake8"""
    return call("flake8 %s" % file, shell=True)


@manager.option('-w', '--where', help='Requirement file', default=None)
@manager.option(
    '-x', '--stop', help='Stop after first error', action='store_true')
def test(where, stop=False):
    """Run nose tests"""
    nose = "python `which nosetests`"
    opts = 'xv' if stop else 'v'
    opts += 'w %s' % where if where else ''
    return call("%s -%s" % (nose, opts), shell=True)


@manager.command
def deploy():
    """Deploy staging app"""
    check_call('heroku keys:add ~/.ssh/id_rsa.pub', shell=True)
    check_call('git push origin features', shell=True)


@manager.option('-r', '--requirement', help='Requirement file', default=None)
def pipme(requirement):
    """Install requirements.txt"""
    prefix = '%s-' % requirement if requirement else ''
    call('pippy -r %srequirements.txt' % prefix, shell=True)


@manager.command
def require():
    """Create requirements.txt"""
    cmd = 'pip freeze -l | grep -vxFf dev-requirements.txt '
    cmd += '| grep -vxFf prod-requirements.txt '
    cmd += '> requirements.txt'
    call(cmd, shell=True)


@manager.command
def createdb():
    """Creates database if it doesn't already exist"""

    with app.app_context():
        db.create_all()
        print('Database created')


@manager.command
def cleardb():
    """Removes all content from database"""

    with app.app_context():
        db.drop_all()
        print('Database cleared')


@manager.command
def setup():
    """Removes all content from database and creates new tables"""

    with app.app_context():
        cleardb()
        createdb()


@manager.command
def populate():
    """Populates db with data"""
    limit = 0

    with app.app_context():
        table_name = 'Data'
        table = getattr(models, table_name)
        row_limit = app.config['ROW_LIMIT']
        chunk_size = min(row_limit or 'inf', app.config['CHUNK_SIZE'])
        debug, test = app.config['DEBUG'], app.config['TESTING']

        if test:
            createdb()

        data = utils.fetch_data(app.config)

        del_count = table.query.delete(synchronize_session=False)
        db.session.commit()

        if debug:
            print(
                'Deleted %s records from the %s table...' % (
                    del_count, table_name))

        for records in ft.chunk(data, chunk_size):
            in_count = len(records)
            pprint(records[0])
            limit += in_count

            if debug:
                print(
                    'Inserting %s records into the %s table...' % (
                        in_count, table_name))

            if test:
                pprint(records)

            db.engine.execute(table.__table__.insert(), records)

            if row_limit and limit >= row_limit:
                break

        if debug:
            print(
                'Successfully inserted %s records into the %s table!' % (
                    limit, table_name))


if __name__ == '__main__':
    manager.run()
