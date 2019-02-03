from motedem import SDK
from bluepy import btle
import sys

addr = sys.argv[1]

print('Connecting to '+addr)
btle_device = btle.Peripheral(addr)
device = SDK.Device(btle_device)
