from osiris.base.environments import Environment
from osiris.connector.salesforce import AnalyticsReportHttpConnector
from osiris.jobs.base import BaseJob


class AcquireAnalyticsReportDataJob(BaseJob):
    def __init__(self, name, env: Environment):
        super().__init__(name, env)
        self.sf = AnalyticsReportHttpConnector()

    def do_run(self, **kwargs):
        # TODO ADD Impl here
        self.sf.request_report(self.name)
