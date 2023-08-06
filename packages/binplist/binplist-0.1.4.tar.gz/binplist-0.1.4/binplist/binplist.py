#!/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Parser for Apple's binary plist (Property List) files.

Based on the specification at:
  http://opensource.apple.com/source/CF/CF-550/CFBinaryPList.c

To parse a plist from a file you can use the readPlist(fileOrObj) function
with a file name or a file-like object. It returns the top level object,
which will usually be a dictionary.

Forensic use

If you are using this module, though, chances are you are a forensicator and
you want to be able to get all the information on the plist even when they
are corrupt. For this use case, it's better to create an instance of the
BinaryPlist class and then call the Parse() method on it, with a file-like
object as an argument.

  with open("myfile.plist", "rb") as fd:
    bplist = BinaryPlist(fd)
    top_level_object = bplist.Parse(fd)

The Parse method returns the top level object, just as readPlist.
Once parsed, you can check BinaryPlist.is_corrupt to find out whether the plist
had corrupt data. You will find a dictionary with all objects within the bplist
at BinaryPlist.objects. The dictionary keys are the indexes of each object, and
the values are its parsed contents.

So if a binary plist contains this dictionary:
    {"a": True}

The binary plist will have 3 objects. A dictionary, a string "a" and a True
value. BinaryPlist.objects will contain 3 entries as well, one for each object.

You have a mapping of object index to offset at BinaryPlist.object_offsets.
And the top_level_element index is available ad BinaryPlist.top_level_index.

Happy bplisting!
"""

from . import __version__
from . import __feedback_email__

import datetime
import logging
import math
import os
import plistlib
import string
import struct
import xml.parsers.expat

import pytz


LOG_ULTRA_VERBOSE = -10


class NullValue(object):
  """Identifies the Null object."""


class RawValue(object):
  """Used when objects are corrupt and no sensible value can be extracted."""

  def __init__(self, value):
    self.value = value

  def __str__(self):
    return self.value

  def __repr__(self):
    return repr(self.value)

  def __eq__(self, other):
    return self.value == other

  def __unicode__(self):
    return u"'%s'" % ''.join([u"\\x%s" % c.encode('hex') for c in self.value])


class CorruptReference(object):
  """Marks references to objects that are corrupt."""


class UnknownObject(object):
  """Marks objects that we don't know how to parse."""


class Error(Exception):
  """Base exception."""


class FormatError(Error):
  """Error while parsing the bplist format."""


BIG_ENDIAN = 0
LITTLE_ENDIAN = 1


class BinaryPlist(object):
  """Represents a binary plist."""

  # Maps markers to human readable object types and their parsing function
  KNOWN_MARKERS = {
      0x0: ("BOOLFILL", "_ParseBoolFill"),
      0x1: ("INT", "_ParseInt"),
      0x2: ("REAL", "_ParseReal"),
      0x3: ("DATE", "_ParseDate"),
      0x4: ("DATA", "_ParseData"),
      0x5: ("STRING", "_ParseString"),
      0x6: ("UTF16", "_ParseUtf16"),
      0x8: ("UID", "_ParseUid"),
      0xA: ("ARRAY", "_ParseArray"),
      0xC: ("SET", "_ParseSet"),
      0xD: ("DICT", "_ParseDict"),
  }

  # Several data structures in binary plists explicitly define the size of an
  # integer that's stored next to the declared size.
  # We maintain a mapping of byte sizes to python struct format characters to
  # use them in these cases.
  bytesize_to_uchar = {1: "B", 2: "H", 4: "L", 8: "Q"}

  # Timestamps in binary plists are relative to 2001-01-01T00:00:00.000000Z
  plist_epoch = datetime.datetime(2001, 1, 1, 0, 0, 0, tzinfo=pytz.utc)

  # Length of the preview we show for each object when DEBUG logging
  debug_object_preview_length = 48

  def __init__(self, file_obj=None, discovery_mode=False,
               ultra_verbosity=False):
    """Constructor.

    Args:
      file_obj: File-like object to read from.
      discovery_mode: When activated, it will inform the user when one of the
      uncommon objects has been found. It's expected to be used while we finish
      validating the parser against real binary plists. Disabled by default.
    """
    self.discovery_mode = discovery_mode
    self.ultra_verbosity = ultra_verbosity
    self._Initialize()
    self.fd = None
    if file_obj:
      self.Open(file_obj)

  def _Initialize(self):
    """Resets all the parsing state information."""
    # A list of all the offsets. You can find an object's offset by indexing
    # this list with the object index
    self.object_offsets = []
    # A dictionary of object indexes and parsed object values
    self.objects = {}
    self.is_corrupt = False
    # Header attributes
    self.version = ""
    # Trailer attributes
    self.sort_version = 0
    self.offset_int_size = 0
    self.object_ref_size = 0
    self.object_count = 0
    self.top_level_index = None
    self.offtable_offset = 0
    # List of traversed object indexes to detect circular references
    self.objects_traversed = set()

  @property
  def top_level_object(self):
    if self.top_level_index is None:
      return None
    return self._ParseObjectByIndex(self.top_level_index, self.object_offsets)

  def Open(self, file_obj):
    try:
      start_offset = file_obj.tell()
      file_obj.seek(0, os.SEEK_END)
      self._file_size = file_obj.tell() - start_offset
      file_obj.seek(start_offset, os.SEEK_SET)
      self._bplist_start_offset = start_offset
      self.fd = file_obj
    except AttributeError:
      raise Error("This file object doesn't support seek().")

  def Parse(self):
    """Parses the file descriptor at file_obj."""
    self._Initialize()
    if not self.fd:
      raise IOError("No data available to parse. Did you call Open() ?")
    # Each of these functions will raise if an unrecoverable error is found
    self._ReadHeader()
    self._ReadTrailer()
    self._ReadOffsetTable()
    self._ParseObjects()
    return self._ParseObjectByIndex(self.top_level_index, self.object_offsets)

  def Close(self):
    self.fd = None

  def _ReadHeader(self):
    """Parses the bplist header.

    The binary plist header contains the following structure:

        OFFSET  ELEMENTS  TYPE   DESCRIPTION
        0       6         uint8  Magic number
        6       2         uint8  Plist version

    Raises:
      FormatError: When the header is too short or the magic value is invalid.
    """

    header_struct = struct.Struct(">6s2s")
    data = self.fd.read(header_struct.size)
    if len(data) != header_struct.size:
      raise FormatError("Wrong header length (got %d, expected %ld)." %
                        (len(data), header_struct.size))
    magic, self.version = header_struct.unpack(data)
    if magic != "bplist":
      raise FormatError("Wrong magic '%s', expecting 'bplist'." % magic)
    self._LogDebug("MAGIC = %s", magic)
    self._LogDebug("VERSION = %s", self.version)
    if self.version[0] != "0":
      self._LogWarn("Unknown version. Proceeding anyway...")

  def _ReadTrailer(self):
    """Parses the trailer.

    The binary plist trailer consists of the following structure at the end of
    the file.

        OFFSET  ELEMENTS  TYPE    DESCRIPTION
        0       5         uint8   Unused bytes
        5       1         uint8   Sort version
        6       1         uint8   Offset to the integer size
        7       1         uint8   Offset to the object reference size
        8       1         uint64  Number of objects
        16      1         uint64  Top object identifier
        24      1         uint64  Offset to the offset table

    Raises:
      IOError: When there is not enough data for the trailer.
    """

    trailer_struct = struct.Struct(">5xBBBQQQ")  # YUMMY!
    trailer_size = trailer_struct.size
    self.fd.seek(-trailer_size, os.SEEK_END)
    data = self.fd.read(trailer_size)
    if len(data) != trailer_size:
      raise IOError("Wrong trailer length (got %d, expected %ld." %
                    (len(data), trailer_struct.size))
    (self.sort_version,
     self.offset_int_size,
     self.object_ref_size,
     self.object_count,
     self.top_level_index,
     self.offtable_offset) = trailer_struct.unpack(data)

    self._LogDebug("Sort: %d", self.sort_version)
    self._LogDebug("int size: %d", self.offset_int_size)
    self._LogDebug("ref size: %d", self.object_ref_size)
    self._LogDebug("obects available: %d", self.object_count)
    self._LogDebug("top object: %d", self.top_level_index)
    self._LogDebug("Offset table: %d", self.offtable_offset)

  def _ReadOffsetTable(self):
    """Parses the bplist offset table.

    The offset table is a list of integers of size between 1 and 8 bytes. Each
    points to the file offset where the relevant object is located.

    The integer size comes from the trailer.

    Raises:
      FormatError: When the offset to the offset table is invalid or the
      offset table overflows the file contents.
    """

    self.object_offsets = []
    if self.offtable_offset >= self._file_size:
      raise FormatError("Offset table offset past the file end.")

    self.fd.seek(self._bplist_start_offset + self.offtable_offset)
    # Offsets table declared length
    data_size = self.object_count * self.offset_int_size
    # SANITY CHECK: See if the offset table is contained in the file
    if data_size > (self._file_size - self.offtable_offset):
      raise FormatError("Length of offsets table larger than the data available"
                        "in the file (%d vs %ld)." %
                        (data_size, self._file_size))

    for object_index in range(self.object_count):
      # We can have offsets of sizes 1 to 8 bytes so we can't just use struct
      offset = self._ReadArbitraryLengthInteger(self.offset_int_size)
      self._LogDebug("Object %d offset = %ld.", object_index, offset)
      self.object_offsets.append(offset)

  def _ReadArbitraryLengthInteger(self, length=0, endianness=BIG_ENDIAN):
    """Returns an integer from self.fd of the given length and endianness."""
    self._LogUltraVerbose("read arbitrary length integer length %d", length)
    data = self.fd.read(length)
    if len(data) < length:
      length = len(data)
      self._LogUltraVerbose("Not enough data, reading %d instead.", length)
    integer = 0
    if endianness is BIG_ENDIAN:
      for data_index in range(0, length, 1):
        integer <<= 8
        integer |= ord(data[data_index])
    elif endianness is LITTLE_ENDIAN:
      for data_index in range(length-1, -1, -1):
        integer <<= 8
        integer |= ord(data[data_index])
    else:
      raise ValueError("Unknown endianness requested: %d" % endianness)
    return integer

  def _ParseObjects(self):
    """Parses the objects at file offsets contained in object_offsets."""
    self.objects = {}
    for object_index, offset in enumerate(self.object_offsets):
      self._LogDebug(">>> PARSING OBJECT %d AT OFFSET %ld",
                    object_index, offset)
      self._ParseObjectByIndex(object_index, self.object_offsets)

  def _ParseObjectByIndex(self, index, offset_list):
    """Returns an object by its index.

    If the object has already been parsed, it's not parsed again, but served
    from the cached version instead.

    Args:
      index: The 0-based index of the object in the offset_list.
      offset_list: A list of offsets for each of the available objects in the
      binary plist file.

    Returns:
      The object.

    Raises:
      IndexError: If the index is invalid.
    """

    # Add the object to the list of traversed objects
    self.objects_traversed.add(index)
    offset = offset_list[index]
    self._LogDebug("Parsing object at index %d", index)
    try:
      obj = self.objects[index]
      self._LogDebug("Skipping: Object had already been parsed.")
    except KeyError:
      if offset > self._file_size:
        # This only happens when the offset in the offset table is wrong
        obj = CorruptReference
      else:
        self.fd.seek(self._bplist_start_offset + offset)
        obj = self._ParseObject()
        self.objects[index] = obj
    finally:
      # Remove the index from the list of traversed objects
      self.objects_traversed.remove(index)
    output_string = ToDebugString(obj)
    fmt = "Object %d = %s"
    if len(output_string) > self.debug_object_preview_length:
      fmt = "Object %%d ~= %%.%ds ..." % self.debug_object_preview_length
    self._LogUltraVerbose(fmt, index, output_string)
    return obj

  def _ParseObject(self):
    """Parses the binary plist object available in self.fd.

    Every object in a plist starts with a marker. The markers is a single byte
    where the high nibble indicates the type. The lower nibble meaning depends
    on the object type.

    Returns:
      A python object representing the plist object.

    Raises:
      IOError: When there's not enough data in self.fd to read a new object.
    """

    self._LogUltraVerbose("At offset %d", self.fd.tell())
    marker_string = self.fd.read(1)
    if len(marker_string) < 1:
      raise IOError("Not enough data available to read a new object.")
    marker = ord(marker_string[0])
    self._LogUltraVerbose(">> MARKER: 0x%02lx", marker)
    marker_lo = (marker & 0x0F)
    marker_hi = (marker & 0xF0) >> 4
    self._LogUltraVerbose(">> MARKER HI: %lx", marker_hi)
    self._LogUltraVerbose(">> MARKER LO: %lx", marker_lo)
    try:
      (marker_name, parsing_function_name) = self.KNOWN_MARKERS[marker_hi]
      self._LogDebug("DATA TYPE: %s", marker_name)
      return getattr(self, parsing_function_name)(marker_lo)
    except KeyError:
      self._LogWarn("UNKNOWN MARKER %lx", marker)
      return UnknownObject

  def _ParseBoolFill(self, marker_lo):
    """Parses a null, boolean or fill object.

    Args:
      marker_lo: The lower nibble of the marker.

    Returns:
      NullValue, True, False or None when it's a fill byte. If the object type
      is unknown, UnknownObject is returned instead.
    """
    ret_values = {0x00: NullValue, 0x08: False, 0x09: True, 0xF: None}
    # SANITY CHECK: No values outside these are known
    try:
      return ret_values[marker_lo]
    except KeyError:
      self._LogWarn("Simple value type %d unknown.", marker_lo)
      return UnknownObject

  def _ParseInt(self, marker_lo):
    """Parses an integer object.

    Args:
      marker_lo: The lower nibble of the marker.

    Returns:
      The integer value or RawValue when it's corrupt.
    """
    int_bytes = 1 << marker_lo
    self._LogUltraVerbose("Integer size %d", int_bytes)
    # SANITY CHECK: The only allowed integer lengths by OSX seem to be 1, 2, 4,
    # 8 or 16 bytes.
    # XXX: Revisit this and decide if we should instead accept any length.
    if marker_lo not in [0, 1, 2, 3, 4]:
      self._LogWarn("Non-standard integer length (%d).", marker_lo)
      data = self.fd.read(int_bytes)
      return RawValue(data)

    if int_bytes == 8 and self.version == "00":
      # 8-byte integers in version 00 are always signed
      self._LogUltraVerbose("Signed integer")
      int_struct = struct.Struct(">q")
    elif int_bytes == 16:
      if self.version == "00":
        # 16-bytes signed integer
        self._LogUltraVerbose("Signed integer")
        int_struct = struct.Struct(">qq")
      else:
        # 16-bytes unsigned integer? That's what the documentation seems to hint
        # Sadly, I haven't been able to reproduce this yet as neither plutil nor
        # XCode allow me to give integers bigger than the maximum representable
        # 8-byte integer.
        int_struct = struct.Struct(">QQ")
      data = self.fd.read(int_struct.size)
      (high, low) = int_struct.unpack(data)
      self._LogUltraVerbose("High 8byte: %lx", high)
      self._LogUltraVerbose("Low 8byte: %lx", low)
      return (high << 64) | low
    else:
      # All other sizes are unsigned
      int_struct = struct.Struct(">%c" % self.bytesize_to_uchar[int_bytes])
    data = self.fd.read(int_struct.size)
    if len(data) < int_struct.size:
      return RawValue(data)
    self._LogUltraVerbose("Raw integer: %r", data)
    (value,) = int_struct.unpack(data)
    return value

  def _ParseReal(self, marker_lo):
    """Parses a real object.

    Reals are stored as a 4byte float or 8byte double per IEE754's format.
    The on-disk length is given by marker_lo.

    Args:
      marker_lo: The lower nibble of the marker.

    Returns:
      A float or double object representing the object.
    """
    self._LogUltraVerbose("Real size %d", marker_lo)
    # SANITY CHECK: Real size must be 4 or 8 bytes on disk
    if marker_lo not in [2, 3]:
      real_length = 1 << marker_lo
      self._LogWarn("Non-standard real number length (%d).", real_length)
      data = self.fd.read(real_length)
      return RawValue(data)

    if marker_lo == 2:
      # Read an IEE754 float
      float_struct = struct.Struct(">f")
    else:
      # Read an IEE754 double precision float
      float_struct = struct.Struct(">d")
    data = self.fd.read(float_struct.size)
    (value,) = float_struct.unpack(data)
    return value

  def _ParseDate(self, marker_lo):
    """Parses a date object.

    Dates are stored as a double precision floating point representing the
    seconds since 2001-01-01T01:00:00Z. Interesting enough, negative dates
    not only are allowed, but used by the system to represent earlier dates.
    Again, the binary format differs from the XML format in that OSX doesn't
    seem to allow for microsecond precision in the XML, while the binary
    format does.
    The following code handles these cases gracefully.

    Args:
      marker_lo: The lower nibble of the marker.

    Returns:
      A datetime object representing the stored date or RawValue if the
      datetime data was corrupt.
    """
    # SANITY CHECK: OSX only writes 8 byte dates. We just warn if the size
    # is wrong, but will read and decode 8 bytes anyway hoping only the marker
    # was corrupt.
    if marker_lo != 3:
      self._LogWarn("Non-standard (8) date length (%d).", 1 << marker_lo)
      self.is_corrupt = True
    # Read an IEE754 double precision float
    date_struct = struct.Struct(">d")
    data = self.fd.read(date_struct.size)
    if len(data) < date_struct.size:
      return RawValue(data)
    self._LogUltraVerbose("Raw date: %r.", data)
    (float_date,) = date_struct.unpack(data)
    self._LogUltraVerbose("Date decoded as: %s.", float_date)
    fraction, integer = math.modf(float_date)
    try:
      date_offset = datetime.timedelta(seconds=int(integer),
                                       microseconds=int(fraction*1000000))
    except OverflowError:
      return RawValue(data)
    return self.plist_epoch + date_offset

  def _ParseData(self, marker_lo):
    """Parses a data object.

    Data objects are stored as plain byte dumps. As in python 2.7 there's no
    distiction between bytes and strings, the same function is used.

    Args:
      marker_lo: The lower nibble of the marker.

    Returns:
      A byte string containing the data.
    """
    return self._ParseString(marker_lo)

  def _ParseString(self, marker_lo, char_size=1):
    """Parses a binary object stored like a string/unicode/data object.

    These objects are stored as a bunch of bytes representing the object, the
    length of which is defined by the lower nibble of the marker. If the length
    is 0xF, however, the first data byte marks the power of 2 bytes used to
    store the length of the string.

    So the following object is a string of more than 0xE bytes (\x5F), the
    length of which is contained in 2^0 (\x00) byte, which is 15 (\x0F).

      "\x5F\x00\x0FThis is a string"

    Args:
      marker_lo: The lower nibble of the marker.
      char_size: The amount of bytes to read per each declared length unit.

    Returns:
      A byte string with the data contained in the object.
    """
    strlen = self._GetSizedIntFromFd(marker_lo)
    self._LogUltraVerbose("String of size %d", strlen)
    return self.fd.read(strlen*char_size)

  def _ReadStructFromFd(self, file_obj, structure):
    """Reads the given structure from file_obj and returns the unpacked data.

    Raises:
      IOError: When there wasn't enough data in file_obj to accommodate the
      requested structure.

    Args:
      file_obj: A file_like object.
      structure: An instance of struct.Struct to read from file_obj.

    Returns:
      The unpacked structure elements.
    """
    data = file_obj.read(structure.size)
    if len(data) < structure.size:
      raise IOError
    return structure.unpack(data)

  def _GetSizedIntFromFd(self, marker_lo):
    """Reads a sized integer from self.fd.

    Apple tries to use the minimum amount of storage to serialize its data
    types. To this end, several object types specify their length through sized
    integers. Objects of variable size store its size in the lowest nibble of
    their marker (this is expected to be passed as marker_lo). When the length
    of an object exceeds 14 (0xE), the lowest nibble of the marker is set to
    0xF. Then, the next byte indicates how many bytes the length of the object
    occupies. This length bytes must be read and interpreted as an integer to
    decode how many elements long the object is.

    Example: A dictionary with 20 elements is hex encoded like this:

    DF 01 14 [...]

    0xDF is the marker and it means it's a dictionary (0xD0) with more than 14
    elements (0x0F). That the number of elements can be expressed as a single
    byte (0x01). And that the number of elements is 20 (0x14).

    Args:
      marker_lo: The lower nibble of the marker.

    Returns:
      The integer value of the sized integer at self.fd.
    """

    if marker_lo == 0xF:
      self._LogUltraVerbose("marker_lo is 0xF, fetching real size")
      # First comes the byte count
      size_len_struct = struct.Struct(">B")
      (size,) = self._ReadStructFromFd(self.fd, size_len_struct)
      size_byte_count = 1 << (size & 0xF)
      try:
        struct_char = self.bytesize_to_uchar[size_byte_count]
      except KeyError:
        # TODO(nop): Improve this, this is awful
        # CORRUPTION
        # If the value is not there, we'll default to 2
        self._LogWarn("unknown size found %d, defaulting to 2", size_byte_count)
        struct_char = self.bytesize_to_uchar.get(2)
        self.is_corrupt = True
      strlen_struct = struct.Struct(">%c" % struct_char)
      (strlen,) = self._ReadStructFromFd(self.fd, strlen_struct)
      return strlen
    self._LogUltraVerbose("Found size %s", marker_lo)
    return marker_lo

  def _ParseUtf16(self, marker_lo):
    """Parses a Unicode object.

    Unicode objects are stored with the same format as strings, only that the
    specified string length doesn't match the stored length, which has to be
    multiplied by 2 due to how characters are encoded.

    Args:
      marker_lo: The lower nibble of the marker.

    Returns:
      A unicode string that contains the unicode object data or RawValue
      if the data was not a valid UTF_16 string. Note that the RawValue
      returned will not have a unicode string but raw bytes.
    """
    utf16 = self._ParseString(marker_lo, char_size=2)
    self._LogUltraVerbose("RAW UTF16 = %s...", utf16[:min(len(utf16), 10)])
    try:
      return utf16.decode("utf-16-be")
    except UnicodeDecodeError:
      self._LogWarn("Invalid UTF-16 data")
      return RawValue(utf16)

  def _ParseUid(self, marker_lo):
    """Parses a UID object.

    UID objects are a rare breed. They do not seem to have an XML
    representation and only appear on Keyed archives. OSX only seems to
    write them as 1, 2, 4 or 8 bytes long. However, they are defined as
    32 bits long on OSX, so they'll hardly be written as 64 bits :/

    The low part of the marker is the UID length - 1.

    Args:
      marker_lo: The lower nibble of the marker.

    Returns:
      An integer representing the UID.

    See:
      http://developer.apple.com/library/mac/#documentation/
      cocoa/Reference/Foundation/Classes/NSKeyedArchiver_Class/Reference/
      Reference.html#//apple_ref/occ/cl/NSKeyedArchiver
    """
    # SANITY CHECK: Size
    uid_size = marker_lo + 1
    if uid_size not in [1, 2, 4, 8]:
      self._LogWarn("Uncommon UID size %d (expected 1, 2, 4 or 8)", uid_size)
    self._LogDiscovery("FOUND A UID!")
    return self._ReadArbitraryLengthInteger(uid_size)

  def _ParseArray(self, marker_lo):
    """Parses an array object.

    Arrays are stored on disk as list of references. This function obtains the
    references and resolves the objects inside the array, thus presenting a
    fully resolved array. Corrupt references are replaced by CorruptReference
    objects.

    Note that calling this function directly might not protect you against
    circular references. Call _ParseObject instead.

    Args:
      marker_lo: The lower nibble of the marker, indicating the number of
      references in the array

    Returns:
      A list of objects.
    """
    array = []
    arraylen = self._GetSizedIntFromFd(marker_lo)
    references = self._GetObjectReferences(arraylen)
    self._LogUltraVerbose(references)
    for reference in references:
      # We need to avoid circular references...
      if reference is CorruptReference:
        array.append(CorruptReference)
        continue
      elif reference in self.objects_traversed:
        self._LogWarn("Circular reference detected at array object.")
        self.is_corrupt = True
        array.append(CorruptReference)
        continue
      elif reference >= self.object_count:
        self._LogWarn("Reference %d out of bounds, skipping...", reference)
        self.is_corrupt = True
        array.append(CorruptReference)
        continue
      array.append(self._ParseObjectByIndex(reference, self.object_offsets))
    self._LogUltraVerbose(array)
    return array

  def _GetObjectReferences(self, length):
    """Obtains a list of references from the file descriptor fd.

    Objects that use object references are dicts, arrays and sets.
    An object reference is the index of the object in the offset table.

    Args:
      length: The amount of object references.

    Returns:
      A list of references.
    """
    references = []
    self._LogUltraVerbose("object_ref_size is %d", self.object_ref_size)
    struct_char = self.bytesize_to_uchar[self.object_ref_size]
    objref_struct = struct.Struct(">%c" % struct_char)
    for _ in range(length):
      try:
        (ref,) = self._ReadStructFromFd(self.fd, objref_struct)
      except IOError:
        ref = CorruptReference
      references.append(ref)
    return references

  def _ParseSet(self, marker_lo):
    """Parses a set object.

    Sets are unordered arrays. They look exactly the same on disk as arrays.

    Args:
      marker_lo: The lower nibble of the marker.

    Returns:
      A list representing the stored set object at self.fd.
    """
    self._LogDiscovery("FOUND A SET!!!")
    return self._ParseArray(marker_lo)

  def _ParseDict(self, marker_lo):
    """Parses a dict object.

    Dictionaries are stored as a list of key-value pairs. These are pairs of
    references. The amount of entries in a dictionary is determined by
    marker_lo. If marker_lo is 0xf, then a sized int is used instead.

    The list of references contains first all the keys and then all the values.

    Note that calling this function directly might not protect you against
    circular references. Call _ParseObject instead.

    Args:
      marker_lo: The lower nibble of the marker.

    Returns:
      A dictionary representing the stored dictionary object at self.fd.
    """
    the_dict = {}
    dictlen = self._GetSizedIntFromFd(marker_lo)
    self._LogDebug("Fetching key references.")
    keys = self._GetObjectReferences(dictlen)
    self._LogDebug("Fetching value references.")
    values = self._GetObjectReferences(dictlen)
    self._LogUltraVerbose(zip(keys, values))
    for k_ref, v_ref in zip(keys, values):
      if k_ref in self.objects_traversed or k_ref >= self.object_count:
        # Circular reference at the key or key pointing to a nonexisting object
        self._LogWarn("Circular reference key or invalid object key.")
        key = "corrupt:%d" % k_ref
        self.is_corrupt = True
      else:
        key = self._ParseObjectByIndex(k_ref, self.object_offsets)
      if v_ref in self.objects_traversed or v_ref >= self.object_count:
        # Circular reference at value or value pointing to a nonexisting object
        self._LogWarn("Circular reference value or invalid object value.")
        value = CorruptReference
        self.is_corrupt = True
      else:
        value = self._ParseObjectByIndex(v_ref, self.object_offsets)
      try:
        the_dict[key] = value
      except TypeError:
        # key is not hashable, so we adjust...
        self._LogDebug("Key %s not hashable... marking as corrupt.", k_ref)
        the_dict["corrupt:%d" % k_ref] = value
        self.is_corrupt = True
    return the_dict

  def _LogDiscovery(self, msg, *args, **kwargs):
    """Informs the user that something that requires research was found."""

    if self.discovery_mode:
      self._LogInfo("DISCOVERY FOUND: %s\nPlease inform %s.",
                   msg, __feedback_email__, *args, **kwargs)

  def _Log(self, level=logging.INFO, *args, **kwargs):
    if level == LOG_ULTRA_VERBOSE and self.ultra_verbosity:
      self._LogDebug(*args, **kwargs)
    logging.log(level, *args, **kwargs)

  def _LogInfo(self, *args, **kwargs):
    self._Log(logging.INFO, *args, **kwargs)

  def _LogError(self, *args, **kwargs):
    self._Log(logging.ERROR, *args, **kwargs)

  def _LogWarn(self, *args, **kwargs):
    self._Log(logging.WARN, *args, **kwargs)

  def _LogDebug(self, *args, **kwargs):
    self._Log(logging.DEBUG, *args, **kwargs)

  def _LogUltraVerbose(self, *args, **kwargs):
    self._Log(LOG_ULTRA_VERBOSE, *args, **kwargs)


# Named readPlist so that binplist resembles the plistlib standard python module
def readPlist(pathOrFile):
  """Returns the top level object of the plist at pathOrFile.

  Args:
    pathOrFile: A path or a file-like object to the plist.

  Returns:
    The top level object of the plist.

  Raises:
    FormatError: When the given file is not a binary plist or its version
    is unknown.
  """
  try:
    # See if it's a file-like object.
    bplist_start_offset = pathOrFile.tell()
    file_obj = pathOrFile
  except AttributeError:
    # Must be a path then
    file_obj = open(pathOrFile, "rb")
    bplist_start_offset = file_obj.tell()

  magicversion = file_obj.read(8)
  if magicversion.startswith("bplist15"):
    logging.info("Binary plist version 1.5 found. Please, inform %s.",
                 __feedback_email__)
    raise FormatError("Binary plist version 1.5 found. Not supported yet.")

  try:
    file_obj.seek(bplist_start_offset)
    bplist = BinaryPlist(file_obj)
    return bplist.Parse()
  except FormatError:
    try:
      file_obj.seek(bplist_start_offset)
      return plistlib.readPlist(file_obj)
    except xml.parsers.expat.ExpatError:
      raise FormatError("Invalid plist file.")


def ToDebugString(string):
  try:
    return str(string)
  except UnicodeEncodeError:
    return unicode(string).encode('unicode_escape')



def PlistToUnicode(o, string_encoding='safeascii', encoding_options="strict",
                   indent=4, previous_indent=0):
  """Returns the Unicode representation of a plist object.

  This is mostly just to handle displaying unicode keys or values in
  dictionaries as the default dict implementation escapes them, and to try to
  represent byte strings in a more human-readable form.

  Not very proud of the implementation but it is what it is.
  """
  if isinstance(o, dict):
    indentation = u' '*(previous_indent+indent)
    indentation_join = u',\n%s' % indentation
    opening_bracket = u"{\n%s" % indentation
    closing_bracket = u"\n%s}" % (u' '*previous_indent)
    pieces = []
    for k, v in o.iteritems():
      key = PlistToUnicode(k, string_encoding=string_encoding,
                      encoding_options=encoding_options, indent=indent,
                      previous_indent=previous_indent+indent)
      value = PlistToUnicode(v, string_encoding=string_encoding,
                        encoding_options=encoding_options, indent=indent,
                        previous_indent=previous_indent+indent)
      pieces.append(u"%s: %s" % (key, value))
    if not pieces:
      return '{}'
    return ''.join([opening_bracket,
                    indentation_join.join(pieces),
                    closing_bracket])
  elif isinstance(o, str):
    try:
      if string_encoding == "safeascii":
        safeascii = []
        for c in o:
          if c in string.printable:
            safeascii.append(c)
          else:
            safeascii.append("\\x" + c.encode("hex"))
        return u"'%s'" % (''.join(safeascii)).decode("ascii", "strict")
      return u"'%s'" % o.decode(string_encoding, encoding_options)
    except (UnicodeEncodeError, UnicodeDecodeError):
      return u"'%s'" % ''.join([u"\\x%s" % c.encode('hex') for c in o])
  elif isinstance(o, unicode):
    # Return a quote-enclosed string
    return u"'%s'" % o
  elif o is NullValue:
    return u"NULL"
  elif o is CorruptReference:
    return u"##CORRUPT_REFERENCE##"
  elif o is UnknownObject:
    return u"##UNKNOWN_OBJECT##"
  else:
    try:
      return u'[%s]' % u', '.join([PlistToUnicode(piece,
                                                  string_encoding,
                                                  encoding_options,
                                                  indent,
                                                  previous_indent)
                                   for piece in o])
    except TypeError:
      return unicode(o)
