# -*- coding: utf-8 -*-
"""
    blohg.script
    ~~~~~~~~~~~~

    Module with the CLI script related stuff.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import os
import sys
import posixpath
from flask.ext.script import Command, Group, Manager, Server as _Server, Option
from flask_frozen import Freezer, MissingURLGeneratorWarning
from warnings import filterwarnings
from werkzeug.routing import Map

from blohg import create_app as _create_app
from blohg.vcs import backends, REVISION_DEFAULT, REVISION_WORKING_DIR

# filter MissingURLGeneratorWarning warnings.
filterwarnings('ignore', category=MissingURLGeneratorWarning)


def create_app(*args, **kwargs):
    kwargs['autoinit'] = False
    return _create_app(*args, **kwargs)


class Server(_Server):

    def get_options(self):
        options = _Server.get_options(self)
        options += (Option('-n', '--revision-default', action='store_const',
                           dest='revision_id', const=REVISION_DEFAULT,
                           default=REVISION_WORKING_DIR,
                           help='use files from the default branch, instead '
                           'of the working directory'),)
        return options

    def handle(self, app, *args, **kwargs):
        os.environ['RUNNING_FROM_CLI'] = '1'
        app.blohg.init_repo(kwargs.pop('revision_id'))

        # find extension files
        def _listfiles(directory, files):
            if not os.path.exists(directory):
                return
            for f in os.listdir(directory):
                fname = os.path.join(directory, f)
                if os.path.isdir(fname):
                    _listfiles(fname, files)
                else:
                    files.append(os.path.abspath(fname))

        extra_files = []
        _listfiles(os.path.join(app.config['REPO_PATH'],
                                app.config['EXTENSIONS_DIR']), extra_files)

        if 'extra_files' in self.server_options \
           and self.server_options['extra_files'] is not None:
            self.server_options['extra_files'] = \
                list(self.server_options['extra_files']) + extra_files
        else:
            self.server_options['extra_files'] = extra_files

        _Server.handle(self, app, *args, **kwargs)


class InitRepo(Command):
    """initialize a blohg repo, using the default template."""

    def get_options(self):
        rv = ()
        for backend in backends:
            rv += (Option('--%s' % backend.identifier, action='store_true',
                          dest=backend.identifier,
                          help='create a %s repository' % backend.name),)
        return (Group(*rv, exclusive=True),)

    def handle(self, app, **kwargs):
        repo = None
        for backend in backends:
            if kwargs.get(backend.identifier, False):
                repo = backend
                break
        if repo is None:
            repo = backends[0]
        try:
            repo.create_repo(app.config['REPO_PATH'])
        except RuntimeError, err:
            print >> sys.stderr, str(err)


class Freeze(Command):
    """ freeze the blog into a set of static files. """

    option_list = (Option('--serve', '-s', dest='serve', default=False,
                          action='store_true'),
                   Option('--noindex', dest='no_index', default=False,
                          action='store_true'))

    def remap_rules(self, map, map_html):
        """remaping the rules with files extensions"""
        mapping = {'views.source': 'txt',
                   'views.atom': 'atom'}
        if map_html:
            mapping['views.tag'] = 'html'
            mapping['views.content'] = 'html'
            mapping['views.post_list'] = 'html'
            mapping['views.posts'] = 'html'
            mapping['views.home'] = 'html'
        rules = []
        for rule in map.iter_rules():
            rule = rule.empty()
            if rule.is_leaf:
                # Add the leafs without modif.
                rules.append(rule)
                continue

            # special treatment for the robot.txt url
            if rule.rule == '/source/':
                rules.append(rule)
                continue

            try:
                extension = mapping[rule.endpoint]
            except KeyError:
                # the rest can go through
                rules.append(rule)
                continue
            # It becomes a leaf
            rule.is_leaf = True
            # and we add an extension
            url = rule.rule[:-1]
            if url == '':
                url = '/index'
            rule.rule = url + '.' + extension
            # and we add the modified rule
            rules.append(rule)
        return Map(rules)

    def handle(self, app, serve, no_index):
        app.jinja_loader  # ugly workaround
        app.blohg.init_repo(REVISION_DEFAULT)

        app.url_map = self.remap_rules(app.url_map, no_index)

        # That's a risky one, it woud be better to give a parameter to the
        # freezer
        app.root_path = app.config.get('REPO_PATH')

        freezer = Freezer(app)

        def static_generator(static_dir):
            for f in app.blohg.changectx.files:
                if f.startswith(static_dir):
                    yield dict(filename=f[len(static_dir):] \
                               .strip(posixpath.sep))

        @freezer.register_generator
        def static():
            """Walk the static dir and freeze everything"""
            return static_generator('static')

        @freezer.register_generator
        def attachments():
            """Walk the attachment dir and freeze everything"""
            return static_generator(app.config['ATTACHMENT_DIR'])

        freezer.freeze()
        if serve:
            freezer.serve()


def create_script():
    """Script object factory

    :param repo_path: the path to the mercurial repository.
    :return: the script object (Flask-Script' Manager instance).
    """

    script = Manager(create_app, with_default_commands=False)
    script.add_option('--repo-path', dest='repo_path',
                      default=os.getcwd(), required=False,
                      help='Repository path')
    script.add_option('-e', '--disable-embedded-extensions',
                      action='store_false', dest='embedded_extensions',
                      default=True, help='disable the loading of extensions '
                      'from the mercurial repository')
    server = Server(use_debugger=True, use_reloader=True)
    server.description = 'runs the blohg local server.'
    script.add_command('runserver', server)
    script.add_command('initrepo', InitRepo())
    script.add_command('freeze', Freeze())

    return script
