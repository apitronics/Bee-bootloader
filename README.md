Bee-bootloader
==============

# Dependencies
* AVR studio (tested with 6.1)
* avrdude (tested with 6.1 built from source, the version in the Debian repositories does /not/ work)
The boot loader is in the same repository as the library which is a bit of a mess but it makes it easy to build

# Building
start the avr studio shell

     cd to lufa/Bootloaders/CDC/
     make

the file "BootloaderCDC.hex" should be loaded onto the micro controller
# Using
    avrdude -c avr109 -p x128a3u -P /dev/ttyACM0 -D -U flash:w:./rom.hex -C ./avrdude.conf
(specifying your avrdude.conf is not necessary if you have replaced the older avrdude.conf)

# TODO
* Figure out what's wrong with reading the test switch 
* Integrate Xbee stuff

#Possible XBee Path

Reference: Xbee 900HB Manual: ftp://ftp1.digi.com/support/documentation/90002173_B.pdf

Bee bootloader project

# PYTHON #
- maximum packet size with Xbee 900HB is 256. Expressed as global variable in Xbee.py
- refactor things so that escape bits are used (Arduino Xbee library requires escape characters so that way we match it)
  - page 57 in documentation

  
  
# BOOTLOADER #
- needs to parse firmware code from multiple packets


## Xbee API Specifications ##

Any packet will have this kind of prefix:

| START DELIMITER (0x7E) | LENGTH (MSB) | LENGTH (LSB)     | FRAME TYPE (TRANSMIT=0x10) | FRAME ID (want ACK) | 
|:----------------------:|:------------:|:----------------:|:--------------------------:|:-------------------:|
|           0            |      1       |        2         |            3               |          4          |


Then, there is the actual API frame.

Finally, there is the suffix of the checksum. In python, checksum can be calcualted: `(0xFF-sum(i[3:-1])&255)`

## Escape Bytes ##

Note that the API mode we are using implement escape bytes so that we can be compatible with the Xbee-Arduino library.
Here is the relevant documentation:

Data bytes that need to be escaped:
• 0x7E – Frame Delimiter
• 0x7D – Escape
• 0x11 – XON
• 0x13 – XOFF

Example -
Raw serial data frame (before escaping interfering bytes):
0x7E 0x00 0x02 0x23 0x11 0xCB

0x11 needs to be escaped which results in the following frame:
0x7E 0x00 0x02 0x23 0x7D 0x31 0xCB

Note: In the above example, the length of the raw data (excluding the checksum) is 0x0002 and the checksum of the non-escaped data (excluding frame delimiter and length) is calculated as:
0xFF - (0x23 + 0x11) = (0xFF - 0x34) = 0xCB

## Apitronics API Specifications ##

When the Xbee FRAME TYPE is transmit, then we enter the world of our own custom API.

Byte 5: 
  bit 7: ACK request
  bit 6-4: Apitronics Frame
  bit 3-0: MS-half Byte Index

Byte 6: LSB Index

This means that the maximum index is 2**12=4096 which is enough to transmit over 1MB.
It also means that the Apitronics Frame set can have at most 8 frames.

|     ACK and Index      |    Index     | Actual Data      | 
|:----------------------:|:------------:|:----------------:|
|           5            |      6       |   7 til end      |    
