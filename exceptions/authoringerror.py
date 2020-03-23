class AuthoringError(Exception):

    def __init__(self, bot_id, message_index, authoring_error_type):
        """

        """

        self.bot_id = bot_id
        self.message_index = message_index
        self.authoring_error_type = authoring_error_type
        super(AuthoringError, self).__init__(
            bot_id, message_index, authoring_error_type)

    def __str__(self):
        return f'"{self.authoring_error_type}" authoring error for bot_id: "{self.bot_id}"" at message_index: "{self.message_index}" the bot will be deactivated until this issue has been resolved'



class NoMatchingSelectorPattern(Exception):
    def __init__(self,selector):
        self.selector = selector
        super(NoMatchingSelectorPattern, self).__init__(selector)

    def __str__(self):
        return f"The following selector: {self.selector} does not match any established pattern."


