# Copyright 2013 Google Inc. All Rights Reserved.

"""Generate usage text for displaying to the user.
"""

import argparse
import collections
import re
import StringIO
import sys
import textwrap

from googlecloudsdk.core.util import console_io

LINE_WIDTH = 80
HELP_INDENT = 25

MARKDOWN_BOLD = '*'
MARKDOWN_ITALIC = '_'
MARKDOWN_CODE = '`'


class ReleaseStageAnnotation(object):
  _RELEASE_STAGE_TUPLE = collections.namedtuple('ReleaseStageTuple',
                                                ['id', 'tag', 'note'])
  ALPHA = _RELEASE_STAGE_TUPLE(
      'ALPHA', '{0}(ALPHA){0} '.format(MARKDOWN_BOLD),
      'This command is currently in ALPHA and may change without notice.')
  BETA = _RELEASE_STAGE_TUPLE(
      'BETA', '{0}(BETA){0} '.format(MARKDOWN_BOLD),
      'This command is currently in BETA and may change without notice.')


class HelpInfo(object):
  """A class to hold some the information we need to generate help text."""

  def __init__(self, help_text, is_hidden, release_stage):
    """Create a HelpInfo object.

    Args:
      help_text: str, The text of the help message.
      is_hidden: bool, True if this command or group has been marked as hidden.
      release_stage: ReleaseStageTuple, The maturity level of this command or
        None if not specified.
    """
    self.help_text = help_text or ''
    self.is_hidden = is_hidden
    self.release_stage = release_stage


class CommandChoiceSuggester(object):
  """Utility to suggest mistyped commands.

  """
  TEST_QUOTA = 5000
  MAX_DISTANCE = 5

  def __init__(self):
    self.cache = {}
    self.inf = float('inf')
    self._quota = self.TEST_QUOTA

  def Deletions(self, s):
    return [s[:i] + s[i + 1:] for i in range(len(s))]

  def GetDistance(self, longer, shorter):
    """Get the edit distance between two words.

    They must be in the correct order, since deletions and mutations only happen
    from 'longer'.

    Args:
      longer: str, The longer of the two words.
      shorter: str, The shorter of the two words.

    Returns:
      int, The number of substitutions or deletions on longer required to get
      to shorter.
    """

    if longer == shorter:
      return 0

    try:
      return self.cache[(longer, shorter)]
    except KeyError:
      pass

    self.cache[(longer, shorter)] = self.inf
    best_distance = self.inf

    if len(longer) > len(shorter):
      if self._quota < 0:
        return self.inf
      self._quota -= 1
      for m in self.Deletions(longer):
        best_distance = min(best_distance, self.GetDistance(m, shorter) + 1)

    if len(longer) == len(shorter):
      # just count how many letters differ
      best_distance = 0
      for i in range(len(longer)):
        if longer[i] != shorter[i]:
          best_distance += 1

    self.cache[(longer, shorter)] = best_distance
    return best_distance

  def SuggestCommandChoice(self, arg, choices):
    """Find the item that is closest to what was attempted.

    Args:
      arg: str, The argument provided.
      choices: [str], The list of valid arguments.

    Returns:
      str, The closest match.
    """

    min_distance = self.inf
    for choice in choices:
      self._quota = self.TEST_QUOTA
      first, second = arg, choice
      if len(first) < len(second):
        first, second = second, first
      if len(first) - len(second) > self.MAX_DISTANCE:
        # Don't bother if they're too different.
        continue
      d = self.GetDistance(first, second)
      if d < min_distance:
        min_distance = d
        bestchoice = choice
    if min_distance > self.MAX_DISTANCE:
      return None
    return bestchoice


def WrapMessageInNargs(msg, nargs):
  """Create the display help string for a positional arg.

  Args:
    msg: [str] The possibly repeated text.
    nargs: The repetition operator.

  Returns:
    str, The string representation for printing.
  """
  if nargs == '+':
    return '{msg} [{msg} ...]'.format(msg=msg)
  elif nargs == '*' or nargs == argparse.REMAINDER:
    return '[{msg} ...]'.format(msg=msg)
  elif nargs == '?':
    return '[{msg}]'.format(msg=msg)
  else:
    return msg


def PositionalDisplayString(arg, markdown=False):
  """Create the display help string for a positional arg.

  Args:
    arg: argparse.Argument, The argument object to be displayed.
    markdown: bool, If true add markdowns.

  Returns:
    str, The string representation for printing.
  """
  msg = arg.metavar or arg.dest.upper()
  if markdown:
    msg = re.sub(r'(\b[a-zA-Z][-a-zA-Z_0-9]*)',
                 MARKDOWN_ITALIC + r'\1' + MARKDOWN_ITALIC, msg)
  return ' ' + WrapMessageInNargs(msg, arg.nargs)


def FlagDisplayString(arg, brief=False, markdown=False):
  """Create the display help string for a flag arg.

  Args:
    arg: argparse.Argument, The argument object to be displayed.
    brief: bool, If true, only display one version of a flag that has
        multiple versions, and do not display the default value.
    markdown: bool, If true add markdowns.

  Returns:
    str, The string representation for printing.
  """
  metavar = arg.metavar or arg.dest.upper()
  if brief:
    long_string = sorted(arg.option_strings)[0]
    if arg.nargs == 0:
      return long_string
    return '{flag} {metavar}'.format(
        flag=long_string,
        metavar=WrapMessageInNargs(metavar, arg.nargs))
  else:
    if arg.nargs == 0:
      if markdown:
        return ', '.join([MARKDOWN_BOLD + x + MARKDOWN_BOLD
                          for x in arg.option_strings])
      else:
        return ', '.join(arg.option_strings)
    else:
      if markdown:
        metavar = re.sub('(\\b[a-zA-Z][-a-zA-Z_0-9]*)',
                         MARKDOWN_ITALIC + '\\1' + MARKDOWN_ITALIC, metavar)
      display_string = ', '.join(
          ['{bb}{flag}{be} {metavar}'.format(
              bb=MARKDOWN_BOLD if markdown else '',
              flag=option_string,
              be=MARKDOWN_BOLD if markdown else '',
              metavar=WrapMessageInNargs(metavar, arg.nargs))
           for option_string in arg.option_strings])
      if not arg.required and arg.default:
        display_string += '; default="{val}"'.format(val=arg.default)
      return display_string


def _WrapWithPrefix(prefix, message, indent, length, spacing,
                    writer=sys.stdout):
  """Helper function that does two-column writing.

  If the first column is too long, the second column begins on the next line.

  Args:
    prefix: str, Text for the first column.
    message: str, Text for the second column.
    indent: int, Width of the first column.
    length: int, Width of both columns, added together.
    spacing: str, Space to put on the front of prefix.
    writer: file-like, Receiver of the written output.
  """
  def W(s):
    writer.write(s)
  def Wln(s):
    W(s + '\n')

  # Reformat the message to be of rows of the correct width, which is what's
  # left-over from length when you subtract indent. The first line also needs
  # to begin with the indent, but that will be taken care of conditionally.
  message = ('\n%%%ds' % indent % ' ').join(
      textwrap.wrap(message, length - indent))
  if len(prefix) > indent - len(spacing) - 2:
    # If the prefix is too long to fit in the indent width, start the message
    # on a new line after writing the prefix by itself.
    Wln('%s%s' % (spacing, prefix))
    # The message needs to have the first line indented properly.
    W('%%%ds' % indent % ' ')
    Wln(message)
  else:
    # If the prefix fits comfortably within the indent (2 spaces left-over),
    # print it out and start the message after adding enough whitespace to make
    # up the rest of the indent.
    W('%s%s' % (spacing, prefix))
    Wln('%%%ds %%s'
        % (indent - len(prefix) - len(spacing) - 1)
        % (' ', message))


# TODO(user): Remove this and all references.  See b/18933702.
def ShouldPrintAncestorFlag(arg):
  """Determine if an ancestor flag should be printed in a subcommand.

  This is a temporary hack to prevent these flags from showing up in
  sub-command helps.  Proper support for marking flags as global and
  rationalizing where they will be printed will be in an upcoming CL.

  Args:
    arg: The argparse argument that is to be printed.

  Returns:
    True if is should be printed, False otherwise.
  """
  return arg.option_strings[0] not in ['--user-output-enabled', '--verbosity']


def GenerateUsage(command, argument_interceptor):
  """Generate a usage string for a calliope command or group.

  Args:
    command: calliope._CommandCommon, The command or group object that we're
        generating usage for.
    argument_interceptor: calliope._ArgumentInterceptor, the object that tracks
        all of the flags for this command or group.

  Returns:
    str, The usage string.
  """
  command.LoadAllSubElements()

  buf = StringIO.StringIO()

  command_path = ' '.join(command.GetPath())
  usage_parts = []

  optional_messages = False

  flag_messages = []

  # Do positional args first, since flag args taking lists can mess them
  # up otherwise.
  # Explicitly not sorting here - order matters.
  # Make a copy, and we'll pop items off. Once we get to a REMAINDER, that goes
  # after the flags so we'll stop and finish later.
  positional_args = argument_interceptor.positional_args[:]
  while positional_args:
    arg = positional_args[0]
    if arg.nargs == argparse.REMAINDER:
      break
    positional_args.pop(0)
    usage_parts.append(PositionalDisplayString(arg))

  for arg in argument_interceptor.flag_args:
    if arg.help == argparse.SUPPRESS:
      continue
    if not arg.required:
      optional_messages = True
      continue
    # and add it to the usage
    msg = FlagDisplayString(arg, True)
    flag_messages.append(msg)
  usage_parts.extend(sorted(flag_messages))

  if optional_messages:
    # If there are any optional flags, add a simple message to the usage.
    usage_parts.append('[optional flags]')

  # positional_args will only be non-empty if we had some REMAINDER left.
  for arg in positional_args:
    usage_parts.append(PositionalDisplayString(arg))

  group_helps = command.GetSubGroupHelps()
  command_helps = command.GetSubCommandHelps()

  groups = sorted([name for (name, help_info) in group_helps.iteritems()
                   if command.is_hidden or not help_info.is_hidden])
  commands = sorted([name for (name, help_info) in command_helps.iteritems()
                     if command.is_hidden or not help_info.is_hidden])

  all_subtypes = []
  if groups:
    all_subtypes.append('group')
  if commands:
    all_subtypes.append('command')
  if groups or commands:
    usage_parts.append('<%s>' % ' | '.join(all_subtypes))

  usage_msg = ' '.join(usage_parts)

  non_option = '{command} '.format(command=command_path)

  buf.write(non_option + usage_msg + '\n')

  if groups:
    _WrapWithPrefix('group may be', ' | '.join(
        groups), HELP_INDENT, LINE_WIDTH, spacing='  ', writer=buf)
  if commands:
    _WrapWithPrefix('command may be', ' | '.join(
        commands), HELP_INDENT, LINE_WIDTH, spacing='  ', writer=buf)
  return buf.getvalue()


def ExpandHelpText(command, text):
  """Expand command {...} references in text.

  Args:
    command: calliope._CommandCommon, The command object that we're helping.
    text: str, The text chunk to expand.

  Returns:
    str, The expanded help text.
  """
  if text == command.long_help:
    long_help = ''
  else:
    long_help = ExpandHelpText(command, command.long_help)
  path = command.GetPath()
  return console_io.LazyFormat(
      text or '',
      command=' '.join(path),
      man_name='_'.join(path),
      top_command=path[0],
      parent_command=' '.join(path[:-1]),
      index=command.short_help,
      description=long_help)


def ShortHelpText(command, argument_interceptor):
  """Get a command's short help text.

  Args:
    command: calliope._CommandCommon, The command object that we're helping.
    argument_interceptor: calliope._ArgumentInterceptor, the object that tracks
        all of the flags for this command or group.

  Returns:
    str, The short help text.
  """
  command.LoadAllSubElements()

  buf = StringIO.StringIO()

  required_messages = []
  optional_messages = []

  # Sorting for consistency and readability.
  for arg in (argument_interceptor.flag_args +
              [arg for arg in argument_interceptor.ancestor_flag_args
               if ShouldPrintAncestorFlag(arg)]):
    if arg.help == argparse.SUPPRESS:
      continue
    message = (FlagDisplayString(arg, False), arg.help or '')
    if not arg.required:
      optional_messages.append(message)
      continue
    required_messages.append(message)
    # and add it to the usage
    msg = FlagDisplayString(arg, True)

  positional_messages = []

  # Explicitly not sorting here - order matters.
  for arg in argument_interceptor.positional_args:
    positional_messages.append(
        (PositionalDisplayString(arg), arg.help or ''))

  group_helps = command.GetSubGroupHelps()
  command_helps = command.GetSubCommandHelps()

  group_messages = [(name, help_info.help_text) for (name, help_info)
                    in group_helps.iteritems()
                    if command.is_hidden or not help_info.is_hidden]
  command_messages = [(name, help_info.help_text) for (name, help_info)
                      in command_helps.iteritems()
                      if command.is_hidden or not help_info.is_hidden]

  buf.write('Usage: ' + GenerateUsage(command, argument_interceptor) + '\n')

  # Second, print out the long help.

  buf.write('\n'.join(textwrap.wrap(ExpandHelpText(command, command.long_help),
                                    LINE_WIDTH)))
  buf.write('\n\n')

  # Third, print out the short help for everything that can come on
  # the command line, grouped into required flags, optional flags,
  # sub groups, sub commands, and positional arguments.

  # This printing is done by collecting a list of rows. If the row is just
  # a string, that means print it without decoration. If the row is a tuple,
  # use _WrapWithPrefix to print that tuple in aligned columns.

  required_flag_msgs = []
  unrequired_flag_msgs = []
  for arg in argument_interceptor.flag_args:
    if arg.help == argparse.SUPPRESS:
      continue
    usage = FlagDisplayString(arg, False)
    msg = (usage, arg.help or '')
    if not arg.required:
      unrequired_flag_msgs.append(msg)
    else:
      required_flag_msgs.append(msg)

  def TextIfExists(title, messages):
    if not messages:
      return None
    textbuf = StringIO.StringIO()
    textbuf.write('%s\n' % title)
    for (arg, helptxt) in messages:
      _WrapWithPrefix(arg, helptxt, HELP_INDENT, LINE_WIDTH,
                      spacing='  ', writer=textbuf)
    return textbuf.getvalue()

  all_messages = [
      TextIfExists('required flags:', sorted(required_messages)),
      TextIfExists('optional flags:', sorted(optional_messages)),
      TextIfExists('positional arguments:', positional_messages),
      TextIfExists('command groups:', sorted(group_messages)),
      TextIfExists('commands:', sorted(command_messages)),
  ]
  buf.write('\n'.join([msg for msg in all_messages if msg]))

  return buf.getvalue()


def ExtractHelpStrings(docstring):
  """Extracts short help and long help from a docstring.

  If the docstring contains a blank line (i.e., a line consisting of zero or
  more spaces), everything before the first blank line is taken as the short
  help string and everything after it is taken as the long help string. The
  short help is flowing text with no line breaks, while the long help may
  consist of multiple lines, each line beginning with an amount of whitespace
  determined by dedenting the docstring.

  If the docstring does not contain a blank line, the sequence of words in the
  docstring is used as both the short help and the long help.

  Corner cases: If the first line of the docstring is empty, everything
  following it forms the long help, and the sequence of words of in the long
  help (without line breaks) is used as the short help. If the short help
  consists of zero or more spaces, None is used instead. If the long help
  consists of zero or more spaces, the short help (which might or might not be
  None) is used instead.

  Args:
    docstring: The docstring from which short and long help are to be taken

  Returns:
    a tuple consisting of a short help string and a long help string

  """
  if docstring:
    unstripped_doc_lines = docstring.splitlines()
    stripped_doc_lines = [s.strip() for s in unstripped_doc_lines]
    try:
      empty_line_index = stripped_doc_lines.index('')
      short_help = ' '.join(stripped_doc_lines[:empty_line_index])
      raw_long_help = '\n'.join(unstripped_doc_lines[empty_line_index + 1:])
      long_help = textwrap.dedent(raw_long_help).strip()
    except ValueError:  # no empty line in stripped_doc_lines
      short_help = ' '.join(stripped_doc_lines).strip()
      long_help = None
    if not short_help:  # docstring started with a blank line
      short_help = ' '.join(stripped_doc_lines[empty_line_index + 1:]).strip()
      # words of long help as flowing text
    return (short_help or None, long_help or short_help or None)
  else:
    return (None, None)
