class Job:
    """Abstact Base Class for jobs. Child classes should implement:
    run() executes the task and returns an result object (see documentation in store)
    name() returns the string name of the job. Job names must be uniqute.
    schedule() returns an object with the following fields (all optional):
        year           4-digit year number
        month          month number (1-12)
        day            day of the month (1-31)
        week           ISO week number (1-53)
        day_of_week    number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
        hour           hour (0-23)
        minute         minute (0-59)
        second         second (0-59)
    """
    def __init__(self, store):
        self._store = store

    def _execute_and_store(self):
        val = self.run()
        if not self._store.set(self.name(), val):
            raise Exception("Unable to store data")
