# -*- coding: utf-8 -*-

# Copyright 2023-2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Run Python functions"""

from .common import PostProcessor
from .. import util, formatter


class PythonPP(PostProcessor):

    def __init__(self, job, options):
        PostProcessor.__init__(self, job)

        mode = options.get("mode")
        if mode == "eval" or not mode and options.get("expression"):
            self.function = util.compile_expression(options["expression"])
        else:
            spec = options["function"]
            module_name, _, function_name = spec.rpartition(":")
            module = util.import_file(module_name)
            self.function = getattr(module, function_name)

            args = options.get("args")
            kwargs = options.get("kwargs")
            if args or kwargs:
                self._func = self.function
                self.function = self._call_with_args

                if args:
                    self.args = [formatter.parse(arg).format_map
                                 for arg in args]
                else:
                    self.args = ()

                if kwargs:
                    if isinstance(kwargs, dict):
                        kwargs = kwargs.items()
                    self.kwargs = [(name, formatter.parse(arg).format_map)
                                   for name, arg in kwargs]
                else:
                    self.kwargs = ()

        if archive := self._archive_init(job, options):
            self.run = self.run_archive

        events = options.get("event")
        if events is None:
            events = ("file",)
        elif isinstance(events, str):
            events = events.split(",")
        job.register_hooks({event: self.run for event in events}, options)

        if archive:
            self._archive_register(job)

    def run(self, pathfmt):
        self.function(pathfmt.kwdict)

    def run_archive(self, pathfmt):
        kwdict = pathfmt.kwdict
        if self.archive.check(kwdict):
            return
        self.function(kwdict)
        self.archive.add(kwdict)

    def _call_with_args(self, kwdict):
        return self._func(
            kwdict,
            *[arg(kwdict) for arg in self.args],
            **{name: arg(kwdict) for name, arg in self.kwargs})


__postprocessor__ = PythonPP
