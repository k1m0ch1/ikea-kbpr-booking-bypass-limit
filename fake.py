import sys
import time
import string
import random

from datetime import datetime, timedelta

import requests

headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.9",
    "Content-Type": "application/json;charset=UTF-8",
    "Host": "ikea-booking.lenna.ai",
    "Referer": "https://ikea-booking.lenna.ai/",
    "DNT": "1",
    "Origin": "https://ikea-booking.lenna.ai"
}

body = {
    "name": ''.join(random.choice(string.ascii_uppercase) for _ in range(10)),
    "phone_number": f"+628{''.join(random.choice(string.digits) for _ in range(10))}",
    "email": f"{''.join(random.choice(string.ascii_uppercase) for _ in range(10))}@gmail.com",
    "slot_open":"2021-04-20 8:00:00+00",
    "slot_close":"2021-04-28 11:00:00+00",
    "date": "",
    "store_name":"IKEA Kota Baru Parahyangan",
    "store_id": 2,
    "slot_id": 0,
    "qty": random.randint(2, 5),
    "age": f"40{''.join(random.choice(string.digits) for _ in range(3))}",
    "address": ''.join(random.choice(string.ascii_uppercase) for _ in range(25))
}

def reloadBody(body):
    dataSet = open("name.txt", "r")
    dataName = [ name.split("\n")[0] for name in dataSet ]
    dataSet = open("word.txt", "r")
    dataWord = [ item.split("\n")[0] for item in dataSet ]
    dataSpecChar = ["", ".", "_", "-"]
    dataStreetFirst = ["Jalan ", "jl. ", "gg. ", "gang "]
    body['name'] = dataName[random.randint(0, len(dataName)-1)]
    body['email'] = f"{body['name']}{dataSpecChar[random.randint(0, len(dataSpecChar)-1)]}{dataWord[random.randint(0, len(dataWord)-1)]}@gmail.com"

    dataSet = open("street.txt", "r")
    dataStreet = [ item.split("\t")[0] for item in dataSet ]
    maxNamaJalan = random.randint(2, 4)
    namaJalan = []
    for i in range(0, maxNamaJalan):
        while True:
            tmp = dataStreet[random.randint(0, len(dataSpecChar)-1)]
            if len(namaJalan) > 0:
                if tmp not in namaJalan[len(namaJalan)-1]:
                    namaJalan.append(tmp)
                    break
            else:
                namaJalan.append(tmp)
    body['address'] = f"{dataStreetFirst[random.randint(0,1)]} {''.join(namaJalan)} No {''.join(random.choice(string.digits) for _ in range(3))}"
    body['qty'] = random.randint(2, 5)
    return body

if len(sys.argv) > 1:
    body['date'] = str(sys.argv[1])
else:
    body['date'] = input("tanggal (YYYY-MM-DD) : ")

def checkDate(date, headers) -> dict:
    checkdate = requests.get(f"https://ikea-booking.lenna.ai/backend/public/api/public/list/2/{date}", headers=headers)
    if checkdate.status_code!= 200:
        print(f"{checkdate.status_code} got some error when fetch the date")
        print(checkdate.text)
        sys.exit(1)
    return checkdate.json()

def booking(data, headers):
    print(f"I will book your data, please make sure your data below is right")
    print(f"\n{body}\n")
    if input("are your sure to continue? (Y/N) ").lower() == 'n' :
        print("Well bye")
        sys.exit(1)
    book = requests.post("https://ikea-booking.lenna.ai/backend/public/api/public/visitor", headers=headers, json=data)
    if book.status_code != 200:
        print(f"{book.status_code} Can't create the fake book")
        print(book.text)
        sys.exit(1)
    print(f"Booked Success with code {book.json()['data']['code']} you can access your QRCODE from here : https://ikea-booking.lenna.ai/confirm/{book.json()['data']['code']} ")
    print(f" or convert this code to QRCODE to get the QRCODE")
    print(f"or check your email {data['email']}")


dataResponse = checkDate(body['date'], headers)

for jadwal in dataResponse['data']:
    waktu_buka = datetime.strptime(jadwal['open_time'].split("+")[0], "%Y-%m-%d %H:%M:%S") + timedelta(hours=7)
    waktu_buka = waktu_buka.strftime("%H:%M")
    waktu_tutup = datetime.strptime(jadwal['close_time'].split("+")[0], "%Y-%m-%d %H:%M:%S") + timedelta(hours=7)
    waktu_tutup = waktu_tutup.strftime("%H:%M")
    print(f"{jadwal['name']}. {waktu_buka} s/d {waktu_tutup} BOOKED {jadwal['booked']} QUOTA {jadwal['qty']}") 
kunjungan = input("pilih kunjungan jam? (1/2/3/4) ")

jadwal = dataResponse['data'][int(kunjungan)-1]
booked = jadwal['booked']
quota = jadwal['qty']

if int(kunjungan) < 0 or int(kunjungan) > 4:
    print("hah? ga ada bego")
    sys.exit(1)

body['slot_id'] = int(kunjungan) + 23
print(f"book for {body['date']} currently {booked} (max {quota})")
loop = input("how many data you want to send? ")
interval = input("do you want to send interval second? (Y/N) ")
min_sec = 0 if interval.lower() == 'n' else int(input("min second? "))
max_sec = 1 if interval.lower() == 'n' else int(input("max second? "))
qty_custom = input("do you want custom qty in the first? (Y/N) ")
for index, loops in enumerate(range(0, int(loop))):
    body = reloadBody(body)
    if index == 0 and qty_custom.lower() != 'n':
        body['qty'] = int(input("how many?"))
    print(f"\n{body}\n")
    fake_book = requests.post("https://ikea-booking.lenna.ai/backend/public/api/public/visitor", headers=headers, json=body)
    if fake_book.status_code != 200:
        print(f"{fake_book.status_code} Can't create the fake book")
        print(fake_book.text)
        # sys.exit(1)
        continue
    print(f"\nBooked Success with code {fake_book.json()['data']['code']} you can access your QRCODE from here : https://ikea-booking.lenna.ai/confirm/{fake_book.json()['data']['code']} ")
    checkdate = checkDate(body['date'], headers)
    jadwal = checkdate['data'][int(kunjungan)-1]
    print(f"Now the booked value is {jadwal['booked']} (max {jadwal['qty']})")
    wait = random.randint(min_sec, max_sec)
    print(f"lets wait for {wait} second")
    time.sleep(wait)
