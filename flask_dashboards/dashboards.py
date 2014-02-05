import coffeescript
import importlib.machinery
import inspect
import json
import logging
import os
import os.path
import scss
import sys

from flask import Blueprint, Response, abort, render_template, \
    render_template_string

from . import job, store, scheduler

logger = logging.getLogger(__name__)

class Dashboards(object):
    def __init__(self, app, path=None, url_prefix="/dashboards",
                 store=store.SimpleStore()):
        logger.debug("Initializing flask-dashboards")
        self.app = app
        self.blueprint = None
        self.basepath = None
        self.dashboards = {}
        self._store = store

        if path is None:
            self.path = os.path.join(app.root_path, "dashboards")
        else:
            self.path = path

        self._start_scheduler(os.path.join(self.path, "jobs"))
        self._load_dashboards(os.path.join(self.path, "boards"))
        self._create_views()
        self.app.register_blueprint(self.blueprint, url_prefix=url_prefix)

    def _start_scheduler(self, job_path):
        self._scheduler = scheduler.SimpleScheduler()
        sys.path.append(job_path)
        for p in os.listdir(job_path):
            filename, ext = os.path.splitext(p)
            if ext != ".py":
                continue
            logger.info("Loading job module: %s" % filename)

            job_module_name = "dashboard_jobs.%s" % filename
            loader = importlib.machinery.SourceFileLoader(job_module_name,
                                                          os.path.join(job_path, p))
            mod = loader.load_module(job_module_name)

            for name, obj in inspect.getmembers(mod):
                if (inspect.isclass(obj) and issubclass(obj, job.Job)
                    and not obj == job.Job):
                    j = obj(self._store)
                    logger.info("Scheduling job: %s, with schedule: %s" %
                                (j.name(), j.schedule()))
                    self._scheduler.schedule(j)

    def _load_dashboards(self, board_path):
        logger.debug("Loading dashboards from: %s" % board_path)
        paths = os.listdir(board_path)
        for p in paths:
            fullpath = os.path.join(board_path, p)
            if os.path.isfile(fullpath) and p.endswith(".html"):
                logger.debug("Loading dashboard: %s" % p)
                with open(fullpath) as f:
                    self.dashboards[p[:-5]] = ("{% extends 'board.html' %}\n"
                                               + f.read())

    def _create_views(self):
        mod = Blueprint("dashboard", __name__,
                        template_folder="templates", static_folder="static")
        self.blueprint = mod

        @mod.route("/list")
        def list():
            return render_template("dashboard_list.html",
                                   dashboards=self.dashboards)

        @mod.route("/board/<name>")
        def dashboard(name):
            if name not in self.dashboards:
                abort(404)
            return render_template_string(self.dashboards[name], title=name)

        @mod.route("/jobs/")
        def jobs():
            return render_template("job_list.html",
                                   jobs=self._scheduler.schedules())

        @mod.route("/jobs/<name>/execute", methods=["POST"])
        def job_execute(name):
            if name not in self._scheduler.schedules():
                return Response("Job not found", status=404)
            self._scheduler.execute(name)
            return Response(status=200)

        @mod.route("/jobs/execute", methods=["POST"])
        def job_execute_all():
            for j in self._scheduler.schedules():
                self._scheduler.execute(j)
            return Response(status=200)

        @mod.route("/jobs/<name>/data")
        def job_data(name):
            logger.debug("Fetching data for: %s" % name)
            if name not in self._store:
                abort(404)

            return Response(json.dumps(self._store[name]),
                            mimetype='application/json')

        #
        # Utilities
        #
        @mod.route("/assets/application.js")
        def javascripts():
            scripts = [
                "javascripts/application.coffee",
            ]

            output = []
            for path in [os.path.join(mod.root_path, "static", s)
                         for s in scripts]:
                output.append("// JS: %s\n" % path)
                if ".coffee" in path:
                    logger.debug("Compiling Coffee for %s " % path)
                    contents = coffeescript.compile_file(path)
                else:
                    with open(path) as f:
                        contents = f.read()

                output.append(contents)

            return Response("".join(output), mimetype="application/javascript")

        @mod.route("/assets/application.css")
        def stylesheets():
            scripts = [
                "stylesheets/table.scss",
            ]

            output = []
            sass = scss.Scss()
            for path in [os.path.join(mod.root_path, "static", s)
                         for s in scripts]:
                output.append("/* CSS: %s*/\n" % path)
                if ".scss" in path:
                    logger.debug("Compiling Sass for %s " % path)
                    contents = sass.compile(scss_file=path)
                else:
                    with open(path) as f:
                        contents = f.read()

                output.append(contents)

            return Response("".join(output), mimetype="text/css")
