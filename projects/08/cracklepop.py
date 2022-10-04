def crackle_pop(num : int) -> None:
    """
    Prints numbers from 1 to num, inclusive, replacing a number with: \n
    "Crackle" if it is divisible by 3 \n
    "Pop" if it is divisible by 5 \n
    "CracklePop" if it is divisible by 3 and 5 \n
    """
    for n in range(1, num + 1):
        # Set default values
        cracklepop : str = ""
        num : str = str(n)

        if n % 3 == 0:
            cracklepop += "Crackle"
            num = ""
        if n % 5 == 0:
            cracklepop += "Pop"
            num = ""

        print(cracklepop + num)

# Run function for numbers 1 to 100
crackle_pop(100)