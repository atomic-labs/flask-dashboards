import logging
from apscheduler.scheduler import Scheduler

logger = logging.getLogger(__name__)

class SimpleScheduler:
    def __init__(self):
        self._sched = Scheduler()
        self._sched.start()
        self._jobs = {}

    def schedule(self, job):
        if job.name() in self._jobs:
            logger.warn("Already have job with name: %s" % job.name())
            return False

        self._sched.add_cron_job(job._execute_and_store, **job.schedule())
        self._jobs[job.name()] = job
        return True

    def schedules(self):
        return {job.name(): job.schedule() for job in self._jobs.values()}

    def execute(self, name):
        return self._jobs[name]._execute_and_store()
