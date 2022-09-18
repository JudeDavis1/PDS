import csv
import bs4
import sys
import requests

from typing import List


def main():
    print('[*] Fetching data...')
    p = People()

    p.get_phone_numbers()
    print('[*] Saving results...')

    p.save()
    print('[*] Done!')


class Field:
    serial: int = 'SN.'
    name: str = 'Name'
    number: str = 'Phone Number'
    postcode: str = 'Postcode'
    is_completed: bool = 'Completed'

class People:

    def __init__(self, name='Smith', postcode='SL1'):
        self.name = name
        self.postcode = postcode
        self.link_classes = 'ml-3 d-inline light-blue my-auto no-wrap'
        self.url = f'https://www.thephonebook.bt.com/Person/PersonSearch/?Surname={self.name}&Location={self.postcode}'

        self.html = requests.get(self.url).text
        self.soup = bs4.BeautifulSoup(self.html, 'html.parser')
        self.fields = [Field.serial, Field.name, Field.number, Field.postcode, Field.is_completed]

        try:
            self.fileobj = open('phone_number_fields.csv', 'w+', newline='')
        except PermissionError:
            print('[-] Error! Could not open Excel file. Please try closing any programs that are using the file, then rerun the program...')
            sys.exit(-1)
        self.writer = csv.DictWriter(self.fileobj, self.fields)

    def get_phone_numbers(self, max=10) -> List[str]:
        self.numbers = []
        links = self.soup.find_all(class_=self.link_classes)

        for i in range(len(links)):
            self.numbers.append(links[i].text.strip('\n'))

        return self.numbers

    def save(self):
        self.writer.writeheader()

        for i in range(len(self.numbers)):
            self.writer.writerow({
                Field.serial: str(i),
                Field.name: self.name,
                Field.number: self.numbers[i],
                Field.postcode: self.postcode,
                Field.is_completed: 'No'
            })


if __name__ == '__main__':
    main()
