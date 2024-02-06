class MaximumRetriesError(Exception):

    def __init__(self, message="Maximum retries reached"):
        self.message = message
        super().__init__(self.message)


class MaxSizeFileError(Exception):
     
     def __init__(self, message):
        self.message = message
        super().__init__(self.message)

