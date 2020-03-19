
class NoPossibleAnswer(Exception):
    
    def __init__(self, bot_id,message_index):
        self.bot_id = bot_id
        self.message_index = message_index
        super(NoPossibleAnswer,self).__init__(bot_id,message_index)

    def __str__(self):
        return f"[ERROR] No possible answer for bot_id: {self.bot_id} at message index: {self.message_index}"
