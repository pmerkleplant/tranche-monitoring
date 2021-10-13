# Tranche Monitoring

A monitoring tool for Buttonwood's tranche contracts, using the [Tranche Subgraph](https://github.com/buttonwood-protocol/subgraph).

This tool is currently in a _demo state_ to explore the exact information to monitor and serve.

The design is obviously to be worked on.

## Setup

This tool runs on Docker.

Run `$ make dev-run` to build and run the tool.

When started succesfully, open the link provided in the docker output.

## Architecture

Currently the monitoring is stateless. All information is fetched from the subgraph and no data is saved (i.e. no historical data can be viewed).
