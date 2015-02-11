"""Generated message classes for bigquery version v2.

A data platform for customers to create, manage, share and query data.
"""

from protorpc import messages

from googlecloudapis.apitools.base.py import encoding
from googlecloudapis.apitools.base.py import extra_types


package = 'bigquery'


class BigqueryDatasetsDeleteRequest(messages.Message):
  """A BigqueryDatasetsDeleteRequest object.

  Fields:
    datasetId: Dataset ID of dataset being deleted
    deleteContents: If True, delete all the tables in the dataset. If False
      and the dataset contains tables, the request will fail. Default is False
    projectId: Project ID of the dataset being deleted
  """

  datasetId = messages.StringField(1, required=True)
  deleteContents = messages.BooleanField(2)
  projectId = messages.StringField(3, required=True)


class BigqueryDatasetsDeleteResponse(messages.Message):
  """An empty BigqueryDatasetsDelete response."""


class BigqueryDatasetsGetRequest(messages.Message):
  """A BigqueryDatasetsGetRequest object.

  Fields:
    datasetId: Dataset ID of the requested dataset
    projectId: Project ID of the requested dataset
  """

  datasetId = messages.StringField(1, required=True)
  projectId = messages.StringField(2, required=True)


class BigqueryDatasetsInsertRequest(messages.Message):
  """A BigqueryDatasetsInsertRequest object.

  Fields:
    dataset: A Dataset resource to be passed as the request body.
    projectId: Project ID of the new dataset
  """

  dataset = messages.MessageField('Dataset', 1)
  projectId = messages.StringField(2, required=True)


class BigqueryDatasetsListRequest(messages.Message):
  """A BigqueryDatasetsListRequest object.

  Fields:
    all: Whether to list all datasets, including hidden ones
    maxResults: The maximum number of results to return
    pageToken: Page token, returned by a previous call, to request the next
      page of results
    projectId: Project ID of the datasets to be listed
  """

  all = messages.BooleanField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32)
  pageToken = messages.StringField(3)
  projectId = messages.StringField(4, required=True)


class BigqueryDatasetsPatchRequest(messages.Message):
  """A BigqueryDatasetsPatchRequest object.

  Fields:
    dataset: A Dataset resource to be passed as the request body.
    datasetId: Dataset ID of the dataset being updated
    projectId: Project ID of the dataset being updated
  """

  dataset = messages.MessageField('Dataset', 1)
  datasetId = messages.StringField(2, required=True)
  projectId = messages.StringField(3, required=True)


class BigqueryDatasetsUpdateRequest(messages.Message):
  """A BigqueryDatasetsUpdateRequest object.

  Fields:
    dataset: A Dataset resource to be passed as the request body.
    datasetId: Dataset ID of the dataset being updated
    projectId: Project ID of the dataset being updated
  """

  dataset = messages.MessageField('Dataset', 1)
  datasetId = messages.StringField(2, required=True)
  projectId = messages.StringField(3, required=True)


class BigqueryJobsGetQueryResultsRequest(messages.Message):
  """A BigqueryJobsGetQueryResultsRequest object.

  Fields:
    jobId: Job ID of the query job
    maxResults: Maximum number of results to read
    pageToken: Page token, returned by a previous call, to request the next
      page of results
    projectId: Project ID of the query job
    startIndex: Zero-based index of the starting row
    timeoutMs: How long to wait for the query to complete, in milliseconds,
      before returning. Default is to return immediately. If the timeout
      passes before the job completes, the request will fail with a TIMEOUT
      error
  """

  jobId = messages.StringField(1, required=True)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32)
  pageToken = messages.StringField(3)
  projectId = messages.StringField(4, required=True)
  startIndex = messages.IntegerField(5, variant=messages.Variant.UINT64)
  timeoutMs = messages.IntegerField(6, variant=messages.Variant.UINT32)


class BigqueryJobsGetRequest(messages.Message):
  """A BigqueryJobsGetRequest object.

  Fields:
    jobId: Job ID of the requested job
    projectId: Project ID of the requested job
  """

  jobId = messages.StringField(1, required=True)
  projectId = messages.StringField(2, required=True)


class BigqueryJobsInsertRequest(messages.Message):
  """A BigqueryJobsInsertRequest object.

  Fields:
    job: A Job resource to be passed as the request body.
    projectId: Project ID of the project that will be billed for the job
  """

  job = messages.MessageField('Job', 1)
  projectId = messages.StringField(2, required=True)


class BigqueryJobsListRequest(messages.Message):
  """A BigqueryJobsListRequest object.

  Enums:
    ProjectionValueValuesEnum: Restrict information returned to a set of
      selected fields
    StateFilterValueValuesEnum: Filter for job state

  Fields:
    allUsers: Whether to display jobs owned by all users in the project.
      Default false
    maxResults: Maximum number of results to return
    pageToken: Page token, returned by a previous call, to request the next
      page of results
    projectId: Project ID of the jobs to list
    projection: Restrict information returned to a set of selected fields
    stateFilter: Filter for job state
  """

  class ProjectionValueValuesEnum(messages.Enum):
    """Restrict information returned to a set of selected fields

    Values:
      full: Includes all job data
      minimal: Does not include the job configuration
    """
    full = 0
    minimal = 1

  class StateFilterValueValuesEnum(messages.Enum):
    """Filter for job state

    Values:
      done: Finished jobs
      pending: Pending jobs
      running: Running jobs
    """
    done = 0
    pending = 1
    running = 2

  allUsers = messages.BooleanField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32)
  pageToken = messages.StringField(3)
  projectId = messages.StringField(4, required=True)
  projection = messages.EnumField('ProjectionValueValuesEnum', 5)
  stateFilter = messages.EnumField('StateFilterValueValuesEnum', 6, repeated=True)


class BigqueryJobsQueryRequest(messages.Message):
  """A BigqueryJobsQueryRequest object.

  Fields:
    projectId: Project ID of the project billed for the query
    queryRequest: A QueryRequest resource to be passed as the request body.
  """

  projectId = messages.StringField(1, required=True)
  queryRequest = messages.MessageField('QueryRequest', 2)


class BigqueryProjectsListRequest(messages.Message):
  """A BigqueryProjectsListRequest object.

  Fields:
    maxResults: Maximum number of results to return
    pageToken: Page token, returned by a previous call, to request the next
      page of results
  """

  maxResults = messages.IntegerField(1, variant=messages.Variant.UINT32)
  pageToken = messages.StringField(2)


class BigqueryTabledataInsertAllRequest(messages.Message):
  """A BigqueryTabledataInsertAllRequest object.

  Fields:
    datasetId: Dataset ID of the destination table.
    projectId: Project ID of the destination table.
    tableDataInsertAllRequest: A TableDataInsertAllRequest resource to be
      passed as the request body.
    tableId: Table ID of the destination table.
  """

  datasetId = messages.StringField(1, required=True)
  projectId = messages.StringField(2, required=True)
  tableDataInsertAllRequest = messages.MessageField('TableDataInsertAllRequest', 3)
  tableId = messages.StringField(4, required=True)


class BigqueryTabledataListRequest(messages.Message):
  """A BigqueryTabledataListRequest object.

  Fields:
    datasetId: Dataset ID of the table to read
    maxResults: Maximum number of results to return
    pageToken: Page token, returned by a previous call, identifying the result
      set
    projectId: Project ID of the table to read
    startIndex: Zero-based index of the starting row to read
    tableId: Table ID of the table to read
  """

  datasetId = messages.StringField(1, required=True)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32)
  pageToken = messages.StringField(3)
  projectId = messages.StringField(4, required=True)
  startIndex = messages.IntegerField(5, variant=messages.Variant.UINT64)
  tableId = messages.StringField(6, required=True)


class BigqueryTablesDeleteRequest(messages.Message):
  """A BigqueryTablesDeleteRequest object.

  Fields:
    datasetId: Dataset ID of the table to delete
    projectId: Project ID of the table to delete
    tableId: Table ID of the table to delete
  """

  datasetId = messages.StringField(1, required=True)
  projectId = messages.StringField(2, required=True)
  tableId = messages.StringField(3, required=True)


class BigqueryTablesDeleteResponse(messages.Message):
  """An empty BigqueryTablesDelete response."""


class BigqueryTablesGetRequest(messages.Message):
  """A BigqueryTablesGetRequest object.

  Fields:
    datasetId: Dataset ID of the requested table
    projectId: Project ID of the requested table
    tableId: Table ID of the requested table
  """

  datasetId = messages.StringField(1, required=True)
  projectId = messages.StringField(2, required=True)
  tableId = messages.StringField(3, required=True)


class BigqueryTablesInsertRequest(messages.Message):
  """A BigqueryTablesInsertRequest object.

  Fields:
    datasetId: Dataset ID of the new table
    projectId: Project ID of the new table
    table: A Table resource to be passed as the request body.
  """

  datasetId = messages.StringField(1, required=True)
  projectId = messages.StringField(2, required=True)
  table = messages.MessageField('Table', 3)


class BigqueryTablesListRequest(messages.Message):
  """A BigqueryTablesListRequest object.

  Fields:
    datasetId: Dataset ID of the tables to list
    maxResults: Maximum number of results to return
    pageToken: Page token, returned by a previous call, to request the next
      page of results
    projectId: Project ID of the tables to list
  """

  datasetId = messages.StringField(1, required=True)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32)
  pageToken = messages.StringField(3)
  projectId = messages.StringField(4, required=True)


class BigqueryTablesPatchRequest(messages.Message):
  """A BigqueryTablesPatchRequest object.

  Fields:
    datasetId: Dataset ID of the table to update
    projectId: Project ID of the table to update
    table: A Table resource to be passed as the request body.
    tableId: Table ID of the table to update
  """

  datasetId = messages.StringField(1, required=True)
  projectId = messages.StringField(2, required=True)
  table = messages.MessageField('Table', 3)
  tableId = messages.StringField(4, required=True)


class BigqueryTablesUpdateRequest(messages.Message):
  """A BigqueryTablesUpdateRequest object.

  Fields:
    datasetId: Dataset ID of the table to update
    projectId: Project ID of the table to update
    table: A Table resource to be passed as the request body.
    tableId: Table ID of the table to update
  """

  datasetId = messages.StringField(1, required=True)
  projectId = messages.StringField(2, required=True)
  table = messages.MessageField('Table', 3)
  tableId = messages.StringField(4, required=True)


class Dataset(messages.Message):
  """A Dataset object.

  Messages:
    AccessValueListEntry: A AccessValueListEntry object.

  Fields:
    access: [Optional] An array of objects that define dataset access for one
      or more entities. You can set this property when inserting or updating a
      dataset in order to control who is allowed to access the data. If
      unspecified at dataset creation time, BigQuery adds default dataset
      access for the following entities: access.specialGroup: projectReaders;
      access.role: READER; access.specialGroup: projectWriters; access.role:
      WRITER; access.specialGroup: projectOwners; access.role: OWNER;
      access.userByEmail: [dataset creator email]; access.role: OWNER;
    creationTime: [Output-only] The time when this dataset was created, in
      milliseconds since the epoch.
    datasetReference: [Required] A reference that identifies the dataset.
    description: [Optional] A user-friendly description of the dataset.
    etag: [Output-only] A hash of the resource.
    friendlyName: [Optional] A descriptive name for the dataset.
    id: [Output-only] The fully-qualified unique name of the dataset in the
      format projectId:datasetId. The dataset name without the project name is
      given in the datasetId field. When creating a new dataset, leave this
      field blank, and instead specify the datasetId field.
    kind: [Output-only] The resource type.
    lastModifiedTime: [Output-only] The date when this dataset or any of its
      tables was last modified, in milliseconds since the epoch.
    selfLink: [Output-only] A URL that can be used to access the resource
      again. You can use this URL in Get or Update requests to the resource.
  """

  class AccessValueListEntry(messages.Message):
    """A AccessValueListEntry object.

    Fields:
      domain: [Pick one] A domain to grant access to. Any users signed in with
        the domain specified will be granted the specified access. Example:
        "example.com".
      groupByEmail: [Pick one] An email address of a Google Group to grant
        access to.
      role: [Required] Describes the rights granted to the user specified by
        the other member of the access object. The following string values are
        supported: READER, WRITER, OWNER.
      specialGroup: [Pick one] A special group to grant access to. Possible
        values include: projectOwners: Owners of the enclosing project.
        projectReaders: Readers of the enclosing project. projectWriters:
        Writers of the enclosing project. allAuthenticatedUsers: All
        authenticated BigQuery users.
      userByEmail: [Pick one] An email address of a user to grant access to.
        For example: fred@example.com.
      view: [Pick one] A view from a different dataset to grant access to.
        Queries executed against that view will have read access to tables in
        this dataset. The role field is not required when this field is set.
        If that view is updated by any user, access to the view needs to be
        granted again via an update operation.
    """

    domain = messages.StringField(1)
    groupByEmail = messages.StringField(2)
    role = messages.StringField(3)
    specialGroup = messages.StringField(4)
    userByEmail = messages.StringField(5)
    view = messages.MessageField('TableReference', 6)

  access = messages.MessageField('AccessValueListEntry', 1, repeated=True)
  creationTime = messages.IntegerField(2)
  datasetReference = messages.MessageField('DatasetReference', 3)
  description = messages.StringField(4)
  etag = messages.StringField(5)
  friendlyName = messages.StringField(6)
  id = messages.StringField(7)
  kind = messages.StringField(8, default=u'bigquery#dataset')
  lastModifiedTime = messages.IntegerField(9)
  selfLink = messages.StringField(10)


class DatasetList(messages.Message):
  """A DatasetList object.

  Messages:
    DatasetsValueListEntry: A DatasetsValueListEntry object.

  Fields:
    datasets: An array of the dataset resources in the project. Each resource
      contains basic information. For full information about a particular
      dataset resource, use the Datasets: get method. This property is omitted
      when there are no datasets in the project.
    etag: A hash value of the results page. You can use this property to
      determine if the page has changed since the last request.
    kind: The list type. This property always returns the value
      "bigquery#datasetList".
    nextPageToken: A token that can be used to request the next results page.
      This property is omitted on the final results page.
  """

  class DatasetsValueListEntry(messages.Message):
    """A DatasetsValueListEntry object.

    Fields:
      datasetReference: The dataset reference. Use this property to access
        specific parts of the dataset's ID, such as project ID or dataset ID.
      friendlyName: A descriptive name for the dataset, if one exists.
      id: The fully-qualified, unique, opaque ID of the dataset.
      kind: The resource type. This property always returns the value
        "bigquery#dataset".
    """

    datasetReference = messages.MessageField('DatasetReference', 1)
    friendlyName = messages.StringField(2)
    id = messages.StringField(3)
    kind = messages.StringField(4, default=u'bigquery#dataset')

  datasets = messages.MessageField('DatasetsValueListEntry', 1, repeated=True)
  etag = messages.StringField(2)
  kind = messages.StringField(3, default=u'bigquery#datasetList')
  nextPageToken = messages.StringField(4)


class DatasetReference(messages.Message):
  """A DatasetReference object.

  Fields:
    datasetId: [Required] A unique ID for this dataset, without the project
      name. The ID must contain only letters (a-z, A-Z), numbers (0-9), or
      underscores (_). The maximum length is 1,024 characters.
    projectId: [Optional] The ID of the project containing this dataset.
  """

  datasetId = messages.StringField(1)
  projectId = messages.StringField(2)


class ErrorProto(messages.Message):
  """A ErrorProto object.

  Fields:
    debugInfo: Debugging information. This property is internal to Google and
      should not be used.
    location: Specifies where the error occurred, if present.
    message: A human-readable description of the error.
    reason: A short error code that summarizes the error.
  """

  debugInfo = messages.StringField(1)
  location = messages.StringField(2)
  message = messages.StringField(3)
  reason = messages.StringField(4)


class GetQueryResultsResponse(messages.Message):
  """A GetQueryResultsResponse object.

  Fields:
    cacheHit: Whether the query result was fetched from the query cache.
    etag: A hash of this response.
    jobComplete: Whether the query has completed or not. If rows or totalRows
      are present, this will always be true. If this is false, totalRows will
      not be available.
    jobReference: Reference to the BigQuery Job that was created to run the
      query. This field will be present even if the original request timed
      out, in which case GetQueryResults can be used to read the results once
      the query has completed. Since this API only returns the first page of
      results, subsequent pages can be fetched via the same mechanism
      (GetQueryResults).
    kind: The resource type of the response.
    pageToken: A token used for paging results.
    rows: An object with as many results as can be contained within the
      maximum permitted reply size. To get any additional rows, you can call
      GetQueryResults and specify the jobReference returned above. Present
      only when the query completes successfully.
    schema: The schema of the results. Present only when the query completes
      successfully.
    totalBytesProcessed: The total number of bytes processed for this query.
    totalRows: The total number of rows in the complete query result set,
      which can be more than the number of rows in this single page of
      results. Present only when the query completes successfully.
  """

  cacheHit = messages.BooleanField(1)
  etag = messages.StringField(2)
  jobComplete = messages.BooleanField(3)
  jobReference = messages.MessageField('JobReference', 4)
  kind = messages.StringField(5, default=u'bigquery#getQueryResultsResponse')
  pageToken = messages.StringField(6)
  rows = messages.MessageField('TableRow', 7, repeated=True)
  schema = messages.MessageField('TableSchema', 8)
  totalBytesProcessed = messages.IntegerField(9)
  totalRows = messages.IntegerField(10, variant=messages.Variant.UINT64)


class Job(messages.Message):
  """A Job object.

  Fields:
    configuration: [Required] Describes the job configuration.
    etag: [Output-only] A hash of this resource.
    id: [Output-only] Opaque ID field of the job
    jobReference: [Optional] Reference describing the unique-per-user name of
      the job.
    kind: [Output-only] The type of the resource.
    selfLink: [Output-only] A URL that can be used to access this resource
      again.
    statistics: [Output-only] Information about the job, including starting
      time and ending time of the job.
    status: [Output-only] The status of this job. Examine this value when
      polling an asynchronous job to see if the job is complete.
  """

  configuration = messages.MessageField('JobConfiguration', 1)
  etag = messages.StringField(2)
  id = messages.StringField(3)
  jobReference = messages.MessageField('JobReference', 4)
  kind = messages.StringField(5, default=u'bigquery#job')
  selfLink = messages.StringField(6)
  statistics = messages.MessageField('JobStatistics', 7)
  status = messages.MessageField('JobStatus', 8)


class JobConfiguration(messages.Message):
  """A JobConfiguration object.

  Fields:
    copy: [Pick one] Copies a table.
    dryRun: [Optional] If set, don't actually run this job. A valid query will
      return a mostly empty response with some processing statistics, while an
      invalid query will return the same error it would if it wasn't a dry
      run. Behavior of non-query jobs is undefined.
    extract: [Pick one] Configures an extract job.
    link: [Pick one] Configures a link job.
    load: [Pick one] Configures a load job.
    query: [Pick one] Configures a query job.
  """

  copy = messages.MessageField('JobConfigurationTableCopy', 1)
  dryRun = messages.BooleanField(2)
  extract = messages.MessageField('JobConfigurationExtract', 3)
  link = messages.MessageField('JobConfigurationLink', 4)
  load = messages.MessageField('JobConfigurationLoad', 5)
  query = messages.MessageField('JobConfigurationQuery', 6)


class JobConfigurationExtract(messages.Message):
  """A JobConfigurationExtract object.

  Fields:
    compression: [Optional] The compression type to use for exported files.
      Possible values include GZIP and NONE. The default value is NONE.
    destinationFormat: [Optional] The exported file format. Possible values
      include CSV, NEWLINE_DELIMITED_JSON and AVRO. The default value is CSV.
      Tables with nested or repeated fields cannot be exported as CSV.
    destinationUri: [Pick one] DEPRECATED: Use destinationUris instead,
      passing only one URI as necessary. The fully-qualified Google Cloud
      Storage URI where the extracted table should be written.
    destinationUris: [Pick one] A list of fully-qualified Google Cloud Storage
      URIs where the extracted table should be written.
    fieldDelimiter: [Optional] Delimiter to use between fields in the exported
      data. Default is ','
    printHeader: [Optional] Whether to print out a header row in the results.
      Default is true.
    sourceTable: [Required] A reference to the table being exported.
  """

  compression = messages.StringField(1)
  destinationFormat = messages.StringField(2)
  destinationUri = messages.StringField(3)
  destinationUris = messages.StringField(4, repeated=True)
  fieldDelimiter = messages.StringField(5)
  printHeader = messages.BooleanField(6)
  sourceTable = messages.MessageField('TableReference', 7)


class JobConfigurationLink(messages.Message):
  """A JobConfigurationLink object.

  Fields:
    createDisposition: [Optional] Specifies whether the job is allowed to
      create new tables. The following values are supported: CREATE_IF_NEEDED:
      If the table does not exist, BigQuery creates the table. CREATE_NEVER:
      The table must already exist. If it does not, a 'notFound' error is
      returned in the job result. The default value is CREATE_IF_NEEDED.
      Creation, truncation and append actions occur as one atomic update upon
      job completion.
    destinationTable: [Required] The destination table of the link job.
    sourceUri: [Required] URI of source table to link.
    writeDisposition: [Optional] Specifies the action that occurs if the
      destination table already exists. The following values are supported:
      WRITE_TRUNCATE: If the table already exists, BigQuery overwrites the
      table data. WRITE_APPEND: If the table already exists, BigQuery appends
      the data to the table. WRITE_EMPTY: If the table already exists and
      contains data, a 'duplicate' error is returned in the job result. The
      default value is WRITE_EMPTY. Each action is atomic and only occurs if
      BigQuery is able to complete the job successfully. Creation, truncation
      and append actions occur as one atomic update upon job completion.
  """

  createDisposition = messages.StringField(1)
  destinationTable = messages.MessageField('TableReference', 2)
  sourceUri = messages.StringField(3, repeated=True)
  writeDisposition = messages.StringField(4)


class JobConfigurationLoad(messages.Message):
  """A JobConfigurationLoad object.

  Fields:
    allowJaggedRows: [Optional] Accept rows that are missing trailing optional
      columns. The missing values are treated as nulls. Default is false which
      treats short rows as errors. Only applicable to CSV, ignored for other
      formats.
    allowQuotedNewlines: Indicates if BigQuery should allow quoted data
      sections that contain newline characters in a CSV file. The default
      value is false.
    createDisposition: [Optional] Specifies whether the job is allowed to
      create new tables. The following values are supported: CREATE_IF_NEEDED:
      If the table does not exist, BigQuery creates the table. CREATE_NEVER:
      The table must already exist. If it does not, a 'notFound' error is
      returned in the job result. The default value is CREATE_IF_NEEDED.
      Creation, truncation and append actions occur as one atomic update upon
      job completion.
    destinationTable: [Required] The destination table to load the data into.
    encoding: [Optional] The character encoding of the data. The supported
      values are UTF-8 or ISO-8859-1. The default value is UTF-8. BigQuery
      decodes the data after the raw, binary data has been split using the
      values of the quote and fieldDelimiter properties.
    fieldDelimiter: [Optional] The separator for fields in a CSV file.
      BigQuery converts the string to ISO-8859-1 encoding, and then uses the
      first byte of the encoded string to split the data in its raw, binary
      state. BigQuery also supports the escape sequence "\t" to specify a tab
      separator. The default value is a comma (',').
    ignoreUnknownValues: [Optional] Accept rows that contain values that do
      not match the schema. The unknown values are ignored. Default is false
      which treats unknown values as errors. For CSV this ignores extra values
      at the end of a line. For JSON this ignores named values that do not
      match any column name.
    maxBadRecords: [Optional] The maximum number of bad records that BigQuery
      can ignore when running the job. If the number of bad records exceeds
      this value, an 'invalid' error is returned in the job result and the job
      fails. The default value is 0, which requires that all records are
      valid.
    quote: [Optional] The value that is used to quote data sections in a CSV
      file. BigQuery converts the string to ISO-8859-1 encoding, and then uses
      the first byte of the encoded string to split the data in its raw,
      binary state. The default value is a double-quote ('"'). If your data
      does not contain quoted sections, set the property value to an empty
      string. If your data contains quoted newline characters, you must also
      set the allowQuotedNewlines property to true.
    schema: [Optional] The schema for the destination table. The schema can be
      omitted if the destination table already exists or if the schema can be
      inferred from the loaded data.
    schemaInline: [Deprecated] The inline schema. For CSV schemas, specify as
      "Field1:Type1[,Field2:Type2]*". For example, "foo:STRING, bar:INTEGER,
      baz:FLOAT".
    schemaInlineFormat: [Deprecated] The format of the schemaInline property.
    skipLeadingRows: [Optional] The number of rows at the top of a CSV file
      that BigQuery will skip when loading the data. The default value is 0.
      This property is useful if you have header rows in the file that should
      be skipped.
    sourceFormat: [Optional] The format of the data files. For CSV files,
      specify "CSV". For datastore backups, specify "DATASTORE_BACKUP". For
      newline-delimited JSON, specify "NEWLINE_DELIMITED_JSON". The default
      value is CSV.
    sourceUris: [Required] The fully-qualified URIs that point to your data in
      Google Cloud Storage. Wildcard names are only supported when they appear
      at the end of the URI.
    writeDisposition: [Optional] Specifies the action that occurs if the
      destination table already exists. The following values are supported:
      WRITE_TRUNCATE: If the table already exists, BigQuery overwrites the
      table data. WRITE_APPEND: If the table already exists, BigQuery appends
      the data to the table. WRITE_EMPTY: If the table already exists and
      contains data, a 'duplicate' error is returned in the job result. The
      default value is WRITE_EMPTY. Each action is atomic and only occurs if
      BigQuery is able to complete the job successfully. Creation, truncation
      and append actions occur as one atomic update upon job completion.
  """

  allowJaggedRows = messages.BooleanField(1)
  allowQuotedNewlines = messages.BooleanField(2)
  createDisposition = messages.StringField(3)
  destinationTable = messages.MessageField('TableReference', 4)
  encoding = messages.StringField(5)
  fieldDelimiter = messages.StringField(6)
  ignoreUnknownValues = messages.BooleanField(7)
  maxBadRecords = messages.IntegerField(8, variant=messages.Variant.INT32)
  quote = messages.StringField(9)
  schema = messages.MessageField('TableSchema', 10)
  schemaInline = messages.StringField(11)
  schemaInlineFormat = messages.StringField(12)
  skipLeadingRows = messages.IntegerField(13, variant=messages.Variant.INT32)
  sourceFormat = messages.StringField(14)
  sourceUris = messages.StringField(15, repeated=True)
  writeDisposition = messages.StringField(16)


class JobConfigurationQuery(messages.Message):
  """A JobConfigurationQuery object.

  Fields:
    allowLargeResults: If true, allows the query to produce arbitrarily large
      result tables at a slight cost in performance. Requires destinationTable
      to be set.
    createDisposition: [Optional] Specifies whether the job is allowed to
      create new tables. The following values are supported: CREATE_IF_NEEDED:
      If the table does not exist, BigQuery creates the table. CREATE_NEVER:
      The table must already exist. If it does not, a 'notFound' error is
      returned in the job result. The default value is CREATE_IF_NEEDED.
      Creation, truncation and append actions occur as one atomic update upon
      job completion.
    defaultDataset: [Optional] Specifies the default dataset to use for
      unqualified table names in the query.
    destinationTable: [Optional] Describes the table where the query results
      should be stored. If not present, a new table will be created to store
      the results.
    flattenResults: [Experimental] Flattens all nested and repeated fields in
      the query results. The default value is true. allowLargeResults must be
      true if this is set to false.
    preserveNulls: [Deprecated] This property is deprecated.
    priority: [Optional] Specifies a priority for the query. Possible values
      include INTERACTIVE and BATCH. The default value is INTERACTIVE.
    query: [Required] BigQuery SQL query to execute.
    useQueryCache: [Optional] Whether to look for the result in the query
      cache. The query cache is a best-effort cache that will be flushed
      whenever tables in the query are modified. Moreover, the query cache is
      only available when a query does not have a destination table specified.
    writeDisposition: [Optional] Specifies the action that occurs if the
      destination table already exists. The following values are supported:
      WRITE_TRUNCATE: If the table already exists, BigQuery overwrites the
      table data. WRITE_APPEND: If the table already exists, BigQuery appends
      the data to the table. WRITE_EMPTY: If the table already exists and
      contains data, a 'duplicate' error is returned in the job result. The
      default value is WRITE_EMPTY. Each action is atomic and only occurs if
      BigQuery is able to complete the job successfully. Creation, truncation
      and append actions occur as one atomic update upon job completion.
  """

  allowLargeResults = messages.BooleanField(1)
  createDisposition = messages.StringField(2)
  defaultDataset = messages.MessageField('DatasetReference', 3)
  destinationTable = messages.MessageField('TableReference', 4)
  flattenResults = messages.BooleanField(5)
  preserveNulls = messages.BooleanField(6)
  priority = messages.StringField(7)
  query = messages.StringField(8)
  useQueryCache = messages.BooleanField(9)
  writeDisposition = messages.StringField(10)


class JobConfigurationTableCopy(messages.Message):
  """A JobConfigurationTableCopy object.

  Fields:
    createDisposition: [Optional] Specifies whether the job is allowed to
      create new tables. The following values are supported: CREATE_IF_NEEDED:
      If the table does not exist, BigQuery creates the table. CREATE_NEVER:
      The table must already exist. If it does not, a 'notFound' error is
      returned in the job result. The default value is CREATE_IF_NEEDED.
      Creation, truncation and append actions occur as one atomic update upon
      job completion.
    destinationTable: [Required] The destination table
    sourceTable: [Pick one] Source table to copy.
    sourceTables: [Pick one] Source tables to copy.
    writeDisposition: [Optional] Specifies the action that occurs if the
      destination table already exists. The following values are supported:
      WRITE_TRUNCATE: If the table already exists, BigQuery overwrites the
      table data. WRITE_APPEND: If the table already exists, BigQuery appends
      the data to the table. WRITE_EMPTY: If the table already exists and
      contains data, a 'duplicate' error is returned in the job result. The
      default value is WRITE_EMPTY. Each action is atomic and only occurs if
      BigQuery is able to complete the job successfully. Creation, truncation
      and append actions occur as one atomic update upon job completion.
  """

  createDisposition = messages.StringField(1)
  destinationTable = messages.MessageField('TableReference', 2)
  sourceTable = messages.MessageField('TableReference', 3)
  sourceTables = messages.MessageField('TableReference', 4, repeated=True)
  writeDisposition = messages.StringField(5)


class JobList(messages.Message):
  """A JobList object.

  Messages:
    JobsValueListEntry: A JobsValueListEntry object.

  Fields:
    etag: A hash of this page of results.
    jobs: List of jobs that were requested.
    kind: The resource type of the response.
    nextPageToken: A token to request the next page of results.
    totalItems: Total number of jobs in this collection.
  """

  class JobsValueListEntry(messages.Message):
    """A JobsValueListEntry object.

    Fields:
      configuration: [Full-projection-only] Specifies the job configuration.
      errorResult: A result object that will be present only if the job has
        failed.
      id: Unique opaque ID of the job.
      jobReference: Job reference uniquely identifying the job.
      kind: The resource type.
      state: Running state of the job. When the state is DONE, errorResult can
        be checked to determine whether the job succeeded or failed.
      statistics: [Output-only] Information about the job, including starting
        time and ending time of the job.
      status: [Full-projection-only] Describes the state of the job.
      user_email: [Full-projection-only] User who ran the job.
    """

    configuration = messages.MessageField('JobConfiguration', 1)
    errorResult = messages.MessageField('ErrorProto', 2)
    id = messages.StringField(3)
    jobReference = messages.MessageField('JobReference', 4)
    kind = messages.StringField(5, default=u'bigquery#job')
    state = messages.StringField(6)
    statistics = messages.MessageField('JobStatistics', 7)
    status = messages.MessageField('JobStatus', 8)
    user_email = messages.StringField(9)

  etag = messages.StringField(1)
  jobs = messages.MessageField('JobsValueListEntry', 2, repeated=True)
  kind = messages.StringField(3, default=u'bigquery#jobList')
  nextPageToken = messages.StringField(4)
  totalItems = messages.IntegerField(5, variant=messages.Variant.INT32)


class JobReference(messages.Message):
  """A JobReference object.

  Fields:
    jobId: [Required] The ID of the job. The ID must contain only letters
      (a-z, A-Z), numbers (0-9), underscores (_), or dashes (-). The maximum
      length is 1,024 characters.
    projectId: [Required] The ID of the project containing this job.
  """

  jobId = messages.StringField(1)
  projectId = messages.StringField(2)


class JobStatistics(messages.Message):
  """A JobStatistics object.

  Fields:
    creationTime: [Output-only] Creation time of this job, in milliseconds
      since the epoch. This field will be present on all jobs.
    endTime: [Output-only] End time of this job, in milliseconds since the
      epoch. This field will be present whenever a job is in the DONE state.
    extract: [Output-only] Statistics for an extract job.
    load: [Output-only] Statistics for a load job.
    query: [Output-only] Statistics for a query job.
    startTime: [Output-only] Start time of this job, in milliseconds since the
      epoch. This field will be present when the job transitions from the
      PENDING state to either RUNNING or DONE.
    totalBytesProcessed: [Output-only] [Deprecated] Use the bytes processed in
      the query statistics instead.
  """

  creationTime = messages.IntegerField(1)
  endTime = messages.IntegerField(2)
  extract = messages.MessageField('JobStatistics4', 3)
  load = messages.MessageField('JobStatistics3', 4)
  query = messages.MessageField('JobStatistics2', 5)
  startTime = messages.IntegerField(6)
  totalBytesProcessed = messages.IntegerField(7)


class JobStatistics2(messages.Message):
  """A JobStatistics2 object.

  Fields:
    cacheHit: [Output-only] Whether the query result was fetched from the
      query cache.
    totalBytesProcessed: [Output-only] Total bytes processed for this job.
  """

  cacheHit = messages.BooleanField(1)
  totalBytesProcessed = messages.IntegerField(2)


class JobStatistics3(messages.Message):
  """A JobStatistics3 object.

  Fields:
    inputFileBytes: [Output-only] Number of bytes of source data in a joad
      job.
    inputFiles: [Output-only] Number of source files in a load job.
    outputBytes: [Output-only] Size of the loaded data in bytes. Note that
      while an import job is in the running state, this value may change.
    outputRows: [Output-only] Number of rows imported in a load job. Note that
      while an import job is in the running state, this value may change.
  """

  inputFileBytes = messages.IntegerField(1)
  inputFiles = messages.IntegerField(2)
  outputBytes = messages.IntegerField(3)
  outputRows = messages.IntegerField(4)


class JobStatistics4(messages.Message):
  """A JobStatistics4 object.

  Fields:
    destinationUriFileCounts: [Experimental] Number of files per destination
      URI or URI pattern specified in the extract configuration. These values
      will be in the same order as the URIs specified in the 'destinationUris'
      field.
  """

  destinationUriFileCounts = messages.IntegerField(1, repeated=True)


class JobStatus(messages.Message):
  """A JobStatus object.

  Fields:
    errorResult: [Output-only] Final error result of the job. If present,
      indicates that the job has completed and was unsuccessful.
    errors: [Output-only] All errors encountered during the running of the
      job. Errors here do not necessarily mean that the job has completed or
      was unsuccessful.
    state: [Output-only] Running state of the job.
  """

  errorResult = messages.MessageField('ErrorProto', 1)
  errors = messages.MessageField('ErrorProto', 2, repeated=True)
  state = messages.StringField(3)


@encoding.MapUnrecognizedFields('additionalProperties')
class JsonObject(messages.Message):
  """Represents a single JSON object.

  Messages:
    AdditionalProperty: An additional property for a JsonObject object.

  Fields:
    additionalProperties: Additional properties of type JsonObject
  """

  class AdditionalProperty(messages.Message):
    """An additional property for a JsonObject object.

    Fields:
      key: Name of the additional property.
      value: A JsonValue attribute.
    """

    key = messages.StringField(1)
    value = messages.MessageField('JsonValue', 2)

  additionalProperties = messages.MessageField('AdditionalProperty', 1, repeated=True)


JsonValue = extra_types.JsonValue


class ProjectList(messages.Message):
  """A ProjectList object.

  Messages:
    ProjectsValueListEntry: A ProjectsValueListEntry object.

  Fields:
    etag: A hash of the page of results
    kind: The type of list.
    nextPageToken: A token to request the next page of results.
    projects: Projects to which you have at least READ access.
    totalItems: The total number of projects in the list.
  """

  class ProjectsValueListEntry(messages.Message):
    """A ProjectsValueListEntry object.

    Fields:
      friendlyName: A descriptive name for this project.
      id: An opaque ID of this project.
      kind: The resource type.
      numericId: The numeric ID of this project.
      projectReference: A unique reference to this project.
    """

    friendlyName = messages.StringField(1)
    id = messages.StringField(2)
    kind = messages.StringField(3, default=u'bigquery#project')
    numericId = messages.IntegerField(4, variant=messages.Variant.UINT64)
    projectReference = messages.MessageField('ProjectReference', 5)

  etag = messages.StringField(1)
  kind = messages.StringField(2, default=u'bigquery#projectList')
  nextPageToken = messages.StringField(3)
  projects = messages.MessageField('ProjectsValueListEntry', 4, repeated=True)
  totalItems = messages.IntegerField(5, variant=messages.Variant.INT32)


class ProjectReference(messages.Message):
  """A ProjectReference object.

  Fields:
    projectId: [Required] ID of the project. Can be either the numeric ID or
      the assigned ID of the project.
  """

  projectId = messages.StringField(1)


class QueryRequest(messages.Message):
  """A QueryRequest object.

  Fields:
    defaultDataset: [Optional] Specifies the default datasetId and projectId
      to assume for any unqualified table names in the query. If not set, all
      table names in the query string must be qualified in the format
      'datasetId.tableId'.
    dryRun: [Optional] If set, don't actually run the query. A valid query
      will return an empty response, while an invalid query will return the
      same error it would if it wasn't a dry run. The default value is false.
    kind: The resource type of the request.
    maxResults: [Optional] The maximum number of rows of data to return per
      page of results. Setting this flag to a small value such as 1000 and
      then paging through results might improve reliability when the query
      result set is large. In addition to this limit, responses are also
      limited to 10 MB. By default, there is no maximum row count, and only
      the byte limit applies.
    preserveNulls: [Deprecated] This property is deprecated.
    query: [Required] A query string, following the BigQuery query syntax, of
      the query to execute. Example: "SELECT count(f1) FROM
      [myProjectId:myDatasetId.myTableId]".
    timeoutMs: [Optional] How long to wait for the query to complete, in
      milliseconds, before the request times out and returns. Note that this
      is only a timeout for the request, not the query. If the query takes
      longer to run than the timeout value, the call returns without any
      results and with the 'jobComplete' flag set to false. You can call
      GetQueryResults() to wait for the query to complete and read the
      results. The default value is 10000 milliseconds (10 seconds).
    useQueryCache: [Optional] Whether to look for the result in the query
      cache. The query cache is a best-effort cache that will be flushed
      whenever tables in the query are modified. The default value is true.
  """

  defaultDataset = messages.MessageField('DatasetReference', 1)
  dryRun = messages.BooleanField(2)
  kind = messages.StringField(3, default=u'bigquery#queryRequest')
  maxResults = messages.IntegerField(4, variant=messages.Variant.UINT32)
  preserveNulls = messages.BooleanField(5)
  query = messages.StringField(6)
  timeoutMs = messages.IntegerField(7, variant=messages.Variant.UINT32)
  useQueryCache = messages.BooleanField(8)


class QueryResponse(messages.Message):
  """A QueryResponse object.

  Fields:
    cacheHit: Whether the query result was fetched from the query cache.
    jobComplete: Whether the query has completed or not. If rows or totalRows
      are present, this will always be true. If this is false, totalRows will
      not be available.
    jobReference: Reference to the Job that was created to run the query. This
      field will be present even if the original request timed out, in which
      case GetQueryResults can be used to read the results once the query has
      completed. Since this API only returns the first page of results,
      subsequent pages can be fetched via the same mechanism
      (GetQueryResults).
    kind: The resource type.
    pageToken: A token used for paging results.
    rows: An object with as many results as can be contained within the
      maximum permitted reply size. To get any additional rows, you can call
      GetQueryResults and specify the jobReference returned above.
    schema: The schema of the results. Present only when the query completes
      successfully.
    totalBytesProcessed: The total number of bytes processed for this query.
      If this query was a dry run, this is the number of bytes that would be
      processed if the query were run.
    totalRows: The total number of rows in the complete query result set,
      which can be more than the number of rows in this single page of
      results.
  """

  cacheHit = messages.BooleanField(1)
  jobComplete = messages.BooleanField(2)
  jobReference = messages.MessageField('JobReference', 3)
  kind = messages.StringField(4, default=u'bigquery#queryResponse')
  pageToken = messages.StringField(5)
  rows = messages.MessageField('TableRow', 6, repeated=True)
  schema = messages.MessageField('TableSchema', 7)
  totalBytesProcessed = messages.IntegerField(8)
  totalRows = messages.IntegerField(9, variant=messages.Variant.UINT64)


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
      csv: Responses with Content-Type of text/csv
      json: Responses with Content-Type of application/json
    """
    csv = 0
    json = 1

  alt = messages.EnumField('AltValueValuesEnum', 1, default=u'json')
  fields = messages.StringField(2)
  key = messages.StringField(3)
  oauth_token = messages.StringField(4)
  prettyPrint = messages.BooleanField(5, default=True)
  quotaUser = messages.StringField(6)
  trace = messages.StringField(7)
  userIp = messages.StringField(8)


class Table(messages.Message):
  """A Table object.

  Fields:
    creationTime: [Output-only] The time when this table was created, in
      milliseconds since the epoch.
    description: [Optional] A user-friendly description of this table.
    etag: [Output-only] A hash of this resource.
    expirationTime: [Optional] The time when this table expires, in
      milliseconds since the epoch. If not present, the table will persist
      indefinitely. Expired tables will be deleted and their storage
      reclaimed.
    friendlyName: [Optional] A descriptive name for this table.
    id: [Output-only] An opaque ID uniquely identifying the table.
    kind: [Output-only] The type of the resource.
    lastModifiedTime: [Output-only] The time when this table was last
      modified, in milliseconds since the epoch.
    numBytes: [Output-only] The size of the table in bytes. This property is
      unavailable for tables that are actively receiving streaming inserts.
    numRows: [Output-only] The number of rows of data in this table. This
      property is unavailable for tables that are actively receiving streaming
      inserts.
    schema: [Optional] Describes the schema of this table.
    selfLink: [Output-only] A URL that can be used to access this resource
      again.
    tableReference: [Required] Reference describing the ID of this table.
    type: [Output-only] Describes the table type. The following values are
      supported: TABLE: A normal BigQuery table. VIEW: A virtual table defined
      by a SQL query. The default value is TABLE.
    view: [Optional] The view definition.
  """

  creationTime = messages.IntegerField(1)
  description = messages.StringField(2)
  etag = messages.StringField(3)
  expirationTime = messages.IntegerField(4)
  friendlyName = messages.StringField(5)
  id = messages.StringField(6)
  kind = messages.StringField(7, default=u'bigquery#table')
  lastModifiedTime = messages.IntegerField(8)
  numBytes = messages.IntegerField(9)
  numRows = messages.IntegerField(10, variant=messages.Variant.UINT64)
  schema = messages.MessageField('TableSchema', 11)
  selfLink = messages.StringField(12)
  tableReference = messages.MessageField('TableReference', 13)
  type = messages.StringField(14)
  view = messages.MessageField('ViewDefinition', 15)


class TableCell(messages.Message):
  """Represents a single cell in the result set. Users of the java client can
  detect whether their value result is null by calling
  'com.google.api.client.util.Data.isNull(cell.getV())'.

  Fields:
    v: A extra_types.JsonValue attribute.
  """

  v = messages.MessageField('extra_types.JsonValue', 1)


class TableDataInsertAllRequest(messages.Message):
  """A TableDataInsertAllRequest object.

  Messages:
    RowsValueListEntry: A RowsValueListEntry object.

  Fields:
    kind: The resource type of the response.
    rows: The rows to insert.
  """

  class RowsValueListEntry(messages.Message):
    """A RowsValueListEntry object.

    Fields:
      insertId: [Optional] A unique ID for each row. BigQuery uses this
        property to detect duplicate insertion requests on a best-effort
        basis.
      json: [Required] A JSON object that contains a row of data. The object's
        properties and values must match the destination table's schema.
    """

    insertId = messages.StringField(1)
    json = messages.MessageField('JsonObject', 2)

  kind = messages.StringField(1, default=u'bigquery#tableDataInsertAllRequest')
  rows = messages.MessageField('RowsValueListEntry', 2, repeated=True)


class TableDataInsertAllResponse(messages.Message):
  """A TableDataInsertAllResponse object.

  Messages:
    InsertErrorsValueListEntry: A InsertErrorsValueListEntry object.

  Fields:
    insertErrors: An array of errors for rows that were not inserted.
    kind: The resource type of the response.
  """

  class InsertErrorsValueListEntry(messages.Message):
    """A InsertErrorsValueListEntry object.

    Fields:
      errors: Error information for the row indicated by the index property.
      index: The index of the row that error applies to.
    """

    errors = messages.MessageField('ErrorProto', 1, repeated=True)
    index = messages.IntegerField(2, variant=messages.Variant.UINT32)

  insertErrors = messages.MessageField('InsertErrorsValueListEntry', 1, repeated=True)
  kind = messages.StringField(2, default=u'bigquery#tableDataInsertAllResponse')


class TableDataList(messages.Message):
  """A TableDataList object.

  Fields:
    etag: A hash of this page of results.
    kind: The resource type of the response.
    pageToken: A token used for paging results. Providing this token instead
      of the startIndex parameter can help you retrieve stable results when an
      underlying table is changing.
    rows: Rows of results.
    totalRows: The total number of rows in the complete table.
  """

  etag = messages.StringField(1)
  kind = messages.StringField(2, default=u'bigquery#tableDataList')
  pageToken = messages.StringField(3)
  rows = messages.MessageField('TableRow', 4, repeated=True)
  totalRows = messages.IntegerField(5)


class TableFieldSchema(messages.Message):
  """A TableFieldSchema object.

  Fields:
    description: [Optional] The field description. The maximum length is 16K
      characters.
    fields: [Optional] Describes the nested schema fields if the type property
      is set to RECORD.
    mode: [Optional] The field mode. Possible values include NULLABLE,
      REQUIRED and REPEATED. The default value is NULLABLE.
    name: [Required] The field name. The name must contain only letters (a-z,
      A-Z), numbers (0-9), or underscores (_), and must start with a letter or
      underscore. The maximum length is 128 characters.
    type: [Required] The field data type. Possible values include STRING,
      INTEGER, FLOAT, BOOLEAN, TIMESTAMP or RECORD (where RECORD indicates
      that the field contains a nested schema).
  """

  description = messages.StringField(1)
  fields = messages.MessageField('TableFieldSchema', 2, repeated=True)
  mode = messages.StringField(3)
  name = messages.StringField(4)
  type = messages.StringField(5)


class TableList(messages.Message):
  """A TableList object.

  Messages:
    TablesValueListEntry: A TablesValueListEntry object.

  Fields:
    etag: A hash of this page of results.
    kind: The type of list.
    nextPageToken: A token to request the next page of results.
    tables: Tables in the requested dataset.
    totalItems: The total number of tables in the dataset.
  """

  class TablesValueListEntry(messages.Message):
    """A TablesValueListEntry object.

    Fields:
      friendlyName: The user-friendly name for this table.
      id: An opaque ID of the table
      kind: The resource type.
      tableReference: A reference uniquely identifying the table.
      type: The type of table. Possible values are: TABLE, VIEW.
    """

    friendlyName = messages.StringField(1)
    id = messages.StringField(2)
    kind = messages.StringField(3, default=u'bigquery#table')
    tableReference = messages.MessageField('TableReference', 4)
    type = messages.StringField(5)

  etag = messages.StringField(1)
  kind = messages.StringField(2, default=u'bigquery#tableList')
  nextPageToken = messages.StringField(3)
  tables = messages.MessageField('TablesValueListEntry', 4, repeated=True)
  totalItems = messages.IntegerField(5, variant=messages.Variant.INT32)


class TableReference(messages.Message):
  """A TableReference object.

  Fields:
    datasetId: [Required] The ID of the dataset containing this table.
    projectId: [Required] The ID of the project containing this table.
    tableId: [Required] The ID of the table. The ID must contain only letters
      (a-z, A-Z), numbers (0-9), or underscores (_). The maximum length is
      1,024 characters.
  """

  datasetId = messages.StringField(1)
  projectId = messages.StringField(2)
  tableId = messages.StringField(3)


class TableRow(messages.Message):
  """Represents a single row in the result set, consisting of one or more
  fields.

  Fields:
    f: A TableCell attribute.
  """

  f = messages.MessageField('TableCell', 1, repeated=True)


class TableSchema(messages.Message):
  """A TableSchema object.

  Fields:
    fields: Describes the fields in a table.
  """

  fields = messages.MessageField('TableFieldSchema', 1, repeated=True)


class ViewDefinition(messages.Message):
  """A ViewDefinition object.

  Fields:
    query: [Required] A query that BigQuery executes when the view is
      referenced.
  """

  query = messages.StringField(1)


