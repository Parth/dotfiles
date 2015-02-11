# Copyright 2014 Google Inc. All Rights Reserved.
"""Facilities for printing Python objects."""
import collections
import cStringIO
import difflib
import json
import os
import sys


from protorpc import messages

from googlecloudapis.apitools.base.py import encoding


_INDENTATION = 2


class ResourcePrinter(object):
  """Base class for printing Python objects."""

  def __init__(self, out=None):
    self._out = out or sys.stdout

  def PrintHeader(self):
    """Prints a header if the output format requires one."""

  def AddRecord(self, record):
    """Adds a record for printing.

    Formats that can be outputted in a streaming manner (e.g., YAML)
    can print their results every time AddRecord() is called. Formats
    that cannot be outputted in a streaming manner (e.g., JSON) should
    not print anything when this method is called and should instead
    print their results when Finish() is called.

    Args:
      record: A record to print. This can be any Python object that can
        be serialized to the format that the subclass requires.
    """

  def Finish(self):
    """Prints the results for formats that cannot stream their output."""

  def PrintSingleRecord(self, record):
    """Print one record by itself.

    Args:
      record: A record to print. This can be any Python object that can
        be serialized to the format that the subclass requires.
    """


class JsonPrinter(ResourcePrinter):
  """Prints all records as a JSON list."""

  def __init__(self, *args, **kwargs):
    """Creates a new JsonPrinter."""
    super(JsonPrinter, self).__init__(*args, **kwargs)
    self._records = []

  def AddRecord(self, record):
    """Adds a JSON-serializable Python object to the list.

    Because JSON output cannot be streamed, this method does not
    actually print anything.

    Args:
      record: A JSON-serializable Python object.
    """
    if isinstance(record, messages.Message):
      record = encoding.MessageToDict(record)
    self._records.append(record)

  def Finish(self):
    """Prints the JSON list to the output stream."""
    self.PrintSingleRecord(self._records)

  def PrintSingleRecord(self, record):
    if isinstance(record, messages.Message):
      record = encoding.MessageToDict(record)
    json.dump(
        record,
        fp=self._out,
        indent=_INDENTATION,
        sort_keys=True,
        separators=(',', ': '))
    self._out.write('\n')


class YamlPrinter(ResourcePrinter):
  """A printer that outputs YAML representations of YAML-serializable objects.

  For example:

    printer = YamlPrinter(sys.stdout)
    printer.AddRecord({'a': ['hello', 'world'], 'b': {'x': 'bye'}})

  produces:

    ---
    a:
      - hello
      - world
    b:
      - x: bye
  """

  def __init__(self, *args, **kwargs):
    super(YamlPrinter, self).__init__(*args, **kwargs)

    # pylint:disable=g-import-not-at-top, Delay import for performance.
    import yaml
    self.yaml = yaml
    self.yaml.add_representer(
        collections.OrderedDict,
        self.yaml.dumper.SafeRepresenter.represent_dict,
        Dumper=self.yaml.dumper.SafeDumper)

    def LiteralPresenter(dumper, data):
      return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    self.yaml.add_representer(
        YamlPrinter._LiteralString, LiteralPresenter,
        Dumper=self.yaml.dumper.SafeDumper)

  class _LiteralString(str):
    """A type used to inform the yaml printer about how it should look."""

  def _UpdateTypesForOutput(self, val):
    """Dig through a dict of list of primitives to help yaml output.

    Args:
      val: dict, list, or primitive, The object with its types being updated.

    Returns:
      An updated version of val.
    """
    if isinstance(val, basestring) and '\n' in val:
      return YamlPrinter._LiteralString(val)
    if isinstance(val, list):
      for i in range(len(val)):
        val[i] = self._UpdateTypesForOutput(val[i])
      return val
    if isinstance(val, dict):
      for key in val:
        val[key] = self._UpdateTypesForOutput(val[key])
      return val
    return val

  def AddRecord(self, record):
    """Immediately prints the given record as YAML.

    A "---" is printed before the actual record to delimit the
    document.

    Args:
      record: A YAML-serializable Python object.
    """
    if isinstance(record, messages.Message):
      record = encoding.MessageToDict(record)

    record = self._UpdateTypesForOutput(record)
    self.yaml.safe_dump(
        record,
        stream=self._out,
        default_flow_style=False,
        indent=_INDENTATION,
        explicit_start=True)

  def PrintSingleRecord(self, record):
    if isinstance(record, messages.Message):
      record = encoding.MessageToDict(record)

    record = self._UpdateTypesForOutput(record)
    self.yaml.safe_dump(
        record,
        stream=self._out,
        default_flow_style=False,
        indent=_INDENTATION,
        explicit_start=False)


def _Flatten(obj):
  """Flattens a JSON-serializable object into a list of tuples.

  The first element of each tuple will be a key and the second element
  will be a simple value.

  For example, _Flatten({'a': ['hello', 'world'], 'b': {'x': 'bye'}})
  will produce:

    [
        ('a[0]', 'hello'),
        ('a[1]', 'world'),
        ('b.x', 'bye'),
    ]

  Args:
    obj: A JSON-serializable object.

  Returns:
    A list of tuples.
  """

  class Index(str):
    pass

  class Key(str):
    pass

  def IntegerLen(integer):
    return len(str(integer))

  def ConstructFlattenedKey(path):
    """[Key('a'), Index('1'), Key('b')] -> 'a[1].b'."""
    buf = cStringIO.StringIO()
    for i in xrange(len(path)):
      if isinstance(path[i], Index):
        buf.write('[')
        buf.write(str(path[i]))
        buf.write(']')
      else:
        if i > 0:
          buf.write('.')
        buf.write(str(path[i]))
    return buf.getvalue()

  def Flatten(obj, path, res):
    if isinstance(obj, list):
      for i in xrange(len(obj)):
        zfilled_idx = str(i).zfill(IntegerLen(len(obj) - 1))
        Flatten(obj[i], path + [Index(zfilled_idx)], res)
    elif isinstance(obj, dict):
      for key, value in obj.iteritems():
        Flatten(value, path + [Key(key)], res)
    else:
      res[ConstructFlattenedKey(path)] = obj

  res = collections.OrderedDict()
  Flatten(obj, [], res)
  return res


class DetailPrinter(ResourcePrinter):
  """A printer that can flatten JSON representations of objects.

  For example:

    printer = DetailPrinter(sys.stdout)
    printer.AddRecord({'a': ['hello', 'world'], 'b': {'x': 'bye'}})

  produces:

    ---
    a[0]: hello
    a[1]: world
    b.x:  bye
  """

  def AddRecord(self, record):
    """Immediately prints the record as a flattened JSON object.

    A "document delimiter" of "---" is inserted before the object.

    Args:
      record: A JSON-serializable object.
    """
    self._out.write('---\n')
    self.PrintSingleRecord(record)

  def PrintSingleRecord(self, record):
    """Print just one record as a flattened JSON object."""
    if isinstance(record, messages.Message):
      record = encoding.MessageToDict(record)
    flattened_record = sorted(_Flatten(record).items())
    max_key_len = max(len(key) for key, _ in flattened_record)

    for key, value in flattened_record:
      self._out.write(key + ':')
      self._out.write(' ' * (max_key_len - len(key)))
      self._out.write(' ')
      self._out.write(str(value))
      self._out.write('\n')


def _Stringify(value):
  """Dumps value to JSON if it's not a string."""
  if not value:
    return ''
  elif isinstance(value, basestring):
    return value
  else:
    return json.dumps(value, sort_keys=True)


class TablePrinter(ResourcePrinter):
  """A printer for printing human-readable tables."""

  def __init__(self, *args, **kwargs):
    """Creates a new TablePrinter."""
    super(TablePrinter, self).__init__(*args, **kwargs)
    self._rows = []

  def AddRow(self, row):
    """Adds a record without outputting anything."""
    self._rows.append(row)

  def Print(self):
    """Prints the actual table."""
    if not self._rows:
      self._out.write(os.linesep)
      return

    rows = [[_Stringify(cell) for cell in row] for row in self._rows]
    col_widths = [0] * len(rows[0])
    for row in rows:
      for i in xrange(len(row)):
        col_widths[i] = max(col_widths[i], len(row[i]))

    for row in rows:
      line = cStringIO.StringIO()
      for i in xrange(len(row) - 1):
        line.write(row[i].ljust(col_widths[i]))
        line.write(' ')
      if row:
        line.write(row[len(row) - 1])
      self._out.write(line.getvalue().strip())
      self._out.write(os.linesep)


_FORMATTERS = {
    'json': JsonPrinter,
    'yaml': YamlPrinter,
    'text': DetailPrinter,
}

SUPPORTED_FORMATS = sorted(_FORMATTERS)


class ResourceDiff(object):
  """For resources whose diffs are to be printed."""

  def __init__(self, original, changed):
    self.original = original
    self.changed = changed

  def PrintDiff(self, formatter_class, out=None):
    """Using the indicated formatter, print the diff of the two resources.

    Prints a unified diff, eg,
    ---

    +++

    @@ -27,6 +27,6 @@

     settings.pricingPlan:                             PER_USE
     settings.replicationType:                         SYNCHRONOUS
     settings.settingsVersion:                         1
    -settings.tier:                                    D1
    +settings.tier:                                    D0
     state:                                            RUNNABLE

    Args:
      formatter_class: type, The class for the formatter that should be used.
      out: .write()able, The output stream to use. If None, use stdout.
    """
    # Full a buffer with the object as rendered originally.
    buff_original = cStringIO.StringIO()
    formatter = formatter_class(out=buff_original)
    formatter.PrintHeader()
    formatter.PrintSingleRecord(self.original)
    # Full a buffer with the object as rendered after the change.
    buff_changed = cStringIO.StringIO()
    formatter = formatter_class(out=buff_changed)
    formatter.PrintHeader()
    formatter.PrintSingleRecord(self.changed)
    # Send these two buffers to the unified_diff() function for printing.
    lines_original = buff_original.getvalue().split('\n')
    lines_changed = buff_changed.getvalue().split('\n')
    lines_diff = difflib.unified_diff(lines_original, lines_changed)
    out = out or sys.stdout
    for line in lines_diff:
      out.write(line + '\n')


def Print(resources, print_format, out=None):
  """Prints the given resources.

  Args:
    resources: A list of JSON-serializable Python dicts.
    print_format: One of json, yaml, or text.
    out: A file-like object for writing results to.

  Raises:
    ValueError: If print_format is invalid.
  """

  formatter_class = _FORMATTERS.get(print_format)
  if not formatter_class:
    raise ValueError('formats must be one of {0}; received {1}'.format(
        ', '.join(SUPPORTED_FORMATS), print_format))

  if isinstance(resources, ResourceDiff):
    resources.PrintDiff(formatter_class, out)

  elif isinstance(resources, collections.Iterator) or type(resources) == list:

    formatter = formatter_class(out=out)
    formatter.PrintHeader()
    # resources may be a generator and since generators can raise
    # exceptions, we have to call Finish() in the finally block to make
    # sure that the resources we've been able to pull out of the
    # generator are printed before control is given to the
    # exception-handling code.
    try:
      for resource in resources:
        formatter.AddRecord(resource)
    finally:
      formatter.Finish()
  else:
    formatter = formatter_class(out=out)
    formatter.PrintHeader()
    formatter.PrintSingleRecord(resources)
