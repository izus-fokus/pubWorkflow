#!/bin/bash
sqlite3 pubworkflow.db "BEGIN TRANSACTION;"
sqlite3 pubworkflow.db "CREATE TABLE run(invocationId varchar(255), runId varchar(255), status varchar(150), datasetId varchar(255), databaseId varchar(255), pumaStatus varchar(255), pumaId varchar(255), postInvocationId varchar(255), workflowStarted TEXT, okFromAuthor TEXT, published TEXT, exportedToBibliography TEXT);"