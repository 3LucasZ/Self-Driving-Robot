from pathlib import Path
import yaml
from textwrap import wrap

ROOT_PATH = Path(__file__).parent.parent
CONFIG_PATH = ROOT_PATH.joinpath('config.yaml')

def get_root():
    return ROOT_PATH

def get_config():
    return yaml.safe_load(open(CONFIG_PATH))

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