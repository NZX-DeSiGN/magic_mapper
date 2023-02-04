import os
import struct
import fcntl

# Constants for the character device
EV_KEY = 0x01

# Open the character device
device = open('/dev/input/event0', 'rb', 0)

# Set the file descriptor to be exclusive
fcntl.ioctl(device, 0x4501, struct.pack("L", 0x80 | 0x01))

# Read input events from the character device
while True:
    # Read the next input event
    event = device.read(16)

    # Unpack the event data
    time, type, code, value = struct.unpack("QHHi", event)

    # Check if the event is a key event
    if type == EV_KEY:
        # Print the key event data
        print "Key event: time=%d type=%d code=%d value=%d" % (time, type, code, value)
