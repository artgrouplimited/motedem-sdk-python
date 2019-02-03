# MOTEDEM SDK for Python

This SDK is for a BLE device "MOTEDEM" and target to work on Raspberry Pi

-   [Official Site](https://motedem.com)
-   [Kickstarter Campaign](https://www.kickstarter.com/projects/digitalcreations/motedem-infrared-blaster-with-sdk-for-raspberry-pi)

## Prerequisites

-   [Python 3.5](https://python.org/)
-   [BluePy](https://github.com/IanHarvey/bluepy) (Installed with `pip` when installing this package)

## Installation

```bash
pip install git+https://github.com/artgrouplimited/motedem-sdk-python.git
# or
pip3 install git+https://github.com/artgrouplimited/motedem-sdk-python.git
```

## Usage

```python
from motedem import SDK
from bluepy import btle

addr = '8c:14:7d:00:00:00'
btle_device = btle.Peripheral(addr)
device = SDK.Device(btle_device)

# Do something with the MOTEDEM
temperature = device.readTemperature()
print(temperature)
```

## API

-   `class Device`
    -   `def __init__(self, peripheral)`
    -   `def readTemperature(self)`
    -   `def learnAC(self, ready_callback)`
    -   `def learnAV(self, ready_callback)`
    -   `def emit(self, sequence)`
    -   `def onTemperatureReport(self, handler_or_key)`

### `Device.__init__(self, peripheral)`

Initializes the device.

| Parameter    | Type                     | Description                                    |
| ------------ | ------------------------ | ---------------------------------------------- |
| `peripheral` | `bluepy.btle.Peripheral` | **Required** `Peripheral` object from `bluepy` |

> **IMPORTANT**
>
> Once the `SDK.Device` is constructed, it replace handler of `peripheral` object.<br>
> Suggest to not interact the `peripheral` object after construct `SDK.Device`<br>
> Except calling `peripheral.waitForNotifications` in a loop to dispatch events.<br>
> You must dispatch events yourself if you wish to receive notifications.<br>
> View `Device.onTemperatureReport` as example

### `Device.readTemperature(self)`

Read the temperature sensor data

```python
print("Temperature: "+str(device.readTemperature())+"°C")
```

| Return type | Description                 |
| ----------- | --------------------------- |
| `float`     | The temperature value in °C |

### `Device.learnAC(self, ready_callback)`

```python
data = device.learnAC(lambda sender: print("Ready")))
```

Interprets an AC type infrared signal into a form that can later be reused.

| Parameter        | Type                                  | Description                                                                          |
| ---------------- | ------------------------------------- | ------------------------------------------------------------------------------------ |
| `ready_callback` | `typing.Callable[[SDK.Device], None]` | **Optional** Called when the MOTEDEM is ready to learn infrared signal. See remarks. |

| Return type | Description                     |
| ----------- | ------------------------------- |
| `bytes`     | Learn Data can be use at `emit` |

> #### Remarks
>
> If provided `ready_callback`, require to accept a positional parameter which will be passed the `SDK.Device` that dispatched this call.

### `Device.learnAV(self, ready_callback)`

```python
data = device.learnAV(lambda sender: print("Ready")))
```

Interprets a AV type infrared signal into a form that can later be reused.

| Parameter        | Type                                  | Description                                                                          |
| ---------------- | ------------------------------------- | ------------------------------------------------------------------------------------ |
| `ready_callback` | `typing.Callable[[SDK.Device], None]` | **Optional** Called when the MOTEDEM is ready to learn infrared signal. See remarks. |

| Return type | Description                     |
| ----------- | ------------------------------- |
| `bytes`     | Learn Data can be use at `emit` |

> #### Remarks
>
> If provided `ready_callback`, require to accept a positional parameter which will be passed the `SDK.Device` that dispatched this call.

### `Device.emit(self, sequence)`

Blasts an infrared signal learn from `learnAC` and `learnAV`.

```python
device.emit(b"\x16U\xbf\x953gi\xda`N\xefP\x980'S0M\r\x01\xe40{m\x98\x00\xb81\x01\x11A_!\x110_c\x11\x12]C\x01c]_!_\x82]AcB\x11\x13\x01\x11\x11\x11!\x11@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00B")
```

| Parameter  | Type    | Description                                                     |
| ---------- | ------- | --------------------------------------------------------------- |
| `sequence` | `bytes` | **Required** An infrared signal previously learnt by a MOTEDEM. |

### `Device.onTemperatureReport(self, handler_or_key)`

```python
def report(sender, value):
    print("Temperature: ", value)

device.onTemperatureReport(report)

while True:
    btle_device.waitForNotifications(1)
```

Registers or unregisters handlers that will be called when the MOTEDEM notifies that the temperature report.

| Parameter        | Type                                              | Description                 |
| ---------------- | ------------------------------------------------- | --------------------------- |
| `handler_or_key` | `Callable[[SDK.Device, float], None]`<br>or `int` | **Required**<br>See remarks |

| Return type     | Description |
| --------------- | ----------- |
| `int` or `None` | See remarks |

> #### Remarks
>
> This method base on the type of `handler_or_key`
> will become registers and unregisters event handlers.
>
> If is not `int`, then it must be a `Callable` object which accepts two positional parameters.<br>
> the return value is `int`, which for unregister the `Callable`
>
> If is `int`, then it is unregister the `Callable`<br>
> the return value is `None`.
>
> When the MOTEDEM notifies that report temperature, will invoke all registered handlers<br>
> First parameter is `SDK.Device` that dispatched this call<br>
> Second paramter is room temperature in `float`
