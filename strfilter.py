import re


def str_to_numlist(liststr: str):
    filtered_numbers = re.findall(r"[-]*\d+", liststr)
    return [int(num) for num in filtered_numbers]
