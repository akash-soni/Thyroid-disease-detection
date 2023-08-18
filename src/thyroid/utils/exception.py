import sys

def error_message_detail(error, error_detail:sys):

    _, _, exc_tb = error_detail.exc_info() # get the exception info

    file_name = exc_tb.tb_frame.f_code.co_filename # get the file name

    error_message = "Error occurred python script name [{0}] line number [{1}] error message [{2}]".format(
        file_name, exc_tb, str(error)
    )

    return error_message

class customException(Exception):
    def __init__(self, error_message, error_detail:sys):
        """
        inherited the Exception class 
        :param error_message: error message in string format
        """
        super().__init__(error_message)

        """
        using error_message_details() we show exception in formatted way
        """
        self.error_message = error_message_detail( error_message, error_detail=error_detail)

    def __str__(self):
        return self.error_message