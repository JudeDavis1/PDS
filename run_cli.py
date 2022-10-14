import os

from phone_numbers import  People


def run():
    print('[*] Fetching data...')
    p = People(name='Walters', postcode='SL1')

    p.get_phone_numbers(max=20)
    print('[*] Saving results...')

    p.save()
    print('[*] Done!')


if __name__ == '__main__':
    run();os.system('pause')
