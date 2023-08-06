1.1 - 2013-10-01
-----------------

* added support for selectable backends (with MIDO_BACKEND) and
  included python-rtmidi and pygame backends in the official library
  (as mido.backend.rtmidi and mido.backend.pygame).

* added full support for MIDI files (read, write playback)

* added MIDI over TCP/IP (socket ports)

* added utility programs mido-play, mido-ports, mido-serve and mido-forward.

* added support for SMPTE time code quarter frames.

* port constructors and ``open_*()`` functions can now take keyword
  arguments.

* output ports now have reset() and panic() methods.

* new environment variables MIDO_DEFAULT_INPUT, MIDO_DEFAULT_OUTPUT
  and MIDO_DEFAULT_IOPORT. If these are set, the open_*() functions
  will use them instead of the backend's default ports.

* added new meta ports MultiPort and EchoPort.

* added new examples and updated the old ones.

* format_as_string() now takes an include_time argument (defaults to True)
  so you can leave out the time attribute.

* sleep time inside sockets can now be changed.

* Message() no longer accepts a status byte as its first argument. (This was
  only meant to be used internally.)

* added callbacks for input ports (PortMidi and python-rtmidi)

* PortMidi and pygame input ports now actually block on the device
  instead of polling and waiting.

* removed commas from repr() format of Message and MetaMessage to make
  them more consistent with other classes.


1.0.4 - 2013-08-15
-------------------

* rewrote parser


1.0.3 - 2013-07-12
-------------------

* bugfix: __exit__() didn't close port.

* changed repr format of message to start with "message".

* removed support for undefined messages. (0xf4, 0xf5, 0xf7, 0xf9 and 0xfd.)

* default value of velocity is now 64 (0x40).
  (This is the recommended default for devices that don't support velocity.)


1.0.2 - 2013-07-31
-------------------

* fixed some errors in the documentation.


1.0.1 - 2013-07-31 - bugfix
----------------------------

* multi_receive() and multi_iter_pending() had wrong implementation.
  They were supposed to yield only messages by default.

1.0 - 2013-07-20 - initial release
-------------------------------------

Basic functionality: messages, ports and parser.
