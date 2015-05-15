class ViewNotResolved(Exception):
    """ Raised from Application.resolve_view
    """
    def __init__(self, resource, tail):
        super().__init__(resource, tail)
        self.resource = resource
        self.tail = tail
