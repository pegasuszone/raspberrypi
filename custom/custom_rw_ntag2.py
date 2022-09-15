"""
This example shows connecting to the PN532 and writing an NTAG215
type RFID tag
"""
import RPi.GPIO as GPIO

import pn532.pn532 as nfc

from pn532 import *

#pn532 = PN532_SPI(debug=False, reset=20, cs=4)
#pn532 = PN532_I2C(debug=False, reset=20, req=16)
pn532 = PN532_UART(debug=False, reset=20)

# Read user input
print('Enter text to write to NFC card: ')
text = input()
print('\n-----\n')

ic, ver, rev, support = pn532.get_firmware_version()
print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

# Configure PN532 to communicate with NTAG215 cards
pn532.SAM_configuration()

print('Waiting for NFC card to write to...')
while True:
    # Check if a card is available to read
    uid = pn532.read_passive_target(timeout=0.5)
    print('.', end="")
    # Try again if no card is available.
    if uid is not None:
        break
print('Found card with UID:', [hex(i) for i in uid])

print('\n-----\n')

# Handle text array
text_arr = [char for char in text]
text_arr.append(chr(0xFE))

trailing_char = text_arr[0]
text_arr.pop(0)

text_arr_sep = [['', '', '', '']]

incrementer = 0
i = 0

for x in text_arr:
  if incrementer > 3:
    text_arr_sep.append(['', '', '', ''])
    incrementer = 0
    i += 1
  text_arr_sep[i][incrementer] = x
  incrementer += 1

def write_nfc(block, data):
  try:
    pn532.ntag2xx_write_block(block, data)
    if pn532.ntag2xx_read_block(block) == data:
        print('write block %d successfully' % block)
  except nfc.PN532Error as e:
    print(e.errmsg)

# Current block to write
block_number = 6

write_nfc(4, bytes([0x03, 0x16, 0xD1, 0x01]))
write_nfc(5, bytes([0x13, 0x55, 0x04, ord(trailing_char)]))

for block in text_arr_sep:
  data = bytes(r''.join([x for x in block]), 'ascii')
  # data = bytes([0x68, 0x74, 0x74, 0x70])
  try:
    pn532.ntag2xx_write_block(block_number, data)
    if pn532.ntag2xx_read_block(block_number) == data:
        print('write block %d successfully' % block_number)
  except nfc.PN532Error as e:
    print(e.errmsg)
  block_number += 1


GPIO.cleanup()
