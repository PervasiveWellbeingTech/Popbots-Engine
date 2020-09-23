#   Copyright 2020 Stanford University
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
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
        return f'{self.authoring_error_type}. This is an authoring error for bot named: "{self.bot_id}"" at message_index: "{self.message_index}" the bot should be should be deacivated until this issue has been resolved'



class NoMatchingSelectorPattern(Exception):
    def __init__(self,selector):
        self.selector = selector
        super(NoMatchingSelectorPattern, self).__init__(selector)

    def __str__(self):
        return f"The following selector: {self.selector} does not match any established pattern."


