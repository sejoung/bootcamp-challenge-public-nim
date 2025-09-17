import contextlib
import json
import logging
import sqlite3
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any
from typing import List

import mcp.types as types
import uvicorn
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

from . import qna_agent

# import qna_agent

logger = logging.getLogger(__name__)


class Invoice:
    def __init__(self, db_path):
        self.db_path = str(Path().resolve().joinpath(db_path))

    def _invoice_refund(self, invoice_id: int | None, invoice_line_ids: list[int] | None, mock: bool = True) -> List[
        types.TextContent]:
        """Given an Invoice ID and/or Invoice Line IDs, delete the relevant Invoice/InvoiceLine records in the Chinook DB.

        Args:
            invoice_id: The Invoice to delete.
            invoice_line_ids: The Invoice Lines to delete.
            mock: If True, do not actually delete the specified Invoice/Invoice Lines. Used for testing purposes.
        """

        if invoice_id is None and invoice_line_ids is None:
            return 0.0

        # Connect to the Chinook database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        total_refund = 0.0

        try:
            # If invoice_id is provided, delete entire invoice and its lines
            if invoice_id is not None:
                # First get the total amount for the invoice
                cursor.execute(
                    """
                    SELECT Total
                    FROM Invoice
                    WHERE InvoiceId = ?
                    """,
                    (invoice_id,),
                )

                result = cursor.fetchone()
                if result:
                    total_refund += result[0]

                # Delete invoice lines first (due to foreign key constraints)
                if not mock:
                    cursor.execute(
                        """
                        DELETE
                        FROM InvoiceLine
                        WHERE InvoiceId = ?
                        """,
                        (invoice_id,),
                    )

                    # Then delete the invoice
                    cursor.execute(
                        """
                        DELETE
                        FROM Invoice
                        WHERE InvoiceId = ?
                        """,
                        (invoice_id,),
                    )

            # If specific invoice lines are provided
            if invoice_line_ids is not None:
                # Get the total amount for the specified invoice lines
                placeholders = ",".join(["?" for _ in invoice_line_ids])
                cursor.execute(
                    f"""
                    SELECT SUM(UnitPrice * Quantity)
                    FROM InvoiceLine
                    WHERE InvoiceLineId IN ({placeholders})
                """,
                    invoice_line_ids,
                )

                result = cursor.fetchone()
                if result and result[0]:
                    total_refund += result[0]

                if not mock:
                    # Delete the specified invoice lines
                    cursor.execute(
                        f"""
                        DELETE FROM InvoiceLine
                        WHERE InvoiceLineId IN ({placeholders})
                    """,
                        invoice_line_ids,
                    )

            # Commit the changes
            conn.commit()

        except sqlite3.Error as e:
            # Roll back in case of error
            conn.rollback()
            raise e

        finally:
            # Close the connection
            conn.close()

        return [types.TextContent(
            type="text",
            text=str(total_refund)
        )]

    def _invoice_lookup(
            self,
            customer_first_name: str,
            customer_last_name: str,
            customer_phone: str,
            track_name: str | None,
            album_title: str | None,
            artist_name: str | None,
            purchase_date_iso_8601: str | None,
    ) -> List[types.TextContent]:
        """Find all of the Invoice Line IDs in the Chinook DB for the given filters."""
        # Connect to the database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Base query joining all necessary tables
        query = """
                SELECT il.InvoiceLineId,
                       t.Name        as track_name,
                       art.Name      as artist_name,
                       i.InvoiceDate as purchase_date,
                       il.Quantity   as quantity_purchased,
                       il.UnitPrice  as price_per_unit
                FROM InvoiceLine il
                         JOIN Invoice i ON il.InvoiceId = i.InvoiceId
                         JOIN Customer c ON i.CustomerId = c.CustomerId
                         JOIN Track t ON il.TrackId = t.TrackId
                         JOIN Album alb ON t.AlbumId = alb.AlbumId
                         JOIN Artist art ON alb.ArtistId = art.ArtistId
                WHERE c.FirstName = ?
                  AND c.LastName = ?
                  AND c.Phone = ? \
                """

        # Parameters for the query
        params = [customer_first_name, customer_last_name, customer_phone]

        # Add optional filters
        if track_name:
            query += " AND t.Name = ?"
            params.append(track_name)

        if album_title:
            query += " AND alb.Title = ?"
            params.append(album_title)

        if artist_name:
            query += " AND art.Name = ?"
            params.append(artist_name)

        if purchase_date_iso_8601:
            query += " AND date(i.InvoiceDate) = date(?)"
            params.append(purchase_date_iso_8601)

        # Execute query
        cursor.execute(query, params)

        # Fetch results
        results = cursor.fetchall()

        # Convert results to list of dictionaries
        output = []
        for row in results:
            output.append(
                {
                    "invoice_line_id": row[0],
                    "track_name": row[1],
                    "artist_name": row[2],
                    "purchase_date": row[3],
                    "quantity_purchased": row[4],
                    "price_per_unit": row[5],
                }
            )

        # Close connection
        conn.close()

        # return output
        return [types.TextContent(
            type="text",
            text=json.dumps(output)
        )]


class ExternalAgents:
    def __init__(self, nvidia_api_key, mcp_server_qna_path, inf_url):
        self.qna_agent = qna_agent.QNAAgent(nvidia_api_key, mcp_server_qna_path, inf_url)

    async def _media_lookup(self, query) -> List[types.TextContent]:
        ## TODO
        ## invoke qna agent and return output
        response = await self.qna_agent.run(query)
        return [types.TextContent(type="text", text=response)]


def main(db_path: str, nvidia_api_key: str, mcp_server_qna_path: str, inf_url: str):
    invoice = Invoice(db_path)
    external_agent = ExternalAgents(nvidia_api_key, mcp_server_qna_path, inf_url)
    mcp = Server("invoice")

    @mcp.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        ## TODO
        ## return schema for tools
        return [types.Tool(
            name="invoice_lookup",
            description="Look up invoice line IDs based on customer and optional filters.",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_first_name": {"type": "string", "description": "Customer's first name."},
                    "customer_last_name": {"type": "string", "description": "Customer's last name."},
                    "customer_phone": {"type": "string", "description": "Customer's phone number."},
                    "track_name": {"type": "string", "description": "(Optional) Name of the track."},
                    "album_title": {"type": "string", "description": "(Optional) Title of the album."},
                    "artist_name": {"type": "string", "description": "(Optional) Name of the artist."},
                    "purchase_date_iso_8601": {"type": "string",
                                               "description": "(Optional) Purchase date in ISO 8601 format (YYYY-MM-DD)."}
                },
                "required": ["customer_first_name", "customer_last_name", "customer_phone"]
            }),
            types.Tool(
                name="invoice_refund",
                description="Process a refund for the specified invoice or invoice lines.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "invoice_id": {"type": "integer", "description": "(Optional) The Invoice ID to refund."},
                        "invoice_line_ids": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "(Optional) List of Invoice Line IDs to refund."
                        },
                        "mock": {
                            "type": "boolean",
                            "description": "If true, do not actually delete records (for testing purposes).",
                            "default": True
                        }
                    },
                    "required": []
                }
            )]

    @mcp.call_tool()
    async def handle_call_tool(name: str, args: dict[str, Any] | None):
        ## TODO
        ## implement tool calling logic
        if name == "invoice_lookup":
            return invoice._invoice_lookup(
                customer_first_name=args.get("customer_first_name"),
                customer_last_name=args.get("customer_last_name"),
                customer_phone=args.get("customer_phone"),
                track_name=args.get("track_name"),
                album_title=args.get("album_title"),
                artist_name=args.get("artist_name"),
                purchase_date_iso_8601=args.get("purchase_date_iso_8601"),
            )
        elif name == "invoice_refund":
            return invoice._invoice_refund(
                invoice_id=args.get("invoice_id"),
                invoice_line_ids=args.get("invoice_line_ids"),
                mock=args.get("mock", True),
            )
        elif name == "media_lookup":
            query = args.get("query")
            if query:
                return await external_agent._media_lookup(query)
            else:
                return [types.TextContent(type="text", text="Error: 'query' parameter is required for media_lookup.")]
        else:
            return [types.TextContent(type="text", text=f"Error: Unknown tool '{name}'.")]

    # Create the session manager with true stateless mode
    session_manager = StreamableHTTPSessionManager(
        app=mcp,
        event_store=None,
        json_response=True,
        stateless=True,
    )

    async def handle_streamable_http(
            scope: Scope, receive: Receive, send: Send
    ) -> None:
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """Context manager for session manager."""
        async with session_manager.run():
            logger.info("Application started with StreamableHTTP session manager!")
            try:
                yield
            finally:
                logger.info("Application shutting down...")

    # Create an ASGI application using the transport
    starlette_app = Starlette(
        debug=True,
        routes=[
            Mount("/mcp", app=handle_streamable_http),
        ],
        lifespan=lifespan,
    )

    uvicorn.run(starlette_app, host="127.0.0.1")


class ServerWrapper():
    """A wrapper to compat with mcp[cli]"""

    def run(self):
        import asyncio
        asyncio.run(main())


wrapper = ServerWrapper()
