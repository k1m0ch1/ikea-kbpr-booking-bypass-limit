import sys
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

body_fake = {
    "name": ''.join(random.choice(string.ascii_uppercase) for _ in range(10)),
    "phone_number": f"+628{''.join(random.choice(string.digits) for _ in range(10))}",
    "email": f"{''.join(random.choice(string.ascii_uppercase) for _ in range(10))}@gmail.com",
    "slot_open":"2021-04-15 8:00:00+00",
    "slot_close":"2021-04-15 11:00:00+00",
    "date": "",
    "store_name":"IKEA Kota Baru Parahyangan",
    "store_id": 2,
    "slot_id": 0,
    "qty": 0,
    "age": f"+628{''.join(random.choice(string.digits) for _ in range(2))}",
    "address": ''.join(random.choice(string.ascii_uppercase) for _ in range(25))
}

body_fake['date'] = input("tanggal (YYYY-MM-DD) : ")

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

body['name'] = input("Nama: ")
body['phone_number'] = input("Phone Number: ")
body['email'] = input("email (WAJIB): ")
body['age'] = input("kodepos: ")
body['address'] = input("alamat: ")
body['qty'] = int(input("kunjungan erapa orang? 1-5: "))
if body['qty'] < 0 or body['qty'] > 5:
    print("1-5 orang bapak, ulangi lagi ya")
    sys.exist(1)

jadwal = dataResponse['data'][int(kunjungan)-1]
booked = jadwal['booked']
quota = jadwal['qty']

if int(kunjungan) < 0 or int(kunjungan) > 4:
    print("hah? ga ada bego")
    sys.exit(1)

body['slot_id'] = int(kunjungan) + 23

if booked >= quota:
    fake_qty = (quota-booked)-body['qty']
    body_fake['qty'] = fake_qty
    body_fake['slot_id'] = body['slot_id']
    print(f"The Booked is full {booked} and I will decrese the quota by {fake_qty*-1} so the quota will be {quota-body['qty']}")
    print(f"\n I will send this body request \n {body_fake} \n")
    fake_book = requests.post("https://ikea-booking.lenna.ai/backend/public/api/public/visitor", headers=headers, json=body_fake)
    if fake_book.status_code != 200:
        print(f"{fake_book.status_code} Can't create the fake book")
        print(fake_book.text)
        sys.exit(1)
    checkdate = checkDate(body['date'], headers)
    jadwal = checkdate['data'][int(kunjungan)-1]
    print(f"Now the booked value is {jadwal['booked']}")
    booking(body, headers)
else:
    print(f"The Booked is free {booked} with quota {body['qty']} I will book for you")
    booking(body, headers)
