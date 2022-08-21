from typing import List, Generator

class Parser:
    """
    The Parser needs to be initialized with the .vm file that will be parsed.
    Once initialized, calling advance() will update the internal attributes
    to the tokens in the next line. These can be accessed directly.
    """
    def __init__(self, file:str) -> None:
        # This should open the file for reading
        # Be able to check if there is another valid (non-empty and non-comment) line available
        # Parse and store that line when advance() is called
        # And handle the end of the file
        self.file_reader : Generator = self.make_reader(file)
        self.op : str = ""
        self.arg1 : str = ""
        self.arg2 : str = ""
        self.parsed_line : List[str] = []
        # The unparsed line is only useful for debugging
        self.line : str = ""

    def make_reader(self, file:str) -> Generator:
        """
        Create generator which returns lines from file
        """
        with open(file, "r") as f:
            for line in f:
                yield line


    def advance(self) -> bool:
        """
        Advances to the next valid line if possible.
        If successful, updates self.line with parsed line and returns True.
        If unsuccesful, self.line is set to an empty string and returns False.
        """
        # This will iterate though the file_reader until a valid line is found
        # Or the end of the file is reached
        valid_line = False
        while not valid_line:
            # Try-except handles end of file case
            try:
                # Get next line
                line = next(self.file_reader)
                # Remove comments
                if "//" in line:
                    line = line[0:line.index("//")]
                # Remove whitespace and check length
                if len(line.strip()) != 0:
                    # If line is not empty, we have something to parse
                    valid_line = True
                    #print(f"Valid line found: {line}", end="")
                    self.line = line
                    self.parsed_line = self.parse_line(line)
                    return True

            except StopIteration:
                self.line = ""
                return False


    def parse_line(self, line:str) -> List[str]:
        """
        Parses a valid line and returns a list of tokens
        Updates self.parsed_line, self.op, self.arg1, and self.arg2 with current tokens
        """
        tokens = line.split()
        self.parsed_line = tokens
        self.op = tokens[0]
        if self.op in ["push", "pop"]:
            # push or pop have explicit arguments
            self.arg1 = tokens[1]
            self.arg2 = tokens[2]
        else:
            self.arg1 = ""
            self.arg2 = ""

        return tokens