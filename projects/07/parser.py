from typing import TextIO, List

class Parser:
    def __init__(self, file:str) -> None:
        # This should open the file for reading
        # Be able to check if there is another valid (non-empty and non-comment) line available
        # Return that line when advance() is called
        # And prepare for the next line
        self.file : TextIO
        with open(file, "r") as f:
            file = f
        self.line : List[str]


    def advance(self) -> bool:
        """
        advances to the next valid line if possible
        If successful, updates self.line with parsed line and returns True
        If unsuccesful, self.line is set to empty and returns False
        """
        print(self.file.readline())
