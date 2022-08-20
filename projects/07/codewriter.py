from typing import Iterable

class CodeWriter:
    def __init__(self) -> None:
        self.label_index = 0
        # self.segment_list =


    def next_label(self) -> int:
        """
        returns and increments self.label_index
        """
        label = self.label_index
        self.label_index += 1
        return label

    def translate(self, operation:str, segment:str = "", index:str = "") -> str:
        """
        Parameters:
            operation
            segment
            index
        """
        # Check that each operation has the correct number of arguments
        if ((operation == "pop" or operation == "push")
             and (len(segment) == 0 or len(index) == 0)):
             raise ValueError("pop and push operations require both a segment argument and an index argument")

        # call the correct subroutine for a given operation



    # Common push and pop routines for