# Copyright 2013 Google Inc. All Rights Reserved.

"""General console printing utilities used by the Cloud SDK."""

import logging
import string
import sys
import textwrap
import threading
import time

from googlecloudsdk.core import log
from googlecloudsdk.core import properties


class TablePrinter(object):
  """Provides the ability to print a list of items as a formatted table.

  Using this class helps you adhere to the gcloud style guide.

  The table will auto size the columns to fit the maximum item length for that
  column.  You can also choose how to justify each column and to add extra
  padding to each column.
  """

  JUSTIFY_LEFT = '<'
  JUSTIFY_RIGHT = '>'
  JUSTIFY_CENTER = '^'

  def __init__(self, headers, title=None,
               justification=None, column_padding=None):
    """Creates a new TablePrinter.

    Args:
      headers: A tuple of strings that represent the column headers titles.
        This can be a tuple of empty strings or None's if you do not want
        headers displayed.  The number of empty elements in the tuple must match
        the number of columns you want to display.
      title: str, An optional title for the table.
      justification: A tuple of JUSTIFY_LEFT, JUSTIFY_RIGHT, JUSTIFY_CENTER that
        describes the justification for each column.  This must have the same
        number of items as the headers tuple.
      column_padding: A tuple of ints that describes the extra padding that
        should be added to each column.  This must have the same
        number of items as the headers tuple.

    Raises:
      ValueError: If the justification or column_padding tuples are not of the
        correct type or length.
    """
    self.__headers = [h if h else '' for h in headers]
    self.__title = title
    self.__num_columns = len(self.__headers)
    self.__header_widths = [len(str(x)) for x in self.__headers]

    self.__column_padding = column_padding
    if self.__column_padding is None:
      self.__column_padding = tuple([0] * self.__num_columns)
    if (not isinstance(self.__column_padding, (tuple)) or
        len(self.__column_padding) != self.__num_columns):
      raise ValueError('Column padding tuple does not have {} columns'
                       .format(self.__num_columns))

    self.__justification = justification
    if self.__justification is None:
      self.__justification = tuple([TablePrinter.JUSTIFY_LEFT] *
                                   self.__num_columns)
    if (not isinstance(self.__justification, tuple) or
        len(self.__justification) != self.__num_columns):
      raise ValueError('Justification tuple does not have {} columns'
                       .format(self.__num_columns))
    for value in self.__justification:
      if not (value is TablePrinter.JUSTIFY_LEFT or
              value is TablePrinter.JUSTIFY_RIGHT or
              value is TablePrinter.JUSTIFY_CENTER):
        raise ValueError('Justification values must be one of JUSTIFY_LEFT, '
                         'JUSTIFY_RIGHT, or JUSTIFY_CENTER')

  def SetTitle(self, title):
    """Sets the title of the table.

    Args:
      title: str, The new title.
    """
    self.__title = title

  def Log(self, rows, logger=None, level=logging.INFO):
    """Logs the given rows to the given logger.

    Args:
      rows: list of tuples, The rows to log the formatted table for.
      logger: logging.Logger, The logger to do the logging.  If None, the root
        logger will be used.
      level: logging level, An optional override for the logging level, INFO by
        default.
    """
    if not logger:
      logger = log.getLogger()
    lines = self.GetLines(rows)
    for line in lines:
      logger.log(level, line)

  def Print(self, rows, output_stream=None, indent=0):
    """Prints the given rows to stdout.

    Args:
      rows: list of tuples, The rows to print the formatted table for.
      output_stream: file-like object, The stream to wire the rows to.  Defaults
        to log.out if not given.
      indent: int, The number of spaces to indent all lines of the table.
    """
    if not output_stream:
      output_stream = log.out
    lines = self.GetLines(rows, indent=indent)
    for line in lines:
      output_stream.write(line + '\n')

  def GetLines(self, rows, indent=0):
    """Gets a list of strings of formatted lines for the given rows.

    Args:
      rows: list of tuples, The rows to get the formatted table for.
      indent: int, The number of spaces to indent all lines of the table.

    Returns:
      list of str, The lines of the formatted table that can be printed.

    Raises:
      ValueError: If any row does not have the correct number of columns.
    """
    column_widths = list(self.__header_widths)
    for row in rows:
      if len(row) != self.__num_columns:
        raise ValueError('Row [{row}] does not have {rows} columns'
                         .format(row=row, rows=self.__num_columns))
      # Find the max width of each column
      for i in range(self.__num_columns):
        column_widths[i] = max(column_widths[i], len(str(row[i])))

    # Add padding
    column_widths = [column_widths[i] + self.__column_padding[i]
                     for i in range(self.__num_columns)]
    total_width = (len(column_widths) - 1) * 3
    for width in column_widths:
      total_width += width

    edge_line = ('--' +
                 '---'.join(['-' * width for width in column_widths]) +
                 '--')
    title_divider_line = ('|-' +
                          '---'.join(['-' * width for width in column_widths]) +
                          '-|')
    divider_line = ('|-' +
                    '-+-'.join(['-' * width for width in column_widths]) +
                    '-|')
    lines = [edge_line]

    if self.__title:
      title_line = '| {{title:{justify}{width}s}} |'.format(
          justify=TablePrinter.JUSTIFY_CENTER, width=total_width).format(
              title=self.__title)
      lines.append(title_line)
      lines.append(title_divider_line)

    # Generate format strings with the correct width for each column
    column_formats = []
    for i in range(self.__num_columns):
      column_formats.append('{{i{i}:{justify}{width}s}}'.format(
          i=i, justify=self.__justification[i], width=column_widths[i]))
    pattern = '| ' + ' | '.join(column_formats) + ' |'

    def _ParameterizedArrayDict(array):
      return dict(('i{i}'.format(i=i), array[i]) for i in range(len(array)))

    if [h for h in self.__headers if h]:
      # Only print headers if there is at least one non-empty header
      lines.append(pattern.format(**_ParameterizedArrayDict(self.__headers)))
      lines.append(divider_line)

    lines.extend([pattern.format(**_ParameterizedArrayDict(row))
                  for row in rows])
    lines.append(edge_line)

    if indent:
      return [(' ' * indent) + l for l in lines]
    return lines


class ListPrinter(object):
  """Provides the ability to print a list of items as a formatted list.

  Using this class helps you adhere to the gcloud style guide.
  """

  def __init__(self, title):
    """Create a titled list printer that can print rows to stdout.

    Args:
      title: A string for the title of the list.
    """
    self.__title = title

  def Print(self, rows, output_stream=None):
    """Print this list with the provided rows to stdout.

    Args:
      rows: A list of objects representing the rows of this list. Before being
          printed, they will be converted to strings.
      output_stream: file-like object, The stream to wire the rows to.  Defaults
        to log.out if not given.
    """
    if not output_stream:
      output_stream = log.out
    output_stream.write(self.__title + '\n')
    for row in rows:
      output_stream.write(' - ' + str(row) + '\n')


TEXTWRAP = textwrap.TextWrapper(replace_whitespace=False,
                                drop_whitespace=False,
                                break_on_hyphens=False)


def _DoWrap(message):
  """Text wrap the given message and correctly handle newlines in the middle.

  Args:
    message: str, The message to wrap.  It may have newlines in the middle of
      it.

  Returns:
    str, The wrapped message.
  """
  return '\n'.join([TEXTWRAP.fill(line) for line in message.splitlines()])


def _RawInput(prompt=None):
  """A simple redirect to the built-in raw_input function.

  If the prompt is given, it is correctly line wrapped.

  Args:
    prompt: str, An optional prompt.

  Returns:
    The input from stdin.
  """
  if prompt:
    sys.stderr.write(_DoWrap(prompt))

  try:
    return raw_input()
  except EOFError:
    return None


def PromptContinue(message=None, prompt_string=None):
  """Prompts the user a yes or no question and asks if they want to continue.

  Args:
    message: str, The prompt to print before the question.
    prompt_string: str, An alternate yes/no prompt to display.  If None, it
      defaults to 'Do you want to continue'.

  Returns:
    bool, False if the user said no, True if the user said anything else or if
    prompts are disabled.
  """
  if properties.VALUES.core.disable_prompts.GetBool():
    return True
  if not prompt_string:
    prompt_string = 'Do you want to continue'
  if message:
    sys.stderr.write(_DoWrap(message) + '\n\n')

  sys.stderr.write(_DoWrap(prompt_string + ' (Y/n)?  '))
  while True:
    answer = _RawInput()
    if not answer or answer.lower() in ['y', 'yes']:
      sys.stderr.write('\n')
      return True
    elif answer.lower() in ['n', 'no']:
      sys.stderr.write('\n')
      return False
    else:
      sys.stderr.write("Please enter 'y' or 'n':  ")


def PromptResponse(message):
  """Prompts the user for a string.

  Args:
    message: str, The prompt to print before the question.

  Returns:
    str, The string entered by the user, or None if prompts are disabled.
  """
  if properties.VALUES.core.disable_prompts.GetBool():
    return None
  response = _RawInput(message)
  return response


def PromptChoice(options, default=None, message=None, prompt_string=None):
  """Prompt the user to select a choice from a list of items.

  Args:
    options:  [object], A list of objects to print as choices.  Their str()
      method will be used to display them.
    default: int, The default index to return if prompting is disabled or if
      they do not enter a choice.
    message: str, An optional message to print before the choices are displayed.
    prompt_string: str, A string to print when prompting the user to enter a
      choice.  If not given, a default prompt is used.

  Raises:
    ValueError: If no options are given or if the default is not in the range of
      available options.

  Returns:
    The index of the item in the list that was chosen, or the default if prompts
    are disabled.
  """
  if not options:
    raise ValueError('You must provide at least one option.')
  maximum = len(options)
  if default is not None and not 0 <= default < maximum:
    raise ValueError(
        'Default option [{default}] is not a valid index for the options list '
        '[{maximum} options given]'.format(default=default, maximum=maximum))
  if properties.VALUES.core.disable_prompts.GetBool():
    return default

  if message:
    sys.stderr.write(_DoWrap(message) + '\n')
  for i, option in enumerate(options):
    sys.stderr.write(' [{index}] {option}\n'.format(
        index=i + 1, option=str(option)))

  if not prompt_string:
    prompt_string = 'Please enter your numeric choice'
  if default is None:
    suffix_string = ':  '
  else:
    suffix_string = ' ({default}):  '.format(default=default + 1)
  sys.stderr.write(_DoWrap(prompt_string + suffix_string))
  while True:
    answer = _RawInput()
    if answer is None or (answer is '' and default is not None):
      # Return default if we failed to read from stdin
      # Return default if the user hit enter and there is a valid default
      # Prompt again otherwise
      sys.stderr.write('\n')
      return default
    try:
      num_choice = int(answer)
      if num_choice < 1 or num_choice > maximum:
        raise ValueError('Choice must be between 1 and {maximum}'.format(
            maximum=maximum))
      sys.stderr.write('\n')
      return num_choice - 1
    except ValueError:
      sys.stderr.write('Please enter a value between 1 and {maximum}:  '
                       .format(maximum=maximum))


def LazyFormat(s, *args, **kwargs):
  """Format a string, allowing unresolved parameters to remain unresolved.

  Args:
    s: str, The string to format.
    *args: [str], A list of strings for numerical parameters.
    **kwargs: {str:str}, A dict of strings for named parameters.

  Returns:
    str, The lazily-formatted string.
  """

  class SafeDict(dict):

    def __missing__(self, key):
      return '{' + key + '}'
  return string.Formatter().vformat(s, args, SafeDict(kwargs))


def PrintExtendedList(items, col_fetchers):
  """Print a properly formated extended list for some set of resources.

  If items is a generator, this function may elect to only request those rows
  that it is ready to display.

  Args:
    items: [resource] or a generator producing resources, The objects
        representing cloud resources.
    col_fetchers: [(string, func(resource))], A list of tuples, one for each
        column, in the order that they should appear. The string is the title
        of that column which will be printed in a header. The func is a function
        that will fetch a row-value for that column, given the resource
        corresponding to the row.
  """

  total_items = 0

  rows = [[title for (title, unused_func) in col_fetchers]]
  for item in items:
    total_items += 1
    row = []
    for (unused_title, func) in col_fetchers:
      value = func(item)
      if value is None:
        row.append('-')
      else:
        row.append(value)
    rows.append(row)

  max_col_widths = [0] * len(col_fetchers)
  for row in rows:
    for col in range(len(row)):
      max_col_widths[col] = max(max_col_widths[col], len(str(row[col]))+2)

  for row in rows:
    for col in range(len(row)):
      width = max_col_widths[col]
      item = str(row[col])
      if len(item) < width and col != len(row)-1:
        item += ' ' * (width - len(item))
      log.out.write(item)
    log.out.write('\n')
  if not total_items:
    log.status.write('Listed 0 items.\n')


class ProgressTracker(object):
  """A context manager for telling the user about long-running progress."""

  SPIN_MARKS = [
      '|',
      '/',
      '-',
      '\\',
  ]

  def __init__(self, message, autotick=True):
    self._message = message
    self._prefix = message + '...'
    self._ticks = 0
    self._autotick = autotick
    self._done = False
    self._lock = threading.Lock()

  def __enter__(self):
    log.file_only_logger.info(self._prefix)
    sys.stderr.write(self._prefix)

    if self._autotick:
      def Ticker():
        while True:
          time.sleep(1)
          if self.Tick():
            return
      threading.Thread(target=Ticker).start()

    return self

  def Tick(self):
    """Give a visual indication to the user that some progress has been made."""
    with self._lock:
      if not self._done:
        self._ticks += 1
        self._Print()
        sys.stderr.write(
            ProgressTracker.SPIN_MARKS[
                self._ticks % len(ProgressTracker.SPIN_MARKS)])
      return self._done

  def _Print(self):
    sys.stderr.write('\r' + self._prefix)

  def __exit__(self, unused_type, unused_value, unused_traceback):
    with self._lock:
      self._done = True
      self._Print()
    sys.stderr.write('done.\n')


class ProgressBar(object):
  """A simple progress bar for tracking completion of an action.

  This progress bar works without having to use any control characters.  It
  prints the action that is being done, and then fills a progress bar below it.
  You should not print anything else on the output stream during this time as it
  will cause the progress bar to break on lines.

  This class can also be used in a context manager.
  """

  @staticmethod
  def _DefaultCallback(progress_factor):
    pass

  DEFAULT_CALLBACK = _DefaultCallback

  @staticmethod
  def SplitProgressBar(original_callback, weights):
    """Splits a progress bar into logical sections.

    Wraps the original callback so that each of the subsections can use the full
    range of 0 to 1 to indicate its progress.  The overall progress bar will
    display total progress based on the weights of the tasks.

    Args:
      original_callback: f(float), The original callback for the progress bar.
      weights: [float], The weights of the tasks to create.  These can be any
        numbers you want and the split will be based on their proportions to
        each other.

    Raises:
      ValueError: If the weights don't add up to 1.

    Returns:
      (f(float), ), A tuple of callback functions, in order, for the subtasks.
    """
    if (original_callback is None or
        original_callback == ProgressBar.DEFAULT_CALLBACK):
      return tuple([ProgressBar.DEFAULT_CALLBACK for _ in range(len(weights))])

    def MakeCallback(already_done, weight):
      def Callback(done_fraction):
        original_callback(already_done + (done_fraction * weight))
      return Callback

    total = float(sum(weights))
    callbacks = []
    already_done = 0
    for weight in weights:
      normalized_weight = weight / total
      callbacks.append(MakeCallback(already_done, normalized_weight))
      already_done += normalized_weight

    return tuple(callbacks)

  def __init__(self, label, stream=log.status, total_ticks=60):
    """Creates a progress bar for the given action.

    Args:
      label: str, The action that is being performed.
      stream: The output stream to write to, stderr by default.
      total_ticks: int, The number of ticks wide to make the progress bar.
    """
    self._stream = stream
    self._ticks_written = 0
    self._total_ticks = total_ticks

    max_label_width = self._total_ticks - 4
    if len(label) > max_label_width:
      label = label[:max_label_width - 3] + '...'
    elif len(label) < max_label_width:
      diff = max_label_width - len(label)
      label += ' ' * diff
    self._label = '|- {label} -|'.format(label=label)

  def Start(self):
    """Starts the progress bar by writing the label."""
    self._stream.write(self._label + '\n')
    self._stream.write('|')
    self._ticks_written = 0

  def SetProgress(self, progress_factor):
    """Sets the current progress of the task.

    This method has no effect if the progress bar has already progressed past
    the progress you call it with (since the progress bar cannot back up).

    Args:
      progress_factor: float, The current progress as a float between 0 and 1.
    """
    expected_ticks = int(self._total_ticks * progress_factor)
    new_ticks = expected_ticks - self._ticks_written
    # Don't allow us to go over 100%.
    new_ticks = min(new_ticks, self._total_ticks - self._ticks_written)

    if new_ticks > 0:
      self._stream.write('=' * new_ticks)
      self._ticks_written += new_ticks
      if expected_ticks == self._total_ticks:
        self._stream.write('|\n')
      self._stream.flush()

  def Finish(self):
    """Mark the progress as done."""
    self.SetProgress(1)

  def __enter__(self):
    self.Start()
    return self

  def __exit__(self, *args):
    self.Finish()
