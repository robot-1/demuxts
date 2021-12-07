

class descriptor():
    def __init__(self, stream):
        self.stream = stream
        self.tag = None
        self.length = None

class AssociationTagDescriptor(descriptor):
    def __init__(self):
        super(AssociationTagDescriptor, self).__init__(mpkt)
        self.association = None
        self.use = None
        self.selector_length = None
        self.transaction_id = None
        self.timeout = None
    
    def get_dsi_info(self):
        pass

    def __str__(self):
        return "Association Tag Desciptor Type"