import csv
import io
import logging
import os
import smtplib
from datetime import date
from email.encoders import encode_base64
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate

logger = logging.getLogger(__name__)

def email_data(title, data):
    msg = MIMEMultipart()
    msg['From'] = os.environ["DASHBOARD_EMAIL_FROM"]
    msg['To'] = os.environ["DASHBOARD_EMAIL_TO"]
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = title
    msg.attach( MIMEText('') )

    buf = io.StringIO()
    writer = csv.writer(buf)
    row = []
    for s in data:
        row.append(s["key"])
        if type(s["values"][0]) == tuple:
            row.extend([""] * (len(s["values"][0]) - 1))
    writer.writerow(row)
    rows = max((len(s["values"]) for s in data))
    for i in range(rows):
        row = []
        for s in data:
            if len(s["values"]) > i:
                elem = s["values"][i]
                if type(elem) == tuple:
                    for e in elem:
                        row.append(e)
                else:
                    row.append(elem)
            else:
                row.append("")
        writer.writerow(row)

    part = MIMEBase("text", "csv")
    buf.seek(0)
    part.set_payload(buf.read())
    encode_base64(part)
    part.add_header("Content-Disposition",
                    'attachment; filename="%s.csv"' % title)
    msg.attach(part)

    logger.debug("Sending email: %s" % title)
    smtp = smtplib.SMTP_SSL(os.environ["DASHBOARD_EMAIL_SMTP_SERVER"])
    smtp.login(os.environ["DASHBOARD_EMAIL_FROM"],
               os.environ["DASHBOARD_EMAIL_PASSWORD"])
    smtp.sendmail(os.environ["DASHBOARD_EMAIL_FROM"],
                  os.environ["DASHBOARD_EMAIL_TO"],
                  msg.as_string())
    smtp.quit()

class Job:
    """Abstact Base Class for jobs. Child classes should implement:
    run() executes the task and returns an result object.

    Result Object Format
    ====================
    A result object should be a list of dicts. The dict must have keys
    "key" and "values". "key" is a name for the series of
    data. "values" is a list of elements. For tabular data, each row
    should be it's own dict, with each elements of values filling in
    columns. For plotted data, values should be a list of two element
    tuples.
    """

    name = None
    """The string name of the job. Job names must be uniqute."""

    schedule = None
    """A dict that tells the scheduler how often to run the job. Uses
    a cron-like format. Uses the following fields (all optional):
        year           4-digit year number
        month          month number (1-12)
        day            day of the month (1-31)
        week           ISO week number (1-53)
        day_of_week    number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
        hour           hour (0-23)
        minute         minute (0-59)
        second         second (0-59)
    """

    email = False
    """A boolean specifying if the results of the job should be emailed as a csv."""

    def __init__(self, store):
        self._store = store

    def _execute_and_store(self):
        logger.info("Executing job: %s" % self.name)
        val = self.run()
        if not self._store.set(self.name, val):
            raise Exception("Unable to store data")

        if self.email:
            email_data("%s - %s" % (self.name, date.today()), val)
