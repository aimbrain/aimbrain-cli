class BaseCommand(object):
    """
    BaseCommand represents the bare minimum each command needs to implement.
    """
    command_id = 'base'

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.args = args
        self.kwargs = kwargs

    def run(self):
        raise NotImplementedError('Run not implemented')
