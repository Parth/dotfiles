"""A module for displaying tabular data to humans.

This is currently a work in progress.

Example:
--------

  from ... import table

  ...

  t = t.Table(padding=1)
  t.SetColumns(['Country', 'Total Population', 'Populous Cities'])
  t.AppendRow(['China', '1,354,040,000',
              ['Shanghai', 'Beijing', 'Tianjin', 'Guangzhou']])
  t.AppendRow(['India', '1,210,569,573',
              ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad']])
  t.Write()

The snippet above will print the following table to stdout:

  +---------+------------------+-----------------+
  | Country | Total Population | Populous Cities |
  +---------+------------------+-----------------+
  | China   | 1,354,040,000    | Shanghai        |
  |         |                  | Beijing         |
  |         |                  | Tianjin         |
  |         |                  | Guangzhou       |
  +---------+------------------+-----------------+
  | India   | 1,210,569,573    | Mumbai          |
  |         |                  | Delhi           |
  |         |                  | Bangalore       |
  |         |                  | Hyderabad       |
  +---------+------------------+-----------------+

It's also possible to get a detailed format by using the DetailedTable
class:

  +------------+---------------+
  | Country    | China         |
  | Population | 1,354,040,000 |
  | Cities     | Shanghai      |
  |            | Beijing       |
  |            | Tianjin       |
  |            | Guangzhou     |
  +------------+---------------+
  | Country    | India         |
  | Population | 1,210,569,573 |
  | Cities     | Mumbai        |
  |            | Delhi         |
  |            | Bangalore     |
  |            | Hyderabad     |
  +------------+---------------+
"""

import csv
import itertools
import numbers
import os
import re
import StringIO
import subprocess
import sys
import textwrap



__all__ = [
    'Alignment',
    'Format',
    'Column',
    'Table',
    'DetailedTable',
    'Csv',
    'CreateTable',
]

# The absolute minimum width that will be allocated to cells.
_MIN_CELL_WIDTH = 5

# Control characters that need to be escaped before they are printed.
_CONTROL_CHARS = set(unichr(c) for c in range(32) + [127])


def _GetTerminalWidth():
  """Returns the terminal width or None if width cannot be determined."""
  if sys.platform == 'win32':
    try:
      # Redirect stderr to stdout which is ignored anyway if cmd or mode fail.
      output = subprocess.check_output(['cmd', '/R', 'mode', 'con:'],
                                       stderr=subprocess.STDOUT)
      # The second integer value is the console window width. Literal strings
      # are avoided in the parse in case they are localized.
      width = int(re.sub(r'\D+\d+\D+(\d+).*', r'\1', output,
                         count=1, flags=re.DOTALL))
      return width
    except BaseException:
      pass
  else:
    try:
      # Redirect stderr to stdout which is ignored anyway if stty fails.
      output = subprocess.check_output(['stty', 'size'],
                                       stderr=subprocess.STDOUT)
      width = int(output.split()[1])
      return width
    except BaseException:
      pass

    # ``stty size'' is non-standard -- try ``stty -a'' and hope its not
    # localized.
    try:
      # Redirect stderr to stdout which is ignored anyway if stty fails.
      output = subprocess.check_output(['stty', '-a'], stderr=subprocess.STDOUT)
      width = int(re.sub(r'.*columns *(\d+).*', r'\1', output,
                         count=1, flags=re.DOTALL))
      return width
    except BaseException:
      pass

  # Native commands failed, default to COLUMNS.
  return os.environ.get('COLUMNS', None)


class Alignment(object):
  """Alignment policies for columns.

  LEFT, CENTER, and RIGHT are self-explanatory. AUTO will
  right-align numerical values and left-align everything else.

  Alignment does not have an effect on the CSV format.
  """

  POLICIES = ['left', 'center', 'right', 'auto']
  LEFT, CENTER, RIGHT, AUTO = POLICIES


class Format(object):
  """Defines the available table formats."""

  TABLE, DETAILED, CSV = ['table', 'detailed', 'csv']


class Column(object):
  """A class for representing a table column."""

  def __init__(self, name, priority=0, alignment=Alignment.AUTO):
    """Returns a new column descriptor.

    Args:
      name: The name of the column.
      priority: A numerical value that defines this column's
        priority. A higher number means a higher priority.
        Priorities are relative. When there is a terminal column
        length constraint that cannot be met by reducing column
        widths, columns with lower priorities are dropped.
        Priorities are ignored for the CSV format.
      alignment: The alignment policy. See Alignment for more
        details.
    """
    self.__name = name
    self.__priority = priority
    self.__alignment = alignment

  @property
  def name(self):
    return self.__name

  @property
  def priority(self):
    return self.__priority

  @property
  def alignment(self):
    return self.__alignment

  def __eq__(self, other):
    return (self.name == other.name and
            self.priority == other.priority and
            self.alignment == other.alignment)

  def __ne__(self, other):
    return not self.__eq__(other)

  def __lt__(self, other):
    return self.priority < other.priority

  def __le__(self, other):
    return self.priority <= other.priority

  def __gt__(self, other):
    return self.priority > other.priority

  def __ge__(self, other):
    return self.priority >= other.priority

  def __repr__(self):
    args = ', '.join(
        arg + '=' + str(repr(getattr(self, arg)))
        for arg in self.__init__.func_code.co_varnames[1:])
    return '{0}({1})'.format(self.__class__.__name__, args)


class _TabularData(object):
  """A base class for holding tabular data.

  This class takes care of holding the tabular data. Subclasses are
  responsible for implementing a Write() method which will display the
  tabular data.
  """

  def __init__(self):
    """Constructs a new _TabularData object."""
    self.__cols = None
    self.__rows = []

  @property
  def columns(self):
    """Returns the normalized columns."""
    if self.__cols is None:
      raise ValueError('SetColumns() must be called before accessing columns.')
    return tuple(self.__cols)

  @property
  def rows(self):
    """Returns an immutable copy of the rows."""
    return tuple(self.__rows)

  def SetColumns(self, cols):
    """Sets the columns. This method must be called exactly once.

    Args:
      cols: A list of columns. Each element can either be a string
        representing the column's name or an instance of Column.
        Strings are promoted to Column.

    Raises:
      ValueError: If the cols preconditions are violated or if SetColumns()
        has already been called.
    """
    def Normalize(col):
      if isinstance(col, basestring):
        return Column(col)
      elif isinstance(col, Column):
        return col

      raise ValueError(
          'Columns must be strings or instances of Column. Received: {0}'
          .format(col))

    if self.__cols is not None:
      raise ValueError('The header has already been set.')

    self.__cols = [Normalize(col) for col in cols]

  def AppendRow(self, row):
    """Appends a single row to the table.

    Args:
      row: A list of row values. Elements other than lists and dicts
        are serialized to strings using the built-in str(). For CSV
        output, lists and dicts are also converted to strings. For
        non-CSV output, each list element is converted into a string
        and printed on its own line inside the cell. Similarly, each
        dict mapping is output as 'key: value' on its own line.

    Raises:
      ValueError: If SetColumns() has not been called or if len(row) >
        the number of columns.
    """
    if self.__cols is None:
      raise ValueError('SetColumns() must be called before appending rows.')

    row = tuple(row)

    if len(row) > len(self.columns):
      raise ValueError(
          'Expected length of row ({0}) to be <= the number of columns ({1})'
          .format(len(row), len(self.columns)))

    # Pads the right side of the row with Nones until the length of
    # the row is equal to the length of the columns. It's useful to do
    # this now because jagged tables are hard to deal with for
    # subclasses.
    row = tuple(itertools.chain(
        row,
        (None for _ in xrange(len(self.columns) - len(row)))))

    # Normalization is left for the subclasses since different
    # subclasses will have different normalization semantics.
    self.__rows.append(row)

  def AppendRows(self, rows):
    """Appends many rows to the table.

    The semantics of how each row is handled is similar to
    AppendRow().

    Args:
      rows: A list of rows.
    """
    for row in rows:
      self.AppendRow(row)

  def Write(self, out=None):
    """Writes the table to out.

    Assumes SetColumns() has been called.

    Args:
      out: Any object with a write() method. The output is
        written to this object. If None, sys.stdout is used.
    """
    raise NotImplementedError('Write() should be implemented by subclasses.')

  @staticmethod
  def _Stringify(value):
    """Formats the given value so it's appropriate for inclusion in a table.

    The given value is coerced to a unicode and all control characters
    are escaped. For example, '\n' is transformed to '\\n'. '\0' is
    transformed to '\\x00'.

    Args:
      value: The value to transform. This can be any type.

    Returns:
      A unicode string transformed according to the rules above.
    """
    return u''.join(
        c.encode('unicode_escape') if c in _CONTROL_CHARS else c
        for c in unicode(value))


class _Cell(object):
  """A single cell for the tabular display formats.

  This class holds the data associated with a cell and provides
  functionality for outputting the cell into the "tabular" table
  formats.

  A cell can span multiple lines due to print width limitations or
  data requirements (list of items or dicts). Most of the logic here
  is for dealing with multi-line cells.
  """

  __STRING_ALIGNMENT_METHODS = {
      Alignment.LEFT: 'ljust',
      Alignment.CENTER: 'center',
      Alignment.RIGHT: 'rjust',
  }

  def __init__(self, data, alignment=None):
    """Constructs a new _Cell.

    Args:
      data: The data that should be displayed in this cell.
      alignment: The alignment rule for this cell.
    """
    self.__original_data = data
    self.__data = data
    self.__alignment = alignment
    self._UpdateDimensions()

  def _UpdateDimensions(self):
    """Computes and sets the height and width for this cell."""
    self.__height = len(self.__data)
    self.__width = max(len(line) for line in self.__data) if self.__data else 0

  @property
  def data(self):
    return tuple(self.__data)

  @property
  def height(self):
    return self.__height

  @property
  def width(self):
    return self.__width

  @property
  def alignment(self):
    return self.__alignment

  @property
  def is_numeric(self):
    return self.__is_numeric

  def EmitLine(self, line, width, out):
    """Writes one line of this cell's data to out.

    Examples:

    >>> import StringIO
    >>> cell = _Cell('hello\nworld')
    >>> out = StringIO.StringIO()
    >>> cell.EmitLine(0, 10, out)
    >>> out.getvalue()
    'hello     '
    >>> out = StringIO.StringIO()
    >>> cell.EmitLine(1, 10, out)
    >>> out.getvalue()
    'world     '
    >>> out = StringIO.StringIO()
    >>> cell.EmitLine(1, 5, out)
    >>> out.getvalue()
    'world'
    >>> out = StringIO.StringIO()
    >>> cell.EmitLine(2, 10, out)
    >>> out.getvalue()
    '          '

    Args:
      line: An index into data. data[line] will be written to out. If
        line >= len(data), data[line] will be assumed to be the empty
        string.
      width: The space allocated to this cell.
      out: An object with a write() method.

    Raises:
      ValueError: If any of the parameters are non-sane values (e.g.,
        negative width).
    """
    if line < 0:
      raise ValueError('line must be non-negative: {0}'.format(line))

    if line < len(self.data):
      value_at_line = self.data[line]
    else:
      value_at_line = ''

    if len(value_at_line) > width:
      raise ValueError(
          'Line {0} of {1} does not fit in width {2}. '
          'Given width must be >= the width of the cell.'
          .format(line, repr(self.data), width))

    out.write(self.Align(value_at_line, width, alignment=self.alignment))

  def Align(self, string, width, alignment=Alignment.LEFT):
    """Returns the given string aligned in the allotted space."""
    if alignment is None:
      alignment = Alignment.LEFT

    alignment_method = self.__STRING_ALIGNMENT_METHODS.get(alignment)
    if not alignment_method:
      raise ValueError(
          'Alignment value must be one of {{{0}}}; Received: {1}.'.format(
              ', '.join(sorted(self.__STRING_ALIGNMENT_METHODS)),
              alignment))

    return getattr(string, alignment_method)(width)

  def AdjustWidth(self, allotted_width):
    """Shrinks the width of this cell.

    Args:
      allotted_width: The new width. All the lines in the cell will
        coerced into having lengths that are <= allotted_width.
    """
    self.__data = []
    for line in self.__original_data:
      if len(line) > allotted_width:
        self.__data += textwrap.wrap(line, allotted_width)
      else:
        self.__data.append(line)
    self._UpdateDimensions()


class _TableBase(_TabularData):
  """Base class for the human-readable table formats."""

  def __init__(self, width=None, padding=1,
               get_terminal_width_fn=_GetTerminalWidth):
    """"Creates a new Table.

    Args:
      width: The maximum width that the table should occupy. If non-positive,
        no width constraint will be exacted. If None and the output is destined
        for a tty device, get_terminal_width_fn will be invoked to figure out
        the terminal's width.
      padding: The amount of whitespace to add before and after
        each cell value.
      get_terminal_width_fn: A function that can return the terminal's width if
        the output is destined for a tty device. This argument is used for
        testing and should not be set by the client.

    Raises:
      ValueError: If padding is negative.
    """
    super(_TableBase, self).__init__()
    self.__width = width
    self.__get_terminal_width_fn = get_terminal_width_fn

    if padding < 0:
      raise ValueError('padding must be non-negative. Received: {0}'
                       .format(padding))
    self.__padding = padding

  def _UpdateWidth(self, out):
    """Updates the allotted table width, if necessary.

    If no explicit width was specified and the output destination is a
    tty device, this method will attempt to discover the width of the
    device and, if successful, will overwrite the width to the
    device's width.

    Args:
      out: A file-like object to which the table is written. If out
        represents a tty device, it is expected that it will have an
        'isatty' method that returns True.
    """
    if self.__width is not None:
      return

    isatty_method = getattr(out, 'isatty', None)
    if isatty_method is None:
      return

    if isatty_method() and self.__get_terminal_width_fn is not None:
      self.__width = self.__get_terminal_width_fn()

  @property
  def has_width_constraint(self):
    return self.__width is not None and self.__width > 0

  @property
  def padding(self):
    return self.__padding

  @staticmethod
  def _MakeWidthMatrix(cell_matrix):
    """Calculates the width for each cell in cell_matrix."""
    width_matrix = []
    for row in cell_matrix:
      for i, cell in enumerate(row):
        if i == len(width_matrix):
          width_matrix.append([cell.width])
        else:
          width_matrix[i].append(cell.width)
    return width_matrix

  def _CalculateColumnWidths(self, cell_matrix, num_columns, percentile=1):
    """Calculates the amount of characters each column can have.

    If a width constraint is specified by the client, this method will
    attempt to find a "fair" allocation of widths for the columns that
    meet the constraint. The calculation is a best-effort one. If the
    constraint cannot be met, all columns will be allocated
    _MIN_CELL_WIDTH.

    If a width constraint is not specified, this method simply returns
    the widths of the maximum cells in each column.

    Args:
      cell_matrix: A list where each element is a list corresponding to a
        single row of data to be printed.
      num_columns: The number of columns for the final table. This could
        be equal to the number of columns for the normal table or 2 for
        the detailed table (since the latter's left column contains all
        the headers and the right column contains all the values).
      percentile: A number in the range [0.0, 1.0] that controls how
        column widths will be allocated. Each column's cell widths are
        sorted and the percentile is used to pick a "representative"
        width for each column. These widths are then used to figure out
        how much space each column should get in the shrunken table.
        If 1.0, the cell with the maximum width is picked for each column
        as the representative. 0.5 will pick the median, 0.0 will pick the
        minimum. It is recommended to use a number in the neighborhood of
        0.5 so a few really long cells do not skew the calculations in
        favor of their column.

    Raises:
      ValueError: If the percentile is not in [0.0, 1.0].

    Returns:
      A list where the element at index i specifies the amount of
      characters the content of column i can have. Content is defined
      as the data in the cell. Content does not include the padding or
      cell separators ('|').
    """
    if percentile < 0 or percentile > 1:
      raise ValueError('percentile must be in range [0.0, 1.0]; received: {0}'
                       .format(percentile))

    width_matrix = self._MakeWidthMatrix(cell_matrix)

    # The maximum content widths for all the columns. Content width
    # does not include space allocated for padding or the cell
    # separators ('|'). This list represents the ideal widths in the
    # absence of width constraints.
    ideal_col_widths = [max(widths) for widths in width_matrix]

    # If no width constraints exist, returns the ideal widths.
    if not self.has_width_constraint:
      return ideal_col_widths

    # TODO(user): Add logic to degrade padding if necessary. (Or
    # maybe even make padding not be configurable and always use 1?)

    # Selects the content widths based on the given percentile. We use
    # percentiles so that a few really long cells do not skew the
    # final width allocations.
    widths = []
    for column_widths in width_matrix:
      column_widths.sort()
      index = int(percentile * (len(column_widths) - 1))
      widths.append(min(column_widths[index], _MIN_CELL_WIDTH))

    total = sum(widths)  # The total content width at the given percentile.
    normalized_widths = [float(width) / total for width in widths]

    # The amount of width available for content.
    width_budget = min(
        self.__width - (num_columns * (2 * self.padding + 1) + 1),
        sum(ideal_col_widths))

    allowances = [max(int(width_budget * allowance), _MIN_CELL_WIDTH)
                  for allowance in normalized_widths]
    allowances = [min(allowance, ideal_width) for allowance, ideal_width
                  in zip(allowances, ideal_col_widths)]

    # Due to errors arising from casting floats to ints, we could end
    # up with unallocated characters. This block "sprinkles" any
    # leftovers to columns that need extra space one character at a
    # time in round-robin style. (We could do something smarter, but
    # the number of leftovers is small compared to the total width, so
    # additional complexity is probably not warranted.)
    unallocated = width_budget - sum(allowances)
    while unallocated > 0:
      for i, allowance in enumerate(allowances):
        if unallocated <= 0:
          break
        wanted = ideal_col_widths[i] - allowance
        if wanted > 0:
          unallocated -= 1
          allowances[i] += 1
    return allowances

  def _EmitSeparator(self, widths, out):
    """Writes the separator between two rows.

    A separator looks like: '+-----+----+----+\n'

    Args:
      widths: A list containing the widths of the columns.
      out: A file-like object with a write() method.
    """
    out.write('+')
    for width in widths:
      out.write('-' * (2 * self.padding + width))
      out.write('+')
    out.write('\n')

  def _EmitPadding(self, out):
    """Writes padding to out."""
    out.write(' ' * self.padding)

  @staticmethod
  def _AdjustCellWidths(cell_matrix, widths):
    """Shrinks all cells in __cell_matrix based on values in widths."""
    for row in cell_matrix:
      for cell, allotted_width in zip(row, widths):
        cell.AdjustWidth(allotted_width)

  @staticmethod
  def _IsAssociativeList(data):
    """Returns True if data is a dict-like object."""
    if isinstance(data, dict):
      return True
    elif isinstance(data, (list, tuple)):
      try:
        dict(data)
        return True
      except BaseException:
        pass
    return False

  @staticmethod
  def _IsNumeric(data):
    """Returns True if data is numeric."""
    try:
      float(data)
      return True
    except BaseException:
      return False

  def _MakeCell(self, data, alignment):
    """Returns a new _Cell for the given data.

    The data is normalized according to some rules that will be
    described later (see next TODO).

    TODO(user): Explain the normalization rules in detail.

    TODO(user): Revisit normalization and ensure that nothing
    "surprising" will happen.

    Args:
      data: The data for the cell.
      alignment: The alignment policy.

    Returns:
      A list containing the normalized data. Each item in the list will
        represent a singline line of the cell.

    Raises:
      ValueError: If the data type is not supported.
    """
    normalized_data = None

    if data is None:
      normalized_data = tuple()

    elif isinstance(data, numbers.Number):
      normalized_data = (self._Stringify(data),)

    elif isinstance(data, basestring):
      normalized_data = tuple(data.splitlines())

    elif self._IsAssociativeList(data):
      # Sorts the dictionary, so we get consistent results across
      # different versions of Python.
      if isinstance(data, dict):
        data = sorted(data.iteritems())

      normalized_data = tuple(
          self._Stringify(key) + ': ' + self._Stringify(value)
          for key, value in data)

    elif isinstance(data, (list, tuple)):
      normalized_data = tuple(self._Stringify(item) for item in data)

    if normalized_data is None:
      # We have failed to identify the value as a supported type.
      raise ValueError(
          'Unexpected data type. Type: {0}; value: {1}; '
          'one of numbers.Number, basestring, list, tuple, dict is required.'
          .format(type(data), data))

    if alignment == Alignment.AUTO:
      alignment = Alignment.RIGHT if self._IsNumeric(data) else Alignment.LEFT

    return _Cell(normalized_data, alignment=alignment)


class Table(_TableBase):
  """A class that can be used for displaying tabular data.

  This class can produce tables like the following:

  +------+-------------+--------------+------------+------+
  | Rank | Country     | Capital City | Population | Year |
  +------+-------------+--------------+------------+------+
  | 1    | Japan       | Tokyo        | 13,189,000 | 2011 |
  +------+-------------+--------------+------------+------+
  | 2    | Russia      | Moscow       | 11,541,000 | 2011 |
  +------+-------------+--------------+------------+------+
  | 3    | South Korea | Seoul        | 10,528,774 | 2011 |
  +------+-------------+--------------+------------+------+
  | 4    | Indonesia   | Jakarta      | 10,187,595 | 2011 |
  +------+-------------+--------------+------------+------+
  | 5    | Iran        | Tehran       | 9,110,347  |      |
  +------+-------------+--------------+------------+------+
  """

  def _MakeCellMatrix(self):
    """Creates a matrix containing the column headers and rows as _Cells.

    The result is placed in the property __cell_matrix.
    """
    self.__cell_matrix = []

    cells = []
    for col in self.columns:
      cells.append(self._MakeCell(col.name, alignment=col.alignment))
    self.__cell_matrix.append(tuple(cells))

    for row in self.rows:
      cells = []
      for cell, col in zip(row, self.columns):
        cell = self._MakeCell(cell, alignment=col.alignment)
        cells.append(cell)
      self.__cell_matrix.append(tuple(cells))

  def Write(self, out=None):
    """Writes the table to out.

    Assumes SetColumns() has been called.

    Args:
      out: Any object with a write() method. The output is
        written to this object. If None, sys.stdout is used.
    """
    out = out or sys.stdout

    self._UpdateWidth(out)
    self._MakeCellMatrix()
    widths = self._CalculateColumnWidths(
        self.__cell_matrix,
        num_columns=len(self.columns),
        percentile=0.5)
    self._AdjustCellWidths(self.__cell_matrix, widths)

    self._EmitSeparator(widths, out)
    for row in self.__cell_matrix:
      row_height = max(cell.height for cell in row)
      for line in xrange(row_height):
        for col, cell in enumerate(row):
          out.write('|')
          self._EmitPadding(out)
          cell.EmitLine(line, widths[col], out)
          self._EmitPadding(out)
        out.write('|\n')
      self._EmitSeparator(widths, out)


class DetailedTable(_TableBase):
  """A class that can be used for displaying tabular data in detailed format.

  This class can produce tables like the following:

  +------------+---------------+
  | Country    | China         |
  | Population | 1,354,040,000 |
  | Cities     | Shanghai      |
  |            | Beijing       |
  |            | Tianjin       |
  |            | Guangzhou     |
  +------------+---------------+
  | Country    | India         |
  | Population | 1,210,569,573 |
  | Cities     | Mumbai        |
  |            | Delhi         |
  |            | Bangalore     |
  |            | Hyderabad     |
  +------------+---------------+
  """

  def _MakeCellsForDetailValue(self, data, alignment):
    """Returns _Cell instances for non-column header data.

    Args:
      data: The data for the _Cell.
      alignment: The alignment policy.

    Returns:
      A list of _Cell instances. For associative data, the list will contain
       (key, value) _Cell tuples. For all other data, the list will contain
       exactly one _Cell.

    Raises:
      ValueError: If the data type is not supported.
    """
    if not self._IsAssociativeList(data):
      return [self._MakeCell(data, alignment=alignment)]

    # Sorts the dictionary, so we get consistent results across
    # different versions of Python.
    if isinstance(data, dict):
      data = sorted(data.iteritems())

    if alignment == Alignment.AUTO:
      alignment = Alignment.LEFT

    return [
        (_Cell(['  ' + self._Stringify(key)], alignment=Alignment.LEFT),
         _Cell([self._Stringify(value)], alignment=alignment))
        for key, value in data]

  def _MakeCellMatrix(self):
    """Creates a matrix of _Cells corresponding to the final table cells.

    The result is placed in the property __cell_matrix.

    __cell_matrix is a list of lists. Each inner list will
    correspond to a single row of data. Inner lists are comprised of
    tuples where the first element is a key (i.e., column header) and
    the second element is the value for that header in the current
    row.
    """
    self.__cell_matrix = []

    for row in self.rows:

      # A section is a single row. We have sections so that Write()
      # can tell where lines separating each "row" should be written.
      section = []

      for key, value in zip(self.columns, row):
        if value is None:
          continue

        key_cell = self._MakeCell(key.name, alignment=Alignment.LEFT)

        if key_cell.alignment == Alignment.AUTO:
          key_alignment = Alignment.LEFT
        else:
          key_alignment = key_cell.alignment

        value_cells = self._MakeCellsForDetailValue(
            value, alignment=key_alignment)

        if self._IsAssociativeList(value_cells):
          section.append((key_cell, _Cell(tuple())))
          for left, right in value_cells:
            section.append((left, right))
        else:
          section.append((key_cell, value_cells[0]))

      self.__cell_matrix.append(tuple(section))

  def Write(self, out=None):
    """Writes the table to out.

    Assumes SetColumns() has been called.

    Args:
      out: Any object with a write() method. The output is
        written to this object. If None, sys.stdout is used.
    """
    out = out or sys.stdout

    self._UpdateWidth(out)
    self._MakeCellMatrix()
    flattened_cell_matrix = tuple(itertools.chain(*self.__cell_matrix))

    widths = self._CalculateColumnWidths(
        flattened_cell_matrix,
        num_columns=2,
        percentile=0.5)
    self._AdjustCellWidths(flattened_cell_matrix, widths)

    self._EmitSeparator(widths, out)
    for section in self.__cell_matrix:
      for key, value in section:
        row_height = max(key.height, value.height)
        for line in xrange(row_height):
          for i, cell in enumerate((key, value)):
            out.write('|')
            self._EmitPadding(out)
            cell.EmitLine(line, widths[i], out)
            self._EmitPadding(out)
          out.write('|\n')
      self._EmitSeparator(widths, out)


class Csv(_TabularData):
  """A class that can be used for displaying data in CSV format.

  It is recommended that cell values only be simple types such as
  strings and numbers. More complicated types like lists are handled
  by outputting their Pythonic representations.
  """

  # TODO(user): Add customizability to how the CSV is outputted.

  @staticmethod
  def _UnicodeEncode(row):
    """utf-8 encodes all values in iterable row."""
    return ['' if cell is None else unicode(cell).encode('utf-8')
            for cell in row]

  def Write(self, out=None):
    """Writes the table to out.

    Assumes SetColumns() has been called.

    Args:
      out: Any object with a write() method. The output is
        written to this object. If None, sys.stdout is used.
    """
    out = out or sys.stdout

    # The csv module does not support Unicode, so we have to manually
    # shepherd Unicode values in and out of the csv module using the
    # StringIO file-like object.
    buf = StringIO.StringIO()
    writer = csv.writer(
        buf, delimiter=',',
        lineterminator='\n', quoting=csv.QUOTE_MINIMAL)

    writer.writerow(self._UnicodeEncode(col.name for col in self.columns))

    for row in self.rows:
      row = self._UnicodeEncode(row)
      writer.writerow(row)

    out.write(buf.getvalue().decode('utf-8'))


def CreateTable(table_format, width=None, padding=1):
  """Returns a table of the given format."""
  if table_format == Format.TABLE:
    return Table(
        width=width, padding=padding, get_terminal_width_fn=_GetTerminalWidth)
  elif table_format == Format.DETAILED:
    return DetailedTable(
        width=width, padding=padding, get_terminal_width_fn=_GetTerminalWidth)
  elif table_format == Format.CSV:
    return Csv()
  else:
    raise ValueError(
        'Table format not recognized: {0}; expected one of {{{1}}}.'
        .format(table_format,
                ', '.join([Format.TABLE, Format.DETAILED, Format.CSV])))
