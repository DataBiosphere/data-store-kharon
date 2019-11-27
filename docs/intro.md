Introduction to Kharon
------------------------

Kharon is a tool for deleting data in the [Data Storage System (DSS)](https://github.com/HumanCellAtlas/data-store),
a component in the [Data Coordination Platform (DCP)](https://github.com/HumanCellAtlas/dcp-community)
of the [Human Cell Atlas (HCA)](https://github.com/HumanCellAtlas) project.

To cover how Kharon works, we first provide an explanation of how deletion of data is handled by the DSS. This is
dictated by a [deletion RFC](https://github.com/HumanCellAtlas/dcp-community/blob/master/rfcs/text/0004-dss-deletion-process.md)
in the [dcp-community repository](https://github.com/HumanCellAtlas/dcp-community) and was driven by the
requirements of the broader HCA. We cover this on the [deletion](deletion.md) page.

Kharon utilizes several cloud components. We give an overview of the cloud architecture of Kharon and how data
flows through it on the [arch](arch.md) page.

We cover the installation of Kharon and its dependent software components on the [install](install.md) page.

We cover the deployment of Kharon to the cloud on the [deploy](deploy.md) page.

Finally, we cover our test strategy for Kharon on the [test](test.md) page.
