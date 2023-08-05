# -*- coding: utf-8 -*-
#
# This file is part of the python-chess library.
# Copyright (C) 2012 Niklas Fiekas <niklas.fiekas@tu-clausthal.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import chess
import struct

# TODO: Also allow writing to opening books and document the class.

class PolyglotOpeningBook(object):
    def __init__(self, path):
        self._entry_struct = struct.Struct(">QHHI")

        self._stream = open(path, "rb")

        self.seek_entry(0, 2)
        self._entry_count = self._stream.tell() / 16

        self.seek_entry(0)

    def __len__(self):
        return self._entry_count

    def __getitem__(self, key):
        if key >= self._entry_count:
            raise IndexError()
        self.seek_entry(key)
        return self.next()

    def __iter__(self):
        self.seek_entry(0)
        return self

    def __reversed__(self):
        for i in xrange(len(self) - 1, -1, -1):
            self.seek_entry(i)
            yield self.next()

    def seek_entry(self, offset, whence=0):
        self._stream.seek(offset * 16, whence)

    def seek_position(self, position):
        # Calculate the position hash.
        key = hash(position)

        # Do a binary search.
        start = 0
        end = len(self)
        while end >= start:
            middle = (start + end) / 2

            self.seek_entry(middle)
            raw_entry = self.next_raw()

            if raw_entry[0] < key:
                start = middle + 1
            elif raw_entry[0] > key:
                end = middle - 1
            else:
                # Position found. Move back to the first occurence.
                self.seek_entry(-1, 1)
                while raw_entry[0] == key and middle > start:
                    middle -= 1
                    self.seek_entry(middle)
                    raw_entry = self.next_raw()

                    if middle == start and raw_entry[0] == key:
                        self.seek_entry(-1, 1)
                return

        raise KeyError()

    def next_raw(self):
        try:
            return self._entry_struct.unpack(self._stream.read(16))
        except struct.error:
            raise StopIteration()

    def next(self):
        raw_entry = self.next_raw()

        source_x = ((raw_entry[1] >> 6) & 077) & 0x7
        source_y = (((raw_entry[1] >> 6) & 077) >> 3) & 0x7

        target_x = (raw_entry[1] & 077) & 0x7
        target_y = ((raw_entry[1] & 077) >> 3) & 0x7

        promote = (raw_entry[1] >> 12) & 0x7

        if promote:
            move = chess.Move(
                chess.Square.from_rank_and_file(source_y, source_x),
                chess.Square.from_rank_and_file(target_y, target_x),
                "nbrq"[promote - 1])
        else:
            move = chess.Move(
                chess.Square.from_rank_and_file(source_y, source_x),
                chess.Square.from_rank_and_file(target_y, source_x))

        # Replace the non standard castling moves.
        if move.uci == "e1h1":
            move = chess.Move.from_uci("e1g1")
        elif move.uci == "e1a1":
            move = chess.Move.from_uci("e1c1")
        elif move.uci == "e8h8":
            move = chess.Move.from_uci("e8g8")
        elif move.uci == "e8a8":
            move = chess.Move.from_uci("e8c8")

        return {
            "position_hash": raw_entry[0],
            "move": move,
            "weight": raw_entry[2],
            "learn": raw_entry[3]
        }

    def get_entries_for_position(self, position):
        position_hash = hash(position)

        # Seek the position. Stop iteration if no entry exists.
        try:
            self.seek_position(position)
        except KeyError:
            raise StopIteration()

        # Iterate.
        while True:
            entry = self.next()
            if entry["position_hash"] == position_hash:
                yield entry
            else:
                break
