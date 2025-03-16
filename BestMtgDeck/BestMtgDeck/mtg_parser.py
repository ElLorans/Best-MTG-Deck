BASIC_LANDS = {"island": 25, "mountain": 25, "swamp": 25, "plains": 25, "forest": 25}


def clean_input(stringa: str) -> str:
    """
    Clean input from userform at url.
    """
    return (
        stringa.lower()
        .replace("  ", " ")
        .replace("\t", " ")
        .replace("\r", "")
        .replace("’", "'")
    )


def line_to_tuple(stringa: str) -> tuple:
    """
    Converts str to (str, int).
    :param stringa: Must have len(stringa) > 1. Accepts
                    1 fireflux squad
                    1  fireflux squad
                    1x fireflux squad
                    1 fireflux squad (mtga) 333
                    fireflux squad 1
    :return: (str, int)
    """
    stringa = stringa.strip().replace("  ", " ")
    if stringa[0].isdigit():  # if format: 1 tarmogoyf
        copies, name = stringa.split(" ", 1)
    elif stringa[0].isalpha():  # if format: tarmogoyf 1
        name, copies = stringa.rsplit(" ", 1)
    else:
        raise ValueError

    copies = int(copies.replace("x", ""))
    if name[:2] == "x ":
        name = name[2:]

    name = name.split(" (")[0]  # for MTGA export
    return name, copies


def parse_collection(string: str, add_basics=True) -> dict:
    """
    Transform multline str string to Dict[str, int]. Characters coming after ' (' are not parsed to allow MTGA
    input. Str must be lowercase.
    :param string: 1 tarmogoyf\n2 liliana of the VEIL
                   multiline str (not case sensitive), with int and str separated by space or x
                   Accepted formats:
                   int str
                   str int
                   int"x" str
    :param add_basics: bool. If truthy, result is updated with BASIC_LANDS.
    :return: Dict[str, int]
    """
    collection = dict()  # dict with user input
    lines = clean_input(string).splitlines()
    for line in lines:
        if len(line.strip()) > 2:  # ignore empty lines/wrong format
            try:
                name, copies = line_to_tuple(line)
                # merge cards already in coll_dict
                collection[name] = collection.get(name, 0) + copies
                if add_basics:
                    collection.update(BASIC_LANDS)
            except (IndexError, ValueError):  # identify error
                raise ValueError(f"This line is not in the right format:\n{line}")
    return collection


if __name__ == "__main__":
    accepted_inputs = """1 fireflux squad
1  fireflux squad
1x fireflux squad
1 fireflux squad (mtga) 333
fireflux squad 1""".splitlines()

    temp = tuple()
    for el in accepted_inputs:
        if len(temp) == 0:
            temp = line_to_tuple(el)
        elif temp != line_to_tuple(el):
            print("TEST NOT PASSED")
            print(el)
            print(line_to_tuple(el))
