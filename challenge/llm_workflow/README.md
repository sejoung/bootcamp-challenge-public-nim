# LLM workflow

## Run

start invoice mcp server

```bash
cd mcp-servers/invoice
uv run mcp-server-invoice \
    --mcp-server-qna-path ../qna \
    --inf-url https://integrate.api.nvidia.com/v1 \
    --nvidia-api-key <your api key>
```

start llm workflow

```bash
uv run main.py
```