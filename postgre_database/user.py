class USER:
    def __init__(self,user_id,subject_id):
        self.id = user_id
        self.name = None
        self.choice = False
        self.formal = False
        self.suject_id = subject_id
        #self.response_id = None
        #self.bot_id = None
        self.state = (None,None) # (bot_id,response_id)
        self.conv_id = None
        self.last = None
        self.switch = None
        self.problem = []