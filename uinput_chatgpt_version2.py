import os
import struct
import fcntl

# Paths to the character device and uinput device
input_device_path = "/dev/input/event3"
uinput_device_path = "/dev/uinput"

# Open the input device in exclusive mode
input_device = os.open(input_device_path, os.O_RDONLY | os.O_EXCL)
fcntl.ioctl(input_device, 0x80284845, 1)

# Open the uinput device
uinput_device = open(uinput_device_path, "wb")

# Read the input event
input_format = "llHHI"
while True:
    event = input_device.read(struct.calcsize(input_format))
    (tv_sec, tv_usec, type, code, value) = struct.unpack(input_format, event)

    # Write the input event to the uinput device
    uinput_device.write(event)

# Close the devices
input_device.close()
uinput_device.close()
