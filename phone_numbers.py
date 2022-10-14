import os
import csv
import bs4
import sys
import requests

from typing import List


class People:

	def __init__(self, name='Smith', postcode='SL1', filename='phone_number_fields.csv'):
		self.name = name
		self.postcode = postcode

        # HTML classes that contain phone numbers
		self.link_classes = 'ml-3 d-inline light-blue my-auto no-wrap'
		self.url = f'https://www.thephonebook.bt.com/Person/PersonSearch/?Surname={self.name}&Location={self.postcode}'

		self.html = requests.get(self.url).text
		self.soup = bs4.BeautifulSoup(self.html, 'html.parser')

        # Typical row format (see phone_numbers.py)
		self.fields = [Field.serial, Field.name, Field.number, Field.postcode, Field.is_completed]

        # Starting serial no., may increase
		self.starting_sn = 0
		self.numbers_to_add = []
		self.explored_numbers = set()

        # Cannot directly update the writer, so save for the future
		self._updates: List[dict] = []

		try:
			if os.path.exists(filename):
				self.fileobj_r = open(filename, 'r', newline='')
				self.reader = csv.DictReader(self.fileobj_r)

				print('[*] Copying previous data...')

				for row in self.reader:
					self._updates.append({
						Field.serial: row[Field.serial],
						Field.name: row[Field.name],
						Field.number: row[Field.number],
						Field.postcode: row[Field.postcode],
						Field.is_completed: row[Field.is_completed]
					})

                    # Keep track of number that we have seen using a set.
					self.explored_numbers.add(row[Field.number])
                    # Increment the serial number to start from by 1.
					self.starting_sn = int(row[Field.serial]) + 1

				self.fileobj_r.close()

			self.fileobj_w = open(filename, 'w', newline='')
			self.writer = csv.DictWriter(self.fileobj_w, self.fields)
		except PermissionError:
			print('[-] Permission Error! Could not open Excel file. Please try closing any programs that are using the file, then rerun the program...')
			sys.exit(-1)

	def get_phone_numbers(self, max=10) -> List[str]:
		links = self.soup.find_all(class_=self.link_classes)

		for i in range(len(links)):
			n = links[i].text.strip('\n')

			self.numbers_to_add.append(n)

		return self.numbers_to_add

	def save(self):
		self.writer.writeheader()
		if len(self._updates) != 0:
            # 'Yes' at the bottom, 'No' at the top
			self._updates.sort(key=self._updates_sort_key)
			self.writer.writerows(self._updates)

		sn = self.starting_sn
		for i in range(len(self.numbers_to_add)):
            # Remove duplicate phone numbers
			if self.numbers_to_add[i] not in self.explored_numbers:
				self.writer.writerow({
					Field.serial: str(sn),
					Field.name: self.name,
					Field.number: self.numbers_to_add[i],
					Field.postcode: self.postcode,
					Field.is_completed: 'No'
				})
				sn += 1

		self.fileobj_w.close()

	def _updates_sort_key(self, x: dict):
        # If the row is marked as 'completed' then return 1
		if x[Field.is_completed].lower() in ['yes', 'completed', '1', 'true', 'positive', 'done']:
			return 1
		return 0


class Field:
    serial: int = 'SN.'
    name: str = 'Name'
    number: str = 'Phone Number'
    postcode: str = 'Postcode'
    is_completed: bool = 'Completed'


