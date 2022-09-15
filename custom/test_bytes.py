# chr_a = 97

# # https://josefleventon.dev
# text = [
#   0x68, 0x74, 0x74, 0x70, 0x73, 0x3a, 0x2f, 0x2f,  # https://
#   0x6a, 0x6f, 0x73, 0x65, 0x66,                    # josef
#   0x6c, 0x65, 0x76, 0x65, 0x6e, 0x74, 0x6f, 0x6e,  # leventon
#   0x2e, 0x64, 0x65, 0x76                           # .dev
# ]


# # It seems both work just fine!
# print(bytes(text))
# print(bytes("https://josefleventon.dev", 'ascii'))

# ---

text = "https://testnet.pegasus-trade.zone"
text_arr = [char for char in text]
text_arr_sep = [['', '', '', '']]

incrementer = 0
i = 0

for x in text_arr:
  if incrementer > 3:
    text_arr_sep.append(['', '', '', ''])
    incrementer = 0
    i += 1
  text_arr_sep[i][incrementer] = x;
  incrementer += 1

for block in text_arr_sep:
  print(bytes(r''.join([x for x in block]), 'ascii'))