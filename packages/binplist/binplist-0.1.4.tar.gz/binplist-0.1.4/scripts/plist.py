#!/bin/env python
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

import argparse
import logging
import plistlib
import sys

from binplist import binplist


parser = argparse.ArgumentParser(description="A forensic plist parser.")
parser.add_argument(
  "plist", default=None, action="store",
  help="plist file to be parsed")
parser.add_argument(
  "-V", "--version", action="version", version=binplist.__version__)
parser.add_argument("-v", "--verbose", action="append_const", const=True,
                    help="Turn verbose logging on. Use twice for ultra "
                         "verbosity.")
parser.add_argument("-e", "--string-encoding", default="safeascii",
                    help="Encoding of binplist strings.")
parser.add_argument("-eo", "--string-encoding-option", default="strict",
                    choices=['strict', 'ignore', 'replace'],
                    help=("What to do when encoding strings of a binary plist "
                          "and some characters cannot be converted."))
parser.add_argument("-E", "--output-encoding", default="utf-8",
                    help="Output encoding of binplist.")
parser.add_argument("-EO", "--output-encoding-option", default="strict",
                    choices=['strict', 'ignore', 'replace',
                             'xmlcharrefreplace', 'backslashreplace'],
                    help=("What to do when encoding the output of binplist "
                          "and some characters cannot be converted."))
parser.add_argument("-d", "--discovery-mode", action="store_true",
                    help=("Will inform you when a UID or a SET is found so "
                          "that you can help me improve the parser."))


if __name__ == "__main__":
  options = parser.parse_args()
  if not options.plist:
    parser.print_help()
    sys.exit(-1)

  ultra_verbosity = False
  if options.verbose:
    if len(options.verbose) == 1:
      logging.basicConfig(level=logging.DEBUG)
    else:
      ultra_verbosity = True
      logging.basicConfig(level=binplist.LOG_ULTRA_VERBOSE)

  with open(options.plist, "rb") as fd:
    plist = binplist.BinaryPlist(file_obj=fd,
                                 ultra_verbosity=ultra_verbosity,
                                 discovery_mode=options.discovery_mode)
    try:
      parsed_plist = plist.Parse()
      if plist.is_corrupt:
        logging.warn("%s LOOKS CORRUPTED. You might not obtain all data!\n",
                     options.plist)
    except binplist.FormatError, e:
      parsed_plist = plistlib.readPlist(options.plist)

    print binplist.PlistToUnicode(
      parsed_plist,
      string_encoding=options.string_encoding,
      encoding_options=options.string_encoding_option).encode(
        options.output_encoding,
        options.output_encoding_option)
