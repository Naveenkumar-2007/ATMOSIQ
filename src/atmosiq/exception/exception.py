import sys


class AtmosIQException(Exception):
    def __init__(self, error_message, error_details: sys = sys):
        self.error_message = error_message
        _, _, exc_tb = error_details.exc_info()
        self.lineno = exc_tb.tb_lineno if exc_tb is not None else -1
        self.file_name = exc_tb.tb_frame.f_code.co_filename if exc_tb is not None else "<unknown>"
        super().__init__(str(error_message))

    def __str__(self):
        return f"Error occured in python script name [{self.file_name}] line number [{self.lineno}] error message [{str(self.error_message)}]"
