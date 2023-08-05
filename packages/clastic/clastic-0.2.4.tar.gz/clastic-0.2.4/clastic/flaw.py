from __future__ import unicode_literals

import os
import re
from core import Application
from render import AshesRenderFactory


def create_app(traceback_string, monitored_files=None):
    non_site_files = _filter_site_files(monitored_files)
    try:
        parsed_tb = _ParsedTB.from_string(traceback_string)
        parsed_error = parsed_tb.to_dict()
    except:
        parsed_error = {}
    resources = {'tb_str': traceback_string,
                 'parsed_error': parsed_error,
                 'all_mon_files': monitored_files,
                 'mon_files': non_site_files}
    render_fact = AshesRenderFactory()
    render_fact.register_source('flaw_tmpl', _FLAW_TEMPLATE)
    routes = [('/', get_flaw_info, 'flaw_tmpl'),
              ('/<path:_ignored>', get_flaw_info, 'flaw_tmpl')]

    app = Application(routes, resources, render_fact)
    return app


def get_flaw_info(tb_str, parsed_error, mon_files):
    try:
        last_line = tb_str.splitlines()[-1]
    except:
        last_line = 'Unknown error'
    return {'mon_files': mon_files,
            'parsed_err': parsed_error,
            'last_line': last_line,
            'tb_str': tb_str}


_FLAW_TEMPLATE = """\
<html>
  <head>
    <title>Oh, Flaw'd: {exc_type} in {err.source_file}</title>
  </head>
  <body>
    <h1>Whopps!</h1>

    <p>Clastic detected a modification, but couldn't restart your application. This is often the result of a module-level error that prevents one of your application's modules from being imported. Fix the error and try refreshing the page.</p>

    {#parsed_err}
      <h2 class="parsed-error-h2">{exc_type}: {exc_msg}</h2>
    {:else}
      <h2 class="unparsed-error-h2">{last_line}</h2>
    {/parsed_err}
    <h3>Stack trace</h3>
    <pre>{tb_str}</pre>
    <br><hr>
    <p>Monitoring:<ul>{#mon_files}<li>{.}</li>{/mon_files}</ul></p>
  </body>
</html>
"""

_frame_re = re.compile(r'^File "(?P<filepath>.+)", line (?P<lineno>\d+)'
                       r', in (?P<funcname>.+)$')
_se_frame_re = re.compile(r'^File "(?P<filepath>.+)", line (?P<lineno>\d+)')


class _ParsedTB(object):
    def __init__(self, exc_type_name, exc_msg, frames=None):
        self.exc_type = exc_type_name
        self.exc_msg = exc_msg
        self.frames = list(frames or [])

    @property
    def source_file(self):
        try:
            return self.frames[-1]['filepath']
        except IndexError:
            return None

    def to_dict(self):
        return {'exc_type': self.exc_type,
                'exc_msg': self.exc_msg,
                'frames': self.frames}

    @classmethod
    def from_string(cls, tb_str):
        if not isinstance(tb_str, unicode):
            tb_str = tb_str.decode('utf-8')
        tb_lines = tb_str.lstrip().splitlines()
        if tb_lines[0].strip() == 'Traceback (most recent call last):':
            frame_lines = tb_lines[1:-1]
            frame_re = _frame_re
        elif len(tb_lines) > 1 and tb_lines[-2].lstrip().startswith('^'):
            frame_lines = tb_lines[:-2]
            frame_re = _se_frame_re
        else:
            raise ValueError('unrecognized traceback string format')
        while tb_lines:
            cl = tb_lines[-1]
            if cl.startswith('Exception ') and cl.endswith('ignored'):
                # handle some ignored exceptions
                tb_lines.pop()
            else:
                break
        for line in reversed(tb_lines):
            # get the bottom-most line that looks like an actual Exception
            # repr(), (i.e., "Exception: message")
            exc_type, sep, exc_msg = line.partition(':')
            if sep and exc_type and len(exc_type.split()) == 1:
                break

        frames = []
        for pair_idx in range(0, len(frame_lines), 2):
            frame_line = frame_lines[pair_idx].strip()
            frame_match = frame_re.match(frame_line)
            if frame_match:
                frame_dict = frame_match.groupdict()
            else:
                continue
            frame_dict['source_line'] = frame_lines[pair_idx + 1].strip()
            frames.append(frame_dict)

        return cls(exc_type, exc_msg, frames)


def _filter_site_files(paths):
    if not paths:
        return []
    site_dir = os.path.dirname(os.__file__)
    return [fn for fn in paths if not fn.startswith(site_dir)]


if __name__ == '__main__':
    _example_tb = """
Traceback (most recent call last):
  File "example.py", line 2, in <module>
    plarp
NameError: name 'plarp' is not defined
"""
    create_app(_example_tb, [__file__]).serve()
