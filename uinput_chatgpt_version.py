import os
import fcntl
import struct

# Constants for ioctl calls
UI_SET_EVBIT = 0x40045564
UI_SET_KEYBIT = 0x40045565

# Constants for key codes to filter
KEY_MOUSEON = 1198
KEY_MOUSEOFF = 1198

# Open the character device in exclusive mode
device = os.open("/dev/input/event3", os.O_RDONLY | os.O_NONBLOCK)
fcntl.fcntl(device, fcntl.F_SETFL, fcntl.fcntl(device, fcntl.F_GETFL) | os.O_EXCL)

# Open the virtual input device
uinput = os.open("/dev/uinput", os.O_WRONLY | os.O_NONBLOCK)

# Set the type of events to generate
os.ioctl(uinput, UI_SET_EVBIT, struct.pack("I", 0x01))
os.ioctl(uinput, UI_SET_KEYBIT, struct.pack("I", 1))

# Enable the virtual input device
os.write(uinput, struct.pack("16sHHi", "Virtual Input", 0, 0, 0))

while True:
    event = os.read(device, 16)
    (time_sec, time_usec, type, code, value) = struct.unpack("iihhi", event)

    # Filter out certain key codes
    if code not in [KEY_A, KEY_B]:
        os.write(uinput, struct.pack("iihhi", time_sec, time_usec, type, code, value))

# Close the devices
os.close(device)
os.close(uinput)
