==========
LCD Module
==========

This module makes it easier to get started using an Adafruit 16x2 LCD with your Raspberry Pi.

Dependencies
============

This module depends on the following apt packages:

* python-smbus

* i2c-tools

* python-dev

* python-rpi.gpio

Your /etc/modules file should have the following lines in it:

* i2c-bcm2708
  i2c-dev

This module is only designed to be useful on Raspberry Pi systems running Raspbian that have an Adafruit 16x2 LCD screen correctly installed.

Usage
=====

Once you have pip installed raspberry-pi-lcd, you can import lcd into your program. The lcd module exposes the following methods:

* message(text)

	* Displays text on the LCD
