from pymongo import MongoClient
from pymongo.database import Database
import pymongo

import RPi.GPIO as GPIO
import pn532.pn532 as nfc
from pn532 import *

import sys

root = "test.pz-l.ink/"

def get_database() -> Database:
    MONGODB_URI = "mongodb+srv://pegasus:5wJZNZ6KkBudyTGD@pegasuszonedb.pkzyr.mongodb.net/shorturlsDB"
    client = MongoClient(MONGODB_URI)
    return client.get_database()

def get_url(db: Database) -> dict :
    # collections = db.list_collection_names()
    short_urls = db['ShortUrl']
    # urls =  short_urls.find({}, {"destination": 1, "tiny_url":1, "created":1}).limit(1).hint({ created: 1})
    urls =  short_urls.find({}, {"destination": 1, "tiny_url":1, "created":1}).sort('created', -1).limit(1)
    print(urls[0])
    return urls[0]

def write_nfc(block, data):
  try:
    pn532.ntag2xx_write_block(block, data)
    if pn532.ntag2xx_read_block(block) == data:
        print('write block %d successfully' % block, file=sys.stdout)
  except nfc.PN532Error as e:
    print(e.errmsg, file=sys.stderr)


if __name__ == "__main__":
  while True:
    try:
      pn532 = PN532_UART(debug=False, reset=20)

      ic, ver, rev, support = pn532.get_firmware_version()
      pn532.SAM_configuration()

      print('Waiting for NFC card to write to...', file=sys.stdout)
      while True:
          # Check if a card is available to read
          uid = pn532.read_passive_target(timeout=0.5)
          print('.', end="")
          # Try again if no card is available.
          if uid is not None:
              break
      print('Found card with UID:', [hex(i) for i in uid], file=sys.stdout)

      db = get_database()
      url = get_url(db)

      text = root + url['tiny_url']

      # Handle text array
      text_arr = [char for char in text]

      text_arr.append(chr(0xFE))
      text_arr.append(chr(0x00))
      text_arr.append(chr(0x00))
      text_arr.append(chr(0x76))

      trailing_char = text_arr[0]
      text_arr.pop(0)

      text_arr_sep = [[0, 0, 0, 0]]

      incrementer = 0
      i = 0

      for x in text_arr:
        if incrementer > 3:
          text_arr_sep.append([0, 0, 0, 0])
          incrementer = 0
          i += 1
        text_arr_sep[i][incrementer] = ord(x)
        incrementer += 1


      # Current block to write
      block_number = 6

      long_len = len(text) + 5
      short_len = len(text) + 1

      write_nfc(4, bytes([0x03, long_len, 0xD1, 0x01]))
      write_nfc(5, bytes([short_len, 0x55, 0x04, ord(trailing_char)]))

      for block in text_arr_sep:
        data = bytes(block)
        # data = bytes([0x68, 0x74, 0x74, 0x70])
        write_nfc(block_number, data)
        block_number += 1

      for _ in range(block_number, 30):
        data = bytes([0x00, 0x00, 0x00, 0x00])
        write_nfc(block_number, data)
        block_number += 1

      GPIO.cleanup()
    except:
      print("Couldn't write, restarting...", file=sys.stderr)
