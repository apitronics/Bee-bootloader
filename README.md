Bee-bootloader
==============

Reference: [Xbee 900HB Manual](ftp://ftp1.digi.com/support/documentation/90002173_B.pdf)

Bee bootloader project

PYTHON
- maximum packet size with Xbee 900HB is 256. Expressed as global variable in Xbee.py
- improve library so that messages are objects
  - make sure print prints numbers in HEX
- refactor things so that escape bits are used (Arduino Xbee library requires escape characters so that way we match it)
  - page 57 in documentation 

  
  
BOOTLOADER
- needs to parse firmware code from multiple packets


API Specifications

Any packet has this kind of prefix:

| START DELIMITER (0x7E) | LENGTH (MSB) | LENGTH (LSB)     | FRAME TYPE (TRANSMIT=0x10) | FRAME ID (want ACK) | 
|:----------------------:|:------------:|:----------------:|:--------------------------:|:-------------------:|
|           0            |      1       |        2         |            3               |          4          |


Finally, there is a suffix of the checksum. In python, checksum can be calcualted: `(0xFF-sum(i[3:-2])&255)`

**WARNING**: this gets a little trickier with escape bytes 
