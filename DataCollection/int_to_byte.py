from textwrap import wrap
def int_to_byte_array(num):
   if num < 0:
      hexStr = hex((1<<32) + num)
   else:
      hexStr = hex(num)
   hexStr = hexStr.rstrip("L")

   padded = str.format('{:08X}',int(hexStr,16))
   padded = wrap(padded,2)

   array = [0,0,0,0]
   for x in range(4):
      array[x] = int(padded[x],16)

   array.reverse()

   return array

if __name__ == 'main':
    print(int_to_byte_array(-100))