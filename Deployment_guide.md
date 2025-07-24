# Deployment Guide

## Account registration

Register for an account and generate API key with [build.nvidia.com](https://build.nvidia.com/)

**Prepaid cards or numbers marked as spam will not be able to register for an API Key**

## Setup environment variable

### MacOS

1. Open a terminal
2. Edit .zprofile

    `vi ~/.zprofile`

3. insert the following line to end of file

    `export NVIDIA_API_KEY=<your api key>`

4. exit vi editor

    `source ~/.zprofile`

### Windows

1. Open CMD terminal

    `setx NVIDIA_API_KEY "<your api key>"`

## LLM Invocation

The NIMS used in this challenge are
1. llama-3.3-nemotron-super-49b-v1
2. mistral-nemo-12b-instruct

You can invoke the LLMs using the following options

1. Call the NIM APIs hosted in the cloud - you will not need any extra setup for this
2. Host the NIM containers locally in your environment.

    Instructions as follows to host \
    [llama-3.3-nemotron-super-49b-v1](https://build.nvidia.com/nvidia/llama-3_3-nemotron-super-49b-v1/deploy?environment=linux.md)\
    [mistral-nemo-12b-instruct](https://build.nvidia.com/nv-mistralai/mistral-nemo-12b-instruct/deploy)
