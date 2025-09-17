# MCP-SERVER-INVOICE-TEST

## Commands

Start invoice mcp server

```
cd mcp-servers/invoice
uv run mcp-server-invoice \
    --mcp-server-qna-path ../qna \
    --inf-url https://integrate.api.nvidia.com/v1 \
    --nvidia-api-key <your api key>
```

Run your test cases

```
cd mcp-server-invoice-test
uv run main.py
```
