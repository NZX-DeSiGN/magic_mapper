import os
import fcntl

# Device file path
device_file = '/dev/input/eventX'

# Codes to filter out
filter_codes = [4, 5, 6]

# Open the device file in exclusive mode
fd = os.open(device_file, os.O_RDONLY | os.O_EXCL)

# Acquire exclusive control of the device
fcntl.ioctl(fd, 0x80284845, 1)

while True:
    # Read input from the device
    event = os.read(fd, 16)

    # Extract the code from the event data
    code = event[10] + (event[11] << 8)

    # Check if the code should be filtered
    if code not in filter_codes:
        # Release exclusive control of the device
        fcntl.ioctl(fd, 0x80284845, 0)
        # Send the unfiltered code back to the device
        os.write(fd, event)
        # Acquire exclusive control of the device again
        fcntl.ioctl(fd, 0x80284845, 1)

# Release exclusive control of the device
fcntl.ioctl(fd, 0x80284845, 0)

# Close the device file
os.close(fd)

