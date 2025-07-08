mkdir -p submission
cp llm_workflow/main.py submission/llm-workflow/main.py
cp llm_workflow/mcp_http_client.py submission/llm-workflow/mcp_http_client.py
cp mcp-servers/invoice/src/mcp_server_invoice/qna_agent.py submission/mcp-servers/invoice/qna_agent.py
cp mcp-servers/invoice/src/mcp_server_invoice/server_http.py submission/mcp-servers/invoice/server_http.py
cp mcp-servers/qna/src/mcp_server_qna/server.py submission/mcp-servers/qna/server.py
zip -r submission.zip submission