AWS CLI v2
==========

https://awscli.amazonaws.com/v2/documentation/api/latest/reference/index.html

Maintained at [roberth-k/dash-docset-aws-cli](https://github.com/roberth-k/dash-docset-aws-cli).

The maintainer of the docset is not affiliated with AWS.

## Building the docset

The system must provide the following:

- git
- GNU Make
- Python 3.8

To build the docset, run:

```bash
git clone git@github.com:roberth-k/dash-docset-aws-cli.git
cd dash-docset-aws-cli
make .build/2.0.29/AWS-CLI.tgz
```

Replace `2.0.29` with the version of AWS CLI v2 to compile documentation for. The
list of releases is available in the [official AWS CLI repository](https://github.com/aws/aws-cli).
The docset will be available at `.build/2.0.29/AWS-CLI.docset`, and the compressed
variant at `.build/2.0.29/AWS-CLI.tgz`.
