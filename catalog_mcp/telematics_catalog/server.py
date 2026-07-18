"""Telematics catalog MCP server — exposes medallion table metadata and sample rows."""

from __future__ import annotations

import json
from pathlib import Path

import anyio
import pandas as pd
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"

TABLE_SCHEMAS = {
    "bronze.telematics_events": {
        "layer": "bronze",
        "path": DATA_DIR / "bronze" / "telematics_events.parquet",
        "columns": [
            "event_id",
            "locomotive_id",
            "timestamp_utc",
            "latitude",
            "longitude",
            "speed_mph",
            "fuel_rate_lph",
            "fault_code",
            "route_id",
            "_ingested_at",
            "_source_file",
        ],
        "description": "Raw ingested telematics events from CSV sources.",
    },
    "silver.locomotive_events": {
        "layer": "silver",
        "path": DATA_DIR / "silver" / "locomotive_events.parquet",
        "columns": [
            "event_id",
            "locomotive_id",
            "timestamp_utc",
            "event_date",
            "speed_mph",
            "fault_code",
            "has_fault",
            "severity",
            "recommended_action",
            "title",
            "route_id",
        ],
        "description": "Cleaned locomotive events enriched with maintenance bulletin metadata.",
    },
    "gold.service_metrics": {
        "layer": "gold",
        "path": DATA_DIR / "gold" / "service_metrics.parquet",
        "columns": [
            "locomotive_id",
            "route_id",
            "event_date",
            "event_count",
            "fault_event_count",
            "avg_speed_mph",
            "max_speed_mph",
            "high_severity_fault_count",
            "high_severity_fault_flag",
            "recommended_review",
        ],
        "description": "Aggregated service KPIs for operator decisioning dashboards.",
    },
}

server = Server("telematics-catalog")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_tables",
            description="List available bronze, silver, and gold telematics tables.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="describe_table",
            description="Describe columns and metadata for a telematics table.",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Fully qualified table name, e.g. gold.service_metrics",
                    }
                },
                "required": ["table_name"],
            },
        ),
        Tool(
            name="sample_rows",
            description="Return up to 5 sample rows from a table (read-only).",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {"type": "string"},
                    "limit": {"type": "integer", "default": 5},
                },
                "required": ["table_name"],
            },
        ),
    ]


def _read_table(table_name: str, limit: int | None = None) -> pd.DataFrame:
    if table_name not in TABLE_SCHEMAS:
        raise ValueError(f"Unknown table: {table_name}. Use list_tables first.")
    path = TABLE_SCHEMAS[table_name]["path"]
    if not path.exists():
        raise FileNotFoundError(
            f"Table file not found: {path}. Run: python -m src.pipelines.run_all"
        )
    df = pd.read_parquet(path)
    if limit is not None:
        return df.head(limit)
    return df


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "list_tables":
        tables = [
            {"table_name": k, "layer": v["layer"], "description": v["description"]}
            for k, v in TABLE_SCHEMAS.items()
        ]
        return [TextContent(type="text", text=json.dumps(tables, indent=2))]

    if name == "describe_table":
        table_name = arguments["table_name"]
        if table_name not in TABLE_SCHEMAS:
            return [TextContent(type="text", text=f"Unknown table: {table_name}")]
        meta = TABLE_SCHEMAS[table_name]
        payload = {
            "table_name": table_name,
            "layer": meta["layer"],
            "description": meta["description"],
            "columns": meta["columns"],
            "file_exists": meta["path"].exists(),
            "file_path": str(meta["path"]),
        }
        return [TextContent(type="text", text=json.dumps(payload, indent=2))]

    if name == "sample_rows":
        table_name = arguments["table_name"]
        limit = int(arguments.get("limit", 5))
        try:
            df = _read_table(table_name, limit=limit)
            return [TextContent(type="text", text=df.to_json(orient="records", indent=2))]
        except (ValueError, FileNotFoundError) as exc:
            return [TextContent(type="text", text=str(exc))]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def _run() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> None:
    anyio.run(_run)


if __name__ == "__main__":
    main()
