Kharon Cloud Architecture
----------------------------

## Deletion Queue

The central idea behind Kharon is the deletion queue.

When items are marked for physical deletion, they are added to the queue. The queue will accumulate items until the
next deletion event is scheduled (approximately daily). When the scheduled deletion event occurs, the AWS SQS queue
processes each item in the queue and creates an event from each item. Those items then trigger lambda functions to
process the items.

Here is the lambda function code that is triggered by SQS queue events:
[`daemons/dds-delete/app.py`](daemons/dds-delete/app.py)

Each SQS event will spawn a lambda function (specifically, a chalice app) whose job is to delete the queue item
passed to it. This model - populating a queue with items, then removing items from the queue and triggering a
lambda function to process the items - enables a massive scale-up of deletion events using a swarm of lambda
functions.

Here is the Kharon delete method, called by the lambda swarm on each queue item:
[`dds/__init__.py`](../dds/__init__.py)

There is one deletion queue per stage.

## Deletion Lists

A deletion list is a list of files that the DSS explicitly wishes to delete. This is typically a file containing
files, bundles, or blobs to mark for physical deletion. No "master" deletion list is stored in the cloud, since
the deletion queue itself can be thought of as the "master" deletion list.

To delete specific items, a deletion list should be used. An operator will use a script to populate the deletion
queue with all items in a deletion list.

**TODO @chmreid: What script do we use, and can we give an example?**

## Inclusion Lists

Just as we mark files for deletion, it is important to mark files for saving. This is the purpose of the
inclusion list, which is stored in the cloud as a DynamoDB table. Any file in this list will always survive
deletion.

Each item in the deletion queue is processed by its own lambda function. That lambda function will compare the
key it is supposed to delete to keys in the inclusion list, and if the file is in the inclusion list, the lambda
function will exit without touching the file. This design ensures the deletion lambda swarm can effectively scale up.

To save specific items from being deleted, the operator will use a script to add items to the inclusion list
that lives in the cloud.

**TODO @chmreid: What script do we use, and can we give an example?**

### Carrying Over Inclusion Lists

When regular deletion events occur, the inclusion list between events does not typically change much.

The DSS team has found it useful to maintain a plain text version of the inclusion list, to make it easier
to repopulate the inclusion list and to control changes to the inclusion list (e.g., with version control).

## Cleanup Operations

Cleanup operations performed for a given stage will delete all files on that stage except those on the inclusion
list. Cleanup operations do not use deletion lists - they add every file and bundle in the stage to the deletion
queue, and delete any files or bundles that are not on the inclusion list.


