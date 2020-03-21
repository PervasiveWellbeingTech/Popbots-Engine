class UserNotCreated(Exception):
    def __init__(self):
        self.features = features # features must be of type list
        super(BadKeywordInputError,self).__init__(features)

    def __str__(self):
        return "[ERROR] User should have responded with: "+ ",".join(str(x) for x in self.features)
        #repr(self.message)
