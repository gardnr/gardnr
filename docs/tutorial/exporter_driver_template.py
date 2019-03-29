from gardnr import constants, drivers, logger


class Exporter(drivers.Exporter):
    """
    Uncomment these to filter the types of metrics are logged.
    Either whitelist or blacklist must be used, not both.
    """
    # whitelist = [constants.Metrics.IMAGE]
    # blacklist = [constants.Metrics.IMAGE]

    def setup(self):
        """
        Add configuration here
        """

        # remove the next line and add code
        pass

    def export(self, logs):
        """
        Output the list of logs to an external destination.
        The log object has the following fields available.

        Log:
            id: str
            timestamp: datetime
            longitude: float
            latitude: float
            elevation: float
            value: blob
            metric:
                topic: str
                type: str
                manual: bool
        """
        for log in logs:
            # remove the next line and add code
            pass
