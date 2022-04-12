from Crypto.Cipher import Blowfish
from struct import pack

bs = Blowfish.block_size
key = b'An arbitrarily long key'
ciphertext = b'\xe2:\x141vp\x05\x92\xd7\xfa\xb5@\xda\x05w.\xaaRG+U+\xc5G\x08\xdf\xf4Xua\x88\x1b'
iv = ciphertext[:bs]
ciphertext = ciphertext[bs:]

cipher = Blowfish.new(key, Blowfish.MODE_CBC, iv)
msg = cipher.decrypt(ciphertext)

last_byte = msg[-1]
msg = msg[:- (last_byte if type(last_byte) is int else ord(last_byte))]
print(repr(msg))
