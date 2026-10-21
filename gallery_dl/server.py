# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Background IPC Server"""

import struct
import socket
import threading
import logging
import queue
from . import util, config

log = logging.getLogger("server")

HOST = config.get(("server",), "host", "127.0.0.1")
PORT = config.get(("server",), "port", 64696)
KEY = config.get(("server",), "key", "gallery_dl").encode()
TIMEOUT = config.get(("server",), "timeout")
stop_event = threading.Event()
klen = len(KEY)

if TIMEOUT and TIMEOUT < 0:
    TIMEOUT = None


def listen(queueObj):
    # Background thread in master process
    # that accepts data from subsequent gallery-dl processes
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen()
            s.settimeout(1.0)  # Check stop_event periodically
        except Exception as exc:
            log.error("%s: %s", exc.__class__.__name__, exc)
            queueObj.put(util.SENTINEL)
            return False
        log.info("Listening on %s:%s", HOST, PORT)

        while not stop_event.is_set():
            try:
                conn, _ = s.accept()
                with conn:
                    header = conn.recv(4+klen)
                    if not header[:klen] == KEY:
                        continue
                    data_len = struct.unpack(">I", header[klen:])[0]
                    chunks = []
                    bytes_received = 0
                    while bytes_received < data_len:
                        chunk = conn.recv(min(data_len - bytes_received, 4096))
                        if not chunk:
                            break
                        chunks.append(chunk)
                        bytes_received += len(chunk)
                    full_payload = b"".join(chunks)
                    data = util.json_loads(full_payload.decode())
                    if not data:
                        continue

                    if data.__class__ is list:
                        cnt = len(data)
                        if cnt != 1:
                            urls = "\n  ".join(data)
                            log.info(f"Received {cnt} URLs:\n  {urls}")
                            for url in data:
                                queueObj.put(url)
                        else:
                            data = data[0]
                            log.info("Received URL: " + data)
                            queueObj.put(data)
                    else:
                        log.info("Received URL: " + data)
                        queueObj.put(data)
            except socket.timeout:
                continue
        log.info("Shutting down IPC Server")
        queueObj.put(util.SENTINEL)


def send(data):
    # send data to master process
    cnt = len(data) if data.__class__ is list else 1
    if cnt == 1:
        log.info("Sending URL to Server")
    else:
        log.info("Sending %s URLs to Server", cnt)

    payload = util.json_dumps(data).encode()
    header = struct.pack(">I", len(payload))
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            s.connect((HOST, PORT))
            s.sendall(KEY + header + payload)
            return True
    except Exception as exc:
        log.error("%s: %s", exc.__class__.__name__, exc)
    return False


def start():
    log.info("Starting IPC Server")

    queueObj = InputManager()
    listener = threading.Thread(
        target=listen, args=(queueObj,), daemon=True)
    listener.start()
    return queueObj


def stop():
    stop_event.set()


class InputManager(queue.Queue):

    def __init__(self):
        queue.Queue.__init__(self)
        self.files = self.urls = ()
        self.log = self.err = None

        self._index = 0
        self._pformat = None

    def add_url(self, url):
        self.put(url)

    def add_list(self, urls):
        for url in urls:
            self.put(url)

    def progress(self, pformat=True):
        if pformat is True:
            pformat = "[{current}/{total}] {url}"
        self._pformat = pformat.format_map

    def next(self):
        self._index += 1

    def success(self):
        pass

    error = success

    def close(self):
        self.put(util.SENTINEL)

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        try:
            url = self.get(timeout=TIMEOUT)
        except queue.Empty:
            raise StopIteration
        if url is util.SENTINEL:
            raise StopIteration

        log.info(self._pformat({
            "total"  : self._index + self.qsize() + 1,
            "current": self._index + 1,
            "url"    : url,
        }))
        return url
