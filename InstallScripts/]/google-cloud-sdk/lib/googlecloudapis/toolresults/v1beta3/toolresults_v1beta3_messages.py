"""Generated message classes for toolresults version v1beta3.

Read and publish results from tools such as Build and Test.
"""

from protorpc import messages


package = 'toolresults'


class Execution(messages.Message):
  """A Execution represents a series of Steps. For instance, it could
  represent: - a jenkins job that has a Step and a test step - a release
  pipeline execution that have build, test, deploy steps  A Execution can be
  updated until its state is set to COMPLETE at which point it becomes
  immutable. Next tag: 9

  Enums:
    StateValueValuesEnum: The initial state is IN_PROGRESS.  The only legal
      state transitions is from IN_PROGRESS to COMPLETE.  A
      PRECONDITION_FAILED will be returned if an invalid transition is
      requested.  The state can only be set to COMPLETE once. A
      FAILED_PRECONDITION will be returned if the state is set to COMPLETE
      multiple times.  If the state is set to COMPLETE, all the in-progress
      steps within the execution will be set as COMPLETE. If the outcome of
      the step is not set, the outcome will be set to INCONCLUSIVE.  - In
      response always set - In create/update request: optional

  Fields:
    completionTime: The time when the Execution status transitioned to
      COMPLETE.  This value will be set automatically when state transitions
      to COMPLETE.  - In response: set if the execution state is COMPLETE. -
      In create/update request: never set
    creationTime: The time when the Execution was created.  This value will be
      set automatically when CreateExecution is called.  - In response: always
      set - In create/update request: never set
    executionId: A unique identifier within a History for this Execution.
      Returns INVALID_ARGUMENT if this field is set or overwritten by the
      caller.  - In response always set - In create/update request: never set
    outcome: Classify the result, for example into SUCCESS or FAILURE  - In
      response: present if set by create/update request - In create/update
      request: optional
    state: The initial state is IN_PROGRESS.  The only legal state transitions
      is from IN_PROGRESS to COMPLETE.  A PRECONDITION_FAILED will be returned
      if an invalid transition is requested.  The state can only be set to
      COMPLETE once. A FAILED_PRECONDITION will be returned if the state is
      set to COMPLETE multiple times.  If the state is set to COMPLETE, all
      the in-progress steps within the execution will be set as COMPLETE. If
      the outcome of the step is not set, the outcome will be set to
      INCONCLUSIVE.  - In response always set - In create/update request:
      optional
  """

  class StateValueValuesEnum(messages.Enum):
    """The initial state is IN_PROGRESS.  The only legal state transitions is
    from IN_PROGRESS to COMPLETE.  A PRECONDITION_FAILED will be returned if
    an invalid transition is requested.  The state can only be set to COMPLETE
    once. A FAILED_PRECONDITION will be returned if the state is set to
    COMPLETE multiple times.  If the state is set to COMPLETE, all the in-
    progress steps within the execution will be set as COMPLETE. If the
    outcome of the step is not set, the outcome will be set to INCONCLUSIVE.
    - In response always set - In create/update request: optional

    Values:
      complete: <no description>
      inProgress: <no description>
      unknownState: <no description>
    """
    complete = 0
    inProgress = 1
    unknownState = 2

  completionTime = messages.MessageField('Timestamp', 1)
  creationTime = messages.MessageField('Timestamp', 2)
  executionId = messages.StringField(3)
  outcome = messages.MessageField('Outcome', 4)
  state = messages.EnumField('StateValueValuesEnum', 5)


class FailureDetail(messages.Message):
  """A FailureDetail object.

  Fields:
    crashed: If the failure was severe because the system under test crashed.
  """

  crashed = messages.BooleanField(1)


class FileReference(messages.Message):
  """A reference to a file.

  Fields:
    fileUri: A URI to a file stored in Google Cloud Storage. For example:
      http://storage.googleapis.com/mybucket/path/to/test.xml  An
      INVALID_ARGUMENT will be returned if the uri format is not supported.  -
      In response: always set - In create/update request: always set
  """

  fileUri = messages.StringField(1)


class History(messages.Message):
  """A History represents a sorted list of Executions ordered by the
  start_timestamp_millis field (descending). It can be used to group all the
  Executions of a continuous build.  Note that the ordering only operates on
  one-dimension. If a repository has multiple branches, it means that multiple
  histories will need to be used in order to order Executions per branch.

  Fields:
    displayName: A short human-readable (plain text) name to display in the
      UI. Maximum of 100 characters.  - In response always set - In create
      request: always set
    historyId: A unique identifier within a project for this History.  Returns
      INVALID_ARGUMENT if this field is set or overwritten by the caller.  -
      In response always set - In create request: never set
  """

  displayName = messages.StringField(1)
  historyId = messages.StringField(2)


class InconclusiveDetail(messages.Message):
  """A InconclusiveDetail object.

  Fields:
    abortedByUser: If the end user aborted the test execution before a pass or
      fail could be determined. For example, the user pressed ctrl-c which
      sent a kill signal to the test runner while the test was running.
    infrastructureFailure: If the test runner could not determine success or
      failure because the test depends on a component other than the system
      under test which failed.  For example, a mobile test requires
      provisioning a device where the test executes, and that provisioning can
      fail.
  """

  abortedByUser = messages.BooleanField(1)
  infrastructureFailure = messages.BooleanField(2)


class ListExecutionsResponse(messages.Message):
  """Next tag: 3

  Fields:
    executions: Executions.  Always set.
    nextPageToken: A continuation token to resume the query at the next item.
      Will only be set if there are more Executions to fetch.
  """

  executions = messages.MessageField('Execution', 1, repeated=True)
  nextPageToken = messages.StringField(2)


class ListHistoriesResponse(messages.Message):
  """Response message for HistoryService.List

  Fields:
    histories: Histories.
    nextPageToken: A continuation token to resume the query at the next item.
      Will only be set if there are more histories to fetch.  Tokens are valid
      for up to one hour from the time of the first list request. For
      instance, if you make a list request at 1PM and use the token from this
      first request 10 minutes later, the token from this second response will
      only be valid for 50 minutes.
  """

  histories = messages.MessageField('History', 1, repeated=True)
  nextPageToken = messages.StringField(2)


class ListStepsResponse(messages.Message):
  """Response message for StepService.List.

  Fields:
    nextPageToken: A continuation token to resume the query at the next item.
      If set, indicates that there are more steps to read, by calling list
      again with this value in the page_token field.
    steps: Steps.
  """

  nextPageToken = messages.StringField(1)
  steps = messages.MessageField('Step', 2, repeated=True)


class Outcome(messages.Message):
  """Interprets a result so that humans and machines can act on it.

  Enums:
    SummaryValueValuesEnum: The simplest way to interpret a result.  Required

  Fields:
    failureDetail: More information about a FAILURE outcome.  Returns
      INVALID_ARGUMENT if this field is set but the summary is not FAILURE.
      Optional
    inconclusiveDetail: More information about an INCONCLUSIVE outcome.
      Returns INVALID_ARGUMENT if this field is set but the summary is not
      INCONCLUSIVE.  Optional
    summary: The simplest way to interpret a result.  Required
  """

  class SummaryValueValuesEnum(messages.Enum):
    """The simplest way to interpret a result.  Required

    Values:
      failure: <no description>
      inconclusive: <no description>
      success: <no description>
      unset: <no description>
    """
    failure = 0
    inconclusive = 1
    success = 2
    unset = 3

  failureDetail = messages.MessageField('FailureDetail', 1)
  inconclusiveDetail = messages.MessageField('InconclusiveDetail', 2)
  summary = messages.EnumField('SummaryValueValuesEnum', 3)


class PublishXunitXmlFilesRequest(messages.Message):
  """Request message for StepService.PublishXunitXmlFiles.

  Fields:
    xunitXmlFiles: URI of the Xunit XML files to publish.  The maximum size of
      the file this reference is pointing to is 50MB.  Required.
  """

  xunitXmlFiles = messages.MessageField('FileReference', 1, repeated=True)


class StandardQueryParameters(messages.Message):
  """Query parameters accepted by all methods.

  Enums:
    AltValueValuesEnum: Data format for the response.

  Fields:
    alt: Data format for the response.
    fields: Selector specifying which fields to include in a partial response.
    key: API key. Your API key identifies your project and provides you with
      API access, quota, and reports. Required unless you provide an OAuth 2.0
      token.
    oauth_token: OAuth 2.0 token for the current user.
    prettyPrint: Returns response with indentations and line breaks.
    quotaUser: Available to use for quota purposes for server-side
      applications. Can be any arbitrary string assigned to a user, but should
      not exceed 40 characters. Overrides userIp if both are provided.
    trace: A tracing token of the form "token:<tokenid>" or "email:<ldap>" to
      include in api requests.
    userIp: IP address of the site where the request originates. Use this if
      you want to enforce per-user limits.
  """

  class AltValueValuesEnum(messages.Enum):
    """Data format for the response.

    Values:
      json: Responses with Content-Type of application/json
    """
    json = 0

  alt = messages.EnumField('AltValueValuesEnum', 1, default=u'json')
  fields = messages.StringField(2)
  key = messages.StringField(3)
  oauth_token = messages.StringField(4)
  prettyPrint = messages.BooleanField(5, default=True)
  quotaUser = messages.StringField(6)
  trace = messages.StringField(7)
  userIp = messages.StringField(8)


class Step(messages.Message):
  """A Step represents a single operation performed as part of Execution. A
  step can be used to represent the execution of a tool ( for example a test
  runner execution or an execution of a compiler).  Steps can overlap (for
  instance two steps might have the same start time if some operations are
  done in parallel).  Here is an example, let's consider that we have a
  continuous build is executing a test runner for each iteration. The workflow
  would look like: - user creates a Execution with id 1 - user creates an
  TestExecutionStep with id 100 for Execution 1 - user update
  TestExecutionStep with id 100 to add a raw xml log + the service parses the
  xml logs and returns a TestExecutionStep with updated TestResult(s). - user
  update the status of TestExecutionStep with id 100 to COMPLETE  A Step can
  be updated until its state is set to COMPLETE at which points it becomes
  immutable.  Next tag: 17

  Enums:
    StateValueValuesEnum: The initial state is IN_PROGRESS. The only legal
      state transitions are * IN_PROGRESS -> COMPLETE  A PRECONDITION_FAILED
      will be returned if an invalid transition is requested.  It is valid to
      create Step with a state set to COMPLETE. The state can only be set to
      COMPLETE once. A PRECONDITION_FAILED will be returned if the state is
      set to COMPLETE multiple times.  - In response: always set - In
      create/update request: optional

  Fields:
    completionTime: The time when the step status was set to complete.  This
      value will be set automatically when state transitions to COMPLETE.  -
      In response: set if the execution state is COMPLETE. - In create/update
      request: never set
    creationTime: The time when the step was created.  - In response: always
      set - In create/update request: never set
    description: A description of this tool For example: mvm clean package -D
      skipTests=true  - In response: present if set by create/update request -
      In create/update request: optional
    dimensionValue: If the execution containing this step has any
      dimension_definition set, then this field allows the child to specify
      the values of the dimensions.  The keys must exactly match the
      dimension_definition of the execution.  For example, if the execution
      has `dimension_definition = ['attempt', 'device']` then a step must
      define values for those dimensions, eg. `dimension_value = ['attempt':
      '1', 'device': 'Nexus 6']`  If a step does not participate in one
      dimension of the matrix, the value for that dimension should be empty
      string. For example, if one of the tests is executed by a runner which
      does not support retries, the step could have `dimension_value =
      ['attempt': '', 'device': 'Nexus 6']`  If the step does not participate
      in any dimensions of the matrix, it may leave dimension_value unset.  A
      PRECONDITION_FAILED will be returned if any of the keys do not exist in
      the dimension_definition of the execution.  A PRECONDITION_FAILED will
      be returned if another step in this execution which already has the same
      name and dimension_value.  A PRECONDITION_FAILED will be returned if
      dimension_value is set, and there is a dimension_definition in the
      execution which is not specified as one of the keys.  - In response:
      present if set by create - In create request: optional - In update
      request: never set
    hasImages: Whether any of the outputs of this step are images whose
      thumbnails can be fetched with ListThumbnails.  - In response: always
      set - In create/update request: never set
    labels: Arbitrary user-supplied key/value pairs that are associated with
      the step.  Users are responsible for managing the key namespace such
      that keys don't accidentally collide.  An INVALID_ARGUMENT will be
      returned if the number of labels exceeds 100 or if the length of any of
      the keys or values exceeds 100 characters.  - In response: always set -
      In create request: optional - In update request: optional; any new
      key/value pair will be added to the map, and any new value for an
      existing key will update that key's value
    name: A short human-readable name to display in the UI. Maximum of 100
      characters. For example: Clean build  - In response: always set - In
      create request: always set - In update request: never set
    outcome: Classification of the result, for example into SUCCESS or FAILURE
      - In response: present if set by create/update request - In
      create/update request: optional
    state: The initial state is IN_PROGRESS. The only legal state transitions
      are * IN_PROGRESS -> COMPLETE  A PRECONDITION_FAILED will be returned if
      an invalid transition is requested.  It is valid to create Step with a
      state set to COMPLETE. The state can only be set to COMPLETE once. A
      PRECONDITION_FAILED will be returned if the state is set to COMPLETE
      multiple times.  - In response: always set - In create/update request:
      optional
    stepId: A unique identifier within a Execution for this Step.  Returns
      INVALID_ARGUMENT if this field is set or overwritten by the caller.  -
      In response: always set - In create/update request: never set
    testExecutionStep: An execution of a test runner.
    toolExecutionStep: An execution of a tool (used for steps we don't
      explicitly support).
  """

  class StateValueValuesEnum(messages.Enum):
    """The initial state is IN_PROGRESS. The only legal state transitions are
    * IN_PROGRESS -> COMPLETE  A PRECONDITION_FAILED will be returned if an
    invalid transition is requested.  It is valid to create Step with a state
    set to COMPLETE. The state can only be set to COMPLETE once. A
    PRECONDITION_FAILED will be returned if the state is set to COMPLETE
    multiple times.  - In response: always set - In create/update request:
    optional

    Values:
      complete: <no description>
      inProgress: <no description>
      unknownState: <no description>
    """
    complete = 0
    inProgress = 1
    unknownState = 2

  completionTime = messages.MessageField('Timestamp', 1)
  creationTime = messages.MessageField('Timestamp', 2)
  description = messages.StringField(3)
  dimensionValue = messages.MessageField('StepDimensionValueEntry', 4, repeated=True)
  hasImages = messages.BooleanField(5)
  labels = messages.MessageField('StepLabelsEntry', 6, repeated=True)
  name = messages.StringField(7)
  outcome = messages.MessageField('Outcome', 8)
  state = messages.EnumField('StateValueValuesEnum', 9)
  stepId = messages.StringField(10)
  testExecutionStep = messages.MessageField('TestExecutionStep', 11)
  toolExecutionStep = messages.MessageField('ToolExecutionStep', 12)


class StepDimensionValueEntry(messages.Message):
  """A StepDimensionValueEntry object.

  Fields:
    key: A string attribute.
    value: A string attribute.
  """

  key = messages.StringField(1)
  value = messages.StringField(2)


class StepLabelsEntry(messages.Message):
  """A StepLabelsEntry object.

  Fields:
    key: A string attribute.
    value: A string attribute.
  """

  key = messages.StringField(1)
  value = messages.StringField(2)


class TestCaseReference(messages.Message):
  """A reference to a test case.  Test case references are canonically ordered
  lexicographically by these three factors: * First, by test_suite_name. *
  Second, by class_name. * Third, by name.

  Fields:
    className: The name of the class.
    name: The name of the test case.  Required.
    testSuiteName: The name of the test suite to which this test case belongs.
  """

  className = messages.StringField(1)
  name = messages.StringField(2)
  testSuiteName = messages.StringField(3)


class TestExecutionStep(messages.Message):
  """A step that represents running tests.  It accepts ant-junit xml files
  which will be parsed into structured test results by the service. Xml file
  paths are updated in order to append more files, however they can't be
  deleted.  Users can also add test results manually by using the test_result
  field.

  Fields:
    testSuiteOverviews: List of test suite overview contents. This could be
      parsed from xUnit XML log by server, or uploaded directly by user. This
      references should only be called when test suites are fully parsed or
      uploaded.  The maximum allowed number of test suite overviews per step
      is 1000.  - In response: always set - In create request: optional - In
      update request: never (use publishXunitXmlFiles custom method instead)
    toolExecution: Represents the execution of the test runner.  The exit code
      of this tool will be used to determine if the test passed.  - In
      response: always set - In create/update request: optional
  """

  testSuiteOverviews = messages.MessageField('TestSuiteOverview', 1, repeated=True)
  toolExecution = messages.MessageField('ToolExecution', 2)


class TestSuiteOverview(messages.Message):
  """A summary of a test suite result either parsed from XML or uploaded
  directly by a user. Next tag: 7

  Fields:
    errorCount: Number of test cases in error, typically set by the service by
      parsing the xml_source.  - In response: always set - In create/update
      request: never
    failureCount: Number of failed test cases, typically set by the service by
      parsing the xml_source. May also be set by the user.  - In response:
      always set - In create/update request: never
    name: The name of the test suite.  - In response: always set - In
      create/update request: never
    skippedCount: Number of test cases not run, typically set by the service
      by parsing the xml_source.  - In response: always set - In create/update
      request: never
    totalCount: Number of test cases, typically set by the service by parsing
      the xml_source.  - In response: always set - In create/update request:
      never
    xmlSource: If this test suite was parsed from XML, this is the URI where
      the original XML file is stored.  Note: Multiple test suites can share
      the same xml_source  Returns INVALID_ARGUMENT if the uri format is not
      supported.  - In response: optional - In create/update request: never
  """

  errorCount = messages.IntegerField(1, variant=messages.Variant.INT32)
  failureCount = messages.IntegerField(2, variant=messages.Variant.INT32)
  name = messages.StringField(3)
  skippedCount = messages.IntegerField(4, variant=messages.Variant.INT32)
  totalCount = messages.IntegerField(5, variant=messages.Variant.INT32)
  xmlSource = messages.MessageField('FileReference', 6)


class Timestamp(messages.Message):
  """A Timestamp represents a point in time independent of any time zone or
  calendar, represented as seconds and fractions of seconds at nanosecond
  resolution in UTC Epoch time. It is encoded using the Proleptic Gregorian
  Calendar which extends the Gregorian calendar backwards to year one. It is
  encoded assuming all minutes are 60 seconds long, i.e. leap seconds are
  "smeared" so that no leap second table is needed for interpretation. Range
  is from 0001-01-01T00:00:00Z to 9999-12-31T23:59:59.999999999Z.  Example 1:
  compute Timestamp from POSIX `time()`.  Timestamp timestamp;
  timestamp.set_seconds(time(NULL)); timestamp.set_nanos(0);  Example 2:
  compute Timestamp from POSIX `gettimeofday()`.  struct timeval tv;
  gettimeofday(&tv, NULL);  Timestamp timestamp;
  timestamp.set_seconds(tv.tv_sec); timestamp.set_nanos(tv.tv_usec * 1000);
  Example 3: compute Timestamp from Win32 `GetSystemTimeAsFileTime()`.
  FILETIME ft; GetSystemTimeAsFileTime(&ft); UINT64 ticks =
  (((UINT64)ft.dwHighDateTime) << 32) | ft.dwLowDateTime;  // A Windows tick
  is 100 nanoseconds. Windows epoch 1601-01-01T00:00:00Z // is 11644473600
  seconds before Unix epoch 1970-01-01T00:00:00Z. Timestamp timestamp;
  timestamp.set_seconds((INT64) ((ticks / 10000000) - 11644473600LL));
  timestamp.set_nanos((INT32) ((ticks % 10000000) * 100));  Example 4: compute
  Timestamp from Java `System.currentTimeMillis()`.  long millis =
  System.currentTimeMillis();  Timestamp timestamp =
  Timestamp.newBuilder().setSeconds(millis / 1000) .setNanos((int) ((millis %
  1000) * 1000000)).build();  Example 5: compute Timestamp from Python
  `datetime.datetime`.  now = datetime.datetime.utcnow() seconds =
  int(time.mktime(now.timetuple())) nanos = now.microsecond * 1000 timestamp =
  Timestamp(seconds=seconds, nanos=nanos)

  Fields:
    nanos: Non-negative fractions of a second at nanosecond resolution.
      Negative second values with fractions must still have non-negative nanos
      values that count forward in time. Must be from 0 to 999,999,999
      inclusive.
    seconds: Represents seconds of UTC time since Unix epoch
      1970-01-01T00:00:00Z. Must be from from 0001-01-01T00:00:00Z to
      9999-12-31T23:59:59Z inclusive.
  """

  nanos = messages.IntegerField(1, variant=messages.Variant.INT32)
  seconds = messages.IntegerField(2)


class ToolExecution(messages.Message):
  """An execution of an arbitrary tool. It could be a test runner or a tool
  copying artifacts or deploying code. Next tag: 6

  Fields:
    commandLineArguments: The full tokenized command line including the
      program name (equivalent to argv in a C program).  - In response:
      present if set by create request - In create request: optional - In
      update request: never set
    exitCode: Tool execution exit code. This field will be set once the tool
      has exited.  - In response: present if set by create/update request - In
      create request: optional - In update request: optional, a
      FAILED_PRECONDITION error will be returned if an exit_code is already
      set.
    toolLogs: References to any plain text logs output the tool execution.
      This field can be set before the tool has exited in order to be able to
      have access to a live view of the logs while the tool is running.  The
      maximum allowed number of tool logs per step is 1000.  - In response:
      present if set by create/update request - In create request: optional -
      In update request: optional, any value provided will be appended to the
      existing list
    toolOutputs: References to opaque files of any format output by the tool
      execution.  The maximum allowed number of tool outputs per step is 1000.
      - In response: present if set by create/update request - In create
      request: optional - In update request: optional, any value provided will
      be appended to the existing list
  """

  commandLineArguments = messages.StringField(1, repeated=True)
  exitCode = messages.MessageField('ToolExitCode', 2)
  toolLogs = messages.MessageField('FileReference', 3, repeated=True)
  toolOutputs = messages.MessageField('ToolOutputReference', 4, repeated=True)


class ToolExecutionStep(messages.Message):
  """Generic tool step to be used for binaries we do not explicitly support.
  For example: running cp to copy artifacts from one location to another.

  Fields:
    toolExecution: A Tool execution.  - In response: present if set by
      create/update request - In create/update request: optional
  """

  toolExecution = messages.MessageField('ToolExecution', 1)


class ToolExitCode(messages.Message):
  """Exit code from a tool execution.

  Fields:
    number: Tool execution exit code. A value of 0 means that the execution
      was successful.  - In response: always set - In create/update request:
      always set
  """

  number = messages.IntegerField(1, variant=messages.Variant.INT32)


class ToolOutputReference(messages.Message):
  """A reference to a ToolExecution output file.

  Fields:
    creationTime: The creation time of the file.  - In response: present if
      set by create/update request - In create/update request: optional
    output: A FileReference to an output file.  - In response: always set - In
      create/update request: always set
    testCase: The test case to which this output file belongs.  - In response:
      present if set by create/update request - In create/update request:
      optional
  """

  creationTime = messages.MessageField('Timestamp', 1)
  output = messages.MessageField('FileReference', 2)
  testCase = messages.MessageField('TestCaseReference', 3)


class ToolresultsProjectsHistoriesCreateRequest(messages.Message):
  """A ToolresultsProjectsHistoriesCreateRequest object.

  Fields:
    history: A History resource to be passed as the request body.
    projectId: A Project id.  Required.
  """

  history = messages.MessageField('History', 1)
  projectId = messages.StringField(2, required=True)


class ToolresultsProjectsHistoriesExecutionsCreateRequest(messages.Message):
  """A ToolresultsProjectsHistoriesExecutionsCreateRequest object.

  Fields:
    execution: A Execution resource to be passed as the request body.
    historyId: A History id.  Required.
    projectId: A Project id.  Required.
  """

  execution = messages.MessageField('Execution', 1)
  historyId = messages.StringField(2, required=True)
  projectId = messages.StringField(3, required=True)


class ToolresultsProjectsHistoriesExecutionsGetRequest(messages.Message):
  """A ToolresultsProjectsHistoriesExecutionsGetRequest object.

  Fields:
    executionId: A Execution id.  Required.
    historyId: A History id.  Required.
    projectId: A Project id.  Required.
  """

  executionId = messages.StringField(1, required=True)
  historyId = messages.StringField(2, required=True)
  projectId = messages.StringField(3, required=True)


class ToolresultsProjectsHistoriesExecutionsListRequest(messages.Message):
  """A ToolresultsProjectsHistoriesExecutionsListRequest object.

  Fields:
    historyId: A History id.  Required.
    pageSize: The maximum number of Executions to fetch.  Default value: 25.
      The server will use this default if the field is not set or has a value
      of 0.  Optional.
    pageToken: A continuation token to resume the query at the next item.
      Optional.
    projectId: A Project id.  Required.
  """

  historyId = messages.StringField(1, required=True)
  pageSize = messages.IntegerField(2, variant=messages.Variant.INT32)
  pageToken = messages.StringField(3)
  projectId = messages.StringField(4, required=True)


class ToolresultsProjectsHistoriesExecutionsPatchRequest(messages.Message):
  """A ToolresultsProjectsHistoriesExecutionsPatchRequest object.

  Fields:
    execution: A Execution resource to be passed as the request body.
    executionId: Required.
    historyId: Required.
    projectId: A Project id. Required.
  """

  execution = messages.MessageField('Execution', 1)
  executionId = messages.StringField(2, required=True)
  historyId = messages.StringField(3, required=True)
  projectId = messages.StringField(4, required=True)


class ToolresultsProjectsHistoriesExecutionsStepsCreateRequest(messages.Message):
  """A ToolresultsProjectsHistoriesExecutionsStepsCreateRequest object.

  Fields:
    executionId: A Execution id.  Required.
    historyId: A History id.  Required.
    projectId: A Project id.  Required.
    step: A Step resource to be passed as the request body.
  """

  executionId = messages.StringField(1, required=True)
  historyId = messages.StringField(2, required=True)
  projectId = messages.StringField(3, required=True)
  step = messages.MessageField('Step', 4)


class ToolresultsProjectsHistoriesExecutionsStepsGetRequest(messages.Message):
  """A ToolresultsProjectsHistoriesExecutionsStepsGetRequest object.

  Fields:
    executionId: A Execution id.  Required.
    historyId: A History id.  Required.
    projectId: A Project id.  Required.
    stepId: A Step id.  Required.
  """

  executionId = messages.StringField(1, required=True)
  historyId = messages.StringField(2, required=True)
  projectId = messages.StringField(3, required=True)
  stepId = messages.StringField(4, required=True)


class ToolresultsProjectsHistoriesExecutionsStepsListRequest(messages.Message):
  """A ToolresultsProjectsHistoriesExecutionsStepsListRequest object.

  Fields:
    executionId: A Execution id.  Required.
    historyId: A History id.  Required.
    pageSize: The maximum number of Steps to fetch.  Default value: 25. The
      server will use this default if the field is not set or has a value of
      0.  Optional.
    pageToken: A continuation token to resume the query at the next item.
      Optional.
    projectId: A Project id.  Required.
  """

  executionId = messages.StringField(1, required=True)
  historyId = messages.StringField(2, required=True)
  pageSize = messages.IntegerField(3, variant=messages.Variant.INT32)
  pageToken = messages.StringField(4)
  projectId = messages.StringField(5, required=True)


class ToolresultsProjectsHistoriesExecutionsStepsPatchRequest(messages.Message):
  """A ToolresultsProjectsHistoriesExecutionsStepsPatchRequest object.

  Fields:
    executionId: A Execution id.  Required.
    historyId: A History id.  Required.
    projectId: A Project id.  Required.
    step: A Step resource to be passed as the request body.
    stepId: A Step id.  Required.
  """

  executionId = messages.StringField(1, required=True)
  historyId = messages.StringField(2, required=True)
  projectId = messages.StringField(3, required=True)
  step = messages.MessageField('Step', 4)
  stepId = messages.StringField(5, required=True)


class ToolresultsProjectsHistoriesExecutionsStepsPublishXunitXmlFilesRequest(messages.Message):
  """A ToolresultsProjectsHistoriesExecutionsStepsPublishXunitXmlFilesRequest
  object.

  Fields:
    executionId: A Execution id.  Required.
    historyId: A History id.  Required.
    projectId: A Project id.  Required.
    publishXunitXmlFilesRequest: A PublishXunitXmlFilesRequest resource to be
      passed as the request body.
    stepId: A Step id. Note: This step must include a TestExecutionStep.
      Required.
  """

  executionId = messages.StringField(1, required=True)
  historyId = messages.StringField(2, required=True)
  projectId = messages.StringField(3, required=True)
  publishXunitXmlFilesRequest = messages.MessageField('PublishXunitXmlFilesRequest', 4)
  stepId = messages.StringField(5, required=True)


class ToolresultsProjectsHistoriesGetRequest(messages.Message):
  """A ToolresultsProjectsHistoriesGetRequest object.

  Fields:
    historyId: A History id.  Required.
    projectId: A Project id.  Required.
  """

  historyId = messages.StringField(1, required=True)
  projectId = messages.StringField(2, required=True)


class ToolresultsProjectsHistoriesListRequest(messages.Message):
  """A ToolresultsProjectsHistoriesListRequest object.

  Fields:
    filterByDisplayName: If set, only return histories with the given name.
      Optional.
    pageSize: The maximum number of Histories to fetch.  Default value: 20.
      The server will use this default if the field is not set or has a value
      of 0. Any value greater than 100 will be treated as 100.  Optional.
    pageToken: A continuation token to resume the query at the next item.
      Optional.
    projectId: A Project id.  Required.
  """

  filterByDisplayName = messages.StringField(1)
  pageSize = messages.IntegerField(2, variant=messages.Variant.INT32)
  pageToken = messages.StringField(3)
  projectId = messages.StringField(4, required=True)


