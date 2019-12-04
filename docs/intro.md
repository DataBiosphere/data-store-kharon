Introduction to Kharon
------------------------

Kharon is a tool for deleting data in the [Data Storage System (DSS)](https://github.com/HumanCellAtlas/data-store),
a component in the [Data Coordination Platform (DCP)](https://github.com/HumanCellAtlas/dcp-community)
of the [Human Cell Atlas (HCA)](https://github.com/HumanCellAtlas) project.

To cover how Kharon works, we first provide an explanation of how deletion of data is handled by the DSS. This is
dictated by a [deletion RFC](https://github.com/HumanCellAtlas/dcp-community/blob/master/rfcs/text/0004-dss-deletion-process.md)
in the [dcp-community repository](https://github.com/HumanCellAtlas/dcp-community) and was driven by the
requirements of the broader HCA.

* Go to the [Deletion](deletion.html) page

Kharon is architected to scale up and handle massive file deletion events. We explain Kharon's cloud
architecture and design and how data flows through it.

* Go to the [Architecture](arch.html) page

Kharon depends on several pieces of software. We cover how to install Kharon and its dependencies.

* Go to the [Installing Kharon](install.html) page

Kharon utilizes multiple cloud components, which must be built, configured, and deployed to the cloud.
We cover how to deploy Kharon resources to the cloud.

* Go to the [Deploying Kharon](deploy.html) page

Now that Kharon's internals have been covered, we move on to performing common operations with Kharon.

* Go to the [Runbook](runbook.html) page

Finally, Kharon performs sensitive operations and must be rigorously tested. In addition, continuous
integration (CI) is used to schedule test builds and facilitate maintenance operations (including both
scheduled operations and manual operations).

* Go to the [Testing](tests.html) page
