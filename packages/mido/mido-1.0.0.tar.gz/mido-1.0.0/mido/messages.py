"""
MIDI messages

There is no need to use this module directly. All you need is
available in the top level module.
"""
import sys

PY2 = (sys.version_info.major == 2)

# Pitchwheel is a 14 bit signed integer
MIN_PITCHWHEEL = -8192
MAX_PITCHWHEEL = 8191

# Song pos is a 14 bit unsigned integer
MIN_SONGPOS = 0
MAX_SONGPOS = 16383


class MessageSpec(object):
    """
    Specifications for creating a message.
    
    status_byte is the first byte of the message. For channel
    messages, the channel (lower 4 bits) is clear.

    type is the type name of the message, for example 'sysex'.

    arguments is the attributes / keywords arguments specific to
    this message type.

    length is the length of this message in bytes. This value is not used
    for sysex messages, since they use an end byte instead.

    Table of MIDI messages:

        http://www.midi.org/techspecs/midimessages.php
    """

    def __init__(self, status_byte, type_, arguments, length):
        """Create a new message specification."""
        self.status_byte = status_byte
        self.type = type_
        self.arguments = arguments
        self.length = length
   
        # Attributes that can be set on the object
        self.valid_attributes = set(self.arguments) | {'time'}

    def signature(self):
        """Return call signature for Message constructor for this type.

        The signature is returned as a string.
        """
        parts = []
        parts.append(repr(self.type))

        for name in self.arguments:
            if name == 'data':
                parts.append('data=()')
            else:
                parts.append('{}=0'.format(name))
        parts.append('time=0')

        sig = '({})'.format(', '.join(parts))

        return sig


def get_message_specs():
    return [
        # Channel messages
        MessageSpec(0x80, 'note_off', ('channel', 'note', 'velocity'), 3),
        MessageSpec(0x90, 'note_on', ('channel', 'note', 'velocity'), 3),
        MessageSpec(0xa0, 'polytouch', ('channel', 'note', 'value'), 3),
        MessageSpec(0xb0, 'control_change',
                    ('channel', 'control', 'value'), 3),
        MessageSpec(0xc0, 'program_change', ('channel', 'program',), 2),
        MessageSpec(0xd0, 'aftertouch', ('channel', 'value',), 2),
        MessageSpec(0xe0, 'pitchwheel', ('channel', 'pitch',), 3),

        # System common messages
        MessageSpec(0xf0, 'sysex', ('data',), float('inf')),
        MessageSpec(0xf1, 'undefined_f1', (), 1),  # Todo: support this.
        # MessageSpec(0xf1, 'time_code', ('value'), 2),
        MessageSpec(0xf2, 'songpos', ('pos',), 3),
        MessageSpec(0xf3, 'song_select', ('song',), 2),
        MessageSpec(0xf4, 'undefined_f4', (), 1),
        MessageSpec(0xf5, 'undefined_f5', (), 1),
        MessageSpec(0xf6, 'tune_request', (), 1),
        MessageSpec(0xf7, 'sysex_end', (), 1),

        # System real time messages
        MessageSpec(0xf8, 'clock', (), 1),
        MessageSpec(0xf9, 'undefined_f9', (), 1),
        MessageSpec(0xfa, 'start', (), 1),
        MessageSpec(0xfb, 'continue', (), 1),
        MessageSpec(0xfc, 'stop', (), 1),
        MessageSpec(0xfd, 'undefined_fd', (), 1),
        MessageSpec(0xfe, 'active_sensing', (), 1),
        MessageSpec(0xff, 'reset', (), 1),
    ]


def build_spec_lookup(message_specs):
    lookup = {}

    for spec in message_specs:
        status_byte = spec.status_byte

        if status_byte < 0xf0:
            # Channel message.
            # The upper 4 bits are message type, and
            # the lower 4 are MIDI channel.
            # We need lookup for all 16 MIDI channels.
            for channel in range(16):
                lookup[status_byte | channel] = spec
        else:
            lookup[status_byte] = spec

        lookup[spec.type] = spec

    return lookup


def get_spec(type_or_status_byte):
    """Get message specification from status byte or message type name.

    For use in writing parsers.
    """
    try:
        return Message._spec_lookup[type_or_status_byte]
    except KeyError:
        raise LookupError('unknown type or status byte')


def check_time(time):
    """Check type and value of time.
    
    Raises TypeError if value is not an integer or a float
    """
    if PY2 and isinstance(time, long):
        return

    if not (isinstance(time, int) or isinstance(time, float)):
        raise TypeError('time must be an integer or float')


def check_channel(channel):
    """Check type and value of channel.

    Raises TypeError if the value is not an integer, and ValueError if
    it is outside range 0..127.
    """
    if not isinstance(channel, int):
        raise TypeError('channel must be an integer')
    elif not 0 <= channel <= 15:
        raise ValueError('channel must be in range 0..15')


def check_pos(pos):
    """Check type and value of song position.

    Raise TypeError if the value is not an integer, and ValueError if
    it is outside range MIN_SONGPOS..MAX_SONGPOS.
    """
    if not isinstance(pos, int):
        raise TypeError('song pos must be and integer')
    elif not MIN_SONGPOS <= pos <= MAX_SONGPOS:
        raise ValueError('song pos must be in range {}..{}'.format(
                         MIN_SONGPOS, MAX_SONGPOS))


def check_pitch(pitch):
    """Raise TypeError if the value is not an integer, and ValueError
    if it is outside range MIN_PITCHWHEEL..MAX_PITCHWHEEL.
    """
    if not isinstance(pitch, int):
        raise TypeError('pichwheel value must be an integer')
    elif not MIN_PITCHWHEEL <= pitch <= MAX_PITCHWHEEL:
        raise ValueError('pitchwheel value must be in range {}..{}'.format(
                         MIN_PITCHWHEEL, MAX_PITCHWHEEL))


def check_data(data_bytes):
    """Check type of data_byte and type and range of each data byte.

    Returns the data bytes as a tuple of integers.

    Raises TypeError if value is not iterable.
    Raises TypeError if one of the bytes is not an integer.
    Raises ValueError if one of the bytes is out of range 0..127.
    """
    # Make the sequence immutable.
    data_bytes = tuple(data_bytes)

    for byte in data_bytes:
        check_databyte(byte)

    return data_bytes


def check_databyte(value):
    """Raise exception of byte has wrong type or is out of range

    Raises TypeError if the byte is not an integer, and ValueError if
    it is out of range. Data bytes are 7 bit, so the valid range is
    0..127.
    """
    if not isinstance(value, int):
        raise TypeError('data byte must be an integer')
    elif not 0 <= value <= 127:
        raise ValueError('data byte must be in range 0..127')


def encode_channel(channel):
    """Convert channel into a list of bytes. Return an empty list of
    bytes, since channel is already masked into status byte.
    """
    return []


def encode_data(data):
    """Encode sysex data as a list of bytes. A sysex end byte (0xf7)
    is appended.
    """
    return list(data) + [0xf7]

 
def encode_pitch(pitch):
    """Encode pitchwheel pitch as a list of bytes."""
    pitch -= MIN_PITCHWHEEL
    return [pitch & 0x7f, pitch >> 7]


def encode_pos(pos):
    """Encode song position as a list of bytes."""
    return [pos & 0x7f, pos >> 7]


class BaseMessage(object):
    """Base class for MIDI messages.

    Can be subclassed to create meta messages, for example.
    """
    pass

class Message(BaseMessage):
    """
    MIDI message class.
    """

    # Quick lookup of specs by name or status_byte.
    _spec_lookup = build_spec_lookup(get_message_specs())

    def __init__(self, type_, **parameters):
        """Create a new message.

        The first argument is typically the type of message to create,
        for example 'note_on'.

        It can also be the status_byte, that is the first byte of the
        message. For channel messages, the channel (lower 4 bits of
        the status_byte) is masked out from the lower 4 bits of the
        status byte. This can be overriden by passing the 'channel'
        keyword argument.
        """
        try:
            spec = self._spec_lookup[type_]
        except KeyError:
            text = '{!r} is an invalid type name or status byte'
            raise ValueError(text.format(type_))

        self._set('_spec', spec)
        self._set('type', self._spec.type)

        self._set_attributes_to_default_values(type_)
        self._override_attributes(parameters)

    def _set_attributes_to_default_values(self, type_):
        for name in self._spec.arguments:
            if name == 'data':
                self.data = ()
            elif name == 'channel':
                # This is a channel message, so if the first
                # argument to this function was a status_byte,
                # the lower 4 bits will contain the channel.
                if isinstance(type_, int):
                    self.channel = type_ & 0x0f
                else:
                    self.channel = 0
            else:
                setattr(self, name, 0)
        self._set('time', 0)

    def _override_attributes(self, parameters):
        for name, value in parameters.items():
            try:
                setattr(self, name, value)
            except AttributeError:
                raise ValueError('{!r} is an invalid'
                                 ' keyword argument for this message type'
                                 ''.format(name))

    def copy(self, **overrides):
        """Return a copy of the message.

        Attributes will be overriden by the passed keyword arguments.
        Only message specific attributes can be overridden. The message
        type can not be changed.

        Example:

            a = Message('note_on')
            b = a.copy(velocity=32)
        """
        # Get values from this object
        arguments = {}
        for name in self._spec.valid_attributes:
            if name in overrides:
                arguments[name] = overrides[name]
            else:
                arguments[name] = getattr(self, name)

        for name in overrides:
            if name not in self._spec.valid_attributes:
                text = '{!r} is an invalid argument for this message type'
                raise ValueError(text.format(name))

        return self.__class__(self.type, **arguments)

    def _set(self, name, value):
        """Sets an attribute directly, bypassing all type and value checks"""
        self.__dict__[name] = value

    def __setattr__(self, name, value):
        """Set an attribute."""

        if name in self._spec.valid_attributes:
            try:
                check = globals()['check_{}'.format(name)]
            except KeyError:
                check = check_databyte

            ret = check(value)
            if name == 'data':
                value = ret

            self.__dict__[name] = value
        elif name in self.__dict__:
            raise AttributeError('{} attribute is read only'.format(name))
        else:
            raise AttributeError('{} message has no attribute {}'.format(
                                 self.type, name))

    def __delattr__(self, name):
        raise AttributeError('attribute can not be deleted')

    def bytes(self):
        """Encode message and return as a list of integers."""

        status_byte = self._spec.status_byte
        if status_byte < 0xf0:
            # Add channel (lower 4 bits) to status byte.
            # Those bits in spec.status_byte are always 0.
            status_byte |= self.channel

        message_bytes = [status_byte]

        for name in self._spec.arguments:
            value = getattr(self, name)
            try:
                encode = globals()['encode_{}'.format(name)]
                message_bytes.extend(encode(value))
            except KeyError:
                message_bytes.append(value)

        return message_bytes

    def bin(self):
        """Encode message and return as a bytearray.

        This can be used to write the message to a file.
        """
        return bytearray(self.bytes())

    def hex(self, sep=' '):
        """Encode message and return as a string of hex numbers,

        Each number is separated by the string sep.
        """
        return sep.join(['{:02X}'.format(byte) for byte in self.bytes()])

    def __repr__(self):
        parts = []

        for name in self._spec.arguments + ('time',):
            parts.append('{}={!r}'.format(name, getattr(self, name)))

        return '<{} message {}>'.format(self.type, ', '.join(parts))

    def __str__(self):
        return _format_as_string(self)

    def __eq__(self, other):
        """Compare message to another for equality.
        
        Key for comparison: (msg.type, msg.channel, msg.note, msg.velocity).
        """
        if not isinstance(other, Message):
            raise TypeError('comparison between Message and another type')

        def key(msg):
            """Return a key for comparison."""
            return [msg.type] + [
                getattr(msg, arg) for arg in msg._spec.arguments]

        return key(self) == key(other)

    def __len__(self):
        if self.type == 'sysex':
            return len(self.data) + 2
        else:
            return self._spec.length


def parse_time(text):
    if text.endswith('L'):
        raise ValueError('L is not allowed in time')

    if PY2:
        converters = [int, long, float]
    else:
        converters = [int, float]

    for convert in converters:
        try:
            return convert(text)
        except ValueError:
            pass

    raise ValueError('invalid format for time')


def parse_string(text):
    """Parse a string of text and return a message.

    The string can span multiple lines, but must contain
    one full message.

    Raises ValueError if the string could not be parsed.
    """
    words = text.split()

    message = Message(words[0])
    arguments = words[1:]

    names_seen = set()

    for argument in arguments:
        try:
            name, value = argument.split('=')
        except ValueError:
            raise ValueError('missing or extraneous equals sign')

        if name in names_seen:
            raise ValueError('argument passed more than once')
        names_seen.add(name)

        if name == 'data':
            if not value.startswith('(') and value.endswith(')'):
                raise ValueError('missing parentheses in data message')

            try:
                data_bytes = [int(byte) for byte in value[1:-1].split(',')]
            except ValueError:
                raise ValueError('unable to parse data bytes')
            setattr(message, 'data', data_bytes)
        elif name == 'time':
            try:
                time = parse_time(value)
            except ValueError:
                raise ValueError('invalid value for time')
            try:
                setattr(message, 'time', time)
            except AttributeError as err:
                raise ValueError(err.message)
            except TypeError as err:
                raise ValueError(err.message)
        else:
            try:
                setattr(message, name, int(value))
            except AttributeError as exception:
                raise ValueError(*exception.args)
            except ValueError:
                raise ValueError('{!r} is not an integer'.format(value))

    return message


def parse_string_stream(stream):
    """Parse a stram of messages and yield (message, error_message)

    stream can be any iterable that generates text strings. If
    a line can be parsed, (message, None) is returned. If it can't
    be parsed (None, error_message) is returned. The error message
    containes the line number where the error occured.
    """
    line_number = 1
    for line in stream:
        try:
            line = line.split('#')[0].strip()
            if line:
                yield parse_string(line), None
        except ValueError as exception:
            error_message = 'line {line_number}: {message}'.format(
                line_number=line_number,
                message=exception.args[0])
            yield None, error_message
        line_number += 1


def _format_as_string(message):
    """Format a message and return as a string.

    There is no reason to call this function directly.
    Use str(message) instead.
    """
    if not isinstance(message, Message):
        raise ValueError('message must be a mido.Message object')

    words = []
    words.append(message.type)

    for name in message._spec.arguments + ('time',):
        value = getattr(message, name)
        if name == 'data':
            value = '({})'.format(','.join([str(byte) for byte in value]))
        elif name == 'time':
            # Python 2 formats longs as '983989385L'. This is not allowed.
            value = str(value)
            value = value.replace('L', '')
        words.append('{}={}'.format(name, value))
    
    return ' '.join(words)
