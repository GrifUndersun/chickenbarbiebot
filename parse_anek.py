import random

import bs4
import requests


def getanekdot():
    z = ''
    number = random.randrange(1, 1142)
    s = requests.get(f'https://baneks.ru/{number}')
    b = bs4.BeautifulSoup(s.text, "html.parser")
    p = b.select('article')
    for x in p:
        s = (x.getText().strip())
        z = z + s + '\n\n'
    return s


if __name__ == '__main__':
    print(getanekdot())
