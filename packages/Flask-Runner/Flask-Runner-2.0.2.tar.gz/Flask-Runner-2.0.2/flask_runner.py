import sys
import os
import argparse
from flask.ext.script import Manager as BaseManager, Server as BaseServer, Shell
from flask.ext.script import Command, Option, Group, prompt, prompt_bool, prompt_pass, prompt_choices

class Server(BaseServer):
    def get_options(self):
        options = super(Server, self).get_options()
        options += (
            Option('--noeval',
                dest = 'use_evalex',
                action = 'store_false',
                default = True,
                help = 'disable exception evaluation in the debugger'),
            Option('--extra',
                metavar = 'FILE',
                type = str,
                dest = 'extra_files',
                action = 'append', 
                help = 'additional file for the reloader to watch for changes'),
            Option('--profile',
                action = 'store_true',
                default = False,
                help = 'run the profiler for each request'),
            Option('--profile-count',
                metavar = 'COUNT',
                type = int,
                dest = 'profile_restrictions',
                action = 'append',
                help = 'restrict profiler output to the top COUNT lines'),
            Option('--profile-percent',
                metavar = 'PERCENT',
                type = float,
                dest = 'profile_restrictions',
                action = 'append',
                help = 'restrict profiler output to the top PERCENT lines'),
            Option('--profile-regex',
                metavar = 'REGEX',
                type = str,
                dest = 'profile_restrictions',
                action = 'append',
                help = 'filter profiler output with REGEX'),
            Option('--profile-dir',
                metavar = 'DIR',
                default = None,
                help = 'write profiler results one file per request in folder DIR'),
            Option('--lint',
                action = 'store_true',
                default = False,
                help = 'run the lint validation middleware'),
        )
        return options

    def handle(self, app, host, port, use_debugger, use_reloader,
               threaded, processes, passthrough_errors, use_evalex,
               extra_files, profile, profile_restrictions, profile_dir, lint):
        # we don't need to run the server in request context
        # so just run it directly

        if profile:
            from werkzeug.contrib.profiler import ProfilerMiddleware
            app.wsgi_app = ProfilerMiddleware(app.wsgi_app,
                restrictions = profile_restrictions, profile_dir = profile_dir)

        if lint:
            from werkzeug.contrib.lint import LintMiddleware
            app.wsgi_app = LintMiddleware(app.wsgi_app)

        app.run(host = host,
                port = port,
                use_debugger = use_debugger,
                use_reloader = use_reloader,
                threaded = threaded,
                processes = processes,
                passthrough_errors = passthrough_errors,
                use_evalex = use_evalex,
                extra_files = extra_files,
                **self.server_options)

class Test(Command):
    description = 'Runs unit tests.'
    
    def get_options(self):
        return (Option('-c', '--with-coverage',
            dest = 'coverage',
            action = 'store_true',
            help = 'Include coverage report'),)
            
    def run(self, coverage):
        options = ""
        if coverage:
            options += ' --with-coverage --cover-package=app'
        os.system('nosetests' + options)
    
class Manager(BaseManager):
    def __init__(self, app=None, with_default_commands=None, usage=None):
        super(Manager, self).__init__(app, with_default_commands = False, usage = usage)
        if with_default_commands or (app and with_default_commands is None):
            self.add_default_commands()

    def make_shell_context(self):
        d = dict(app = app)
        try:
            from app import db
            d['db'] = db
        except:
            pass
        try:
            from app import models
            d['models'] = models
        except:
            pass
        return d
          
    def add_default_commands(self):
        self.add_command("runserver", Server())
        self.add_command("shell", Shell(make_context = self.make_shell_context))
        self.add_command("test", Test())

class Runner(object):
    def __init__(self, app):
        self.app = app

    def handle(self, prog, args = None):
        server = Server()
        arg_parser = server.create_parser(prog)

        args = arg_parser.parse_args(args)
        server.handle(self.app, **args.__dict__)

    def run(self):
        self.handle(sys.argv[0], sys.argv[1:])

