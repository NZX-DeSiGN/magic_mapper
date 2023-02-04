## Setup buildroot
- sudo apt install ncurses-dev
- git clone git@github.com:openlgtv/buildroot-nc4.git
- cd buildroot-nc4
- make menuconfig
- Select architecture: aarch64 (little endian)
- Select Processor
  - C9: cortex-A73



## Links
- https://github.com/openlgtv/buildroot-nc4
- http://billauer.co.il/blog/2013/05/buildroot-cross-compiler-arm/
