from gardnr import constants, drivers, logger, metrics


class HelloWorldSensor(drivers.Sensor):

    def read(self):
        metrics.create_log('hello-world', '{first} {second}'.format(
            first=self.first,
            second=self.second
        ))

        logger.info('Writing {first} {second} to database'.format(
            first=self.first,
            second=self.second
        ))


class HelloWorldExporter(drivers.Exporter):

    whitelist = [constants.Metrics.TEMPERATURE]

    def export(self, logs):
        for log in logs:
            print(log.value)

        logger.info('Printing logs to console')
