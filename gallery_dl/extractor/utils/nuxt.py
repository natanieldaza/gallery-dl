# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

# Adapted from yt-dlp's 'devalue' implementation.
# https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/utils/jslib/devalue.py

from ... import util, dt
import array
import logging
import math


ARRAY_TYPES = {
    "Int8Array"        : "b",
    "Uint8Array"       : "B",
    "Uint8ClampedArray": "B",
    "Int16Array"       : "h",
    "Uint16Array"      : "H",
    "Int32Array"       : "i",
    "Uint32Array"      : "I",
    "Float32Array"     : "f",
    "Float64Array"     : "d",
    "BigInt64Array"    : "l",
    "BigUint64Array"   : "L",
    "ArrayBuffer"      : "B",
}

REVIVERS = {
    "EmptyShallowRef": util.json_loads,
    "EmptyRef"       : util.json_loads,
    "NuxtError"      : util.identity,
    "ShallowRef"     : util.identity,
    "ShallowReactive": util.identity,
    "Ref"            : util.identity,
    "Reactive"       : util.identity,
    "skipHydrate"    : util.identity,
}


def resolve(data):

    resolved = {
        -1: None,
        -2: None,
        -3: math.nan,
        -4: math.inf,
        -5: -math.inf,
        -6: -0.0,
    }

    retval = [None]
    stack = [(retval, 0, 0)]

    while stack:
        target, index, source = stack.pop()

        if source.__class__ is tuple:
            name, source, reviver = source
            try:
                target[index] = reviver(target[index])
            except Exception as exc:
                error(TypeError(f"failed to parse {source} as {name!r}: "
                                f"{exc.__class__.__name__}: {exc}"))
                target[index] = None
            continue
        if source in resolved:
            target[index] = resolved[source]
            continue
        if source < 0:
            error(IndexError(f"invalid index: {source!r}"))
            continue

        try:
            value = data[source]
        except Exception as exc:
            error(exc)
            continue

        if value.__class__ is list:
            if value and value[0].__class__ is str:
                type = value[0]

                if type in REVIVERS:
                    value = value[1]
                    if value == source:
                        # avoid infinite loop
                        error(IndexError(f"{type!r} cannot point to itself "
                                         f"(index: {source})"))
                        continue
                    stack.append((target, index, (
                        type, value, REVIVERS[type])))
                    stack.append((target, index, value))
                    continue

                elif type in ARRAY_TYPES:
                    data = util.b64rdecode(value[1])
                    result = array.array(ARRAY_TYPES[type], data).tolist()

                elif type == "Date":
                    try:
                        result = dt.parse_iso(value[1])
                    except Exception:
                        error(ValueError(f"invalid date: {value[1]!r}"))
                        result = None

                elif type == "Set":
                    result = [None] * (len(value) - 1)
                    for offset, new in enumerate(value[1:]):
                        stack.append((result, offset, new))

                elif type == "Map":
                    result = []
                    for i in range(1, len(value), 2):
                        pair = [None, None]
                        stack.append((pair, 0, value[i]))
                        stack.append((pair, 1, value[i+1]))
                        result.append(pair)

                elif type == "RegExp":
                    result = util.re(value[1])

                elif type == "Object":
                    result = value[1]

                elif type == "BigInt":
                    result = int(value[1])

                elif type == "null":
                    result = {}
                    for i in range(1, len(value), 2):
                        stack.append((result, value[i], value[i+1]))

                else:
                    error(TypeError(f"invalid type at {source}: {type!r}"))
                    result = None
            else:
                result = [None] * len(value)
                for offset, new in enumerate(value):
                    stack.append((result, offset, new))

        elif value.__class__ is dict:
            result = {}
            for key, new in value.items():
                stack.append((result, key, new))

        else:
            result = value

        target[index] = resolved[source] = result

    return retval[0]


def error(exc):
    logging.getLogger("nuxt").error("%s: %s", exc.__class__.__name__, exc)
