from device import device, btle_device


def report(sender, value):
    print("Temperature: ", value)


device.onTemperatureReport(report)

while True:
    btle_device.waitForNotifications(1)
