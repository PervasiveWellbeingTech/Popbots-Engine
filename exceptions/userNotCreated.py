class UserNotCreated(Exception):
    def __init__(self):
        self.intents = intents # intents must be of type list
        super(BadKeywordInputError,self).__init__(intents)

    def __str__(self):
        return "[ERROR] User should have responded with: "+ ",".join(str(x) for x in self.intents)
        #repr(self.message)
