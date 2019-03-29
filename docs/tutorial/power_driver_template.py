from gardnr import drivers, logger


class Power(drivers.Power):
    """
    Add code to interface with physical powered devices.
    """

    def setup(self):
        """
        Add configuration here
        """

        # remove the next line and add code
        pass

    def on(self):

        """
        Communicate with a powered device

        Example:

        import subprocess
        command = 'gpio mode 0 out; gpio write 0 1'
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        """

        # remove the next line and add code
        pass

    def off(self):
        pass
