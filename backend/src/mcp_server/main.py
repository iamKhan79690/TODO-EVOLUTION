"""
Main FastMCP server configuration for TODO-Evolution.

This module sets up the MCP server with HTTP transport on port 8001,
configures logging, and integrates with existing authentication and database systems.
"""

import os
import sys
import logging
import asyncio
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

# Add the parent directory to the path so we can import from sibling modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from fastmcp import FastMCP
except ImportError:
    # Fallback for development - create a simple mock if FastMCP is not available
    class FastMCP:
        def __init__(self, name: str):
            self.name = name
            self.tools = []

        def tool(self):
            def decorator(func):
                self.tools.append(func)
                return func
            return decorator

        def run(self, **kwargs):
            print(f"MCP Server {self.name} would start with {kwargs}")
            print(f"Available tools: {[tool.__name__ for tool in self.tools]}")

from src.database import get_session
from src.auth.better_auth_config import verify_token
from src.models.models import User

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MCP Server instance
mcp = FastMCP("todo-evolution-mcp")

# Global state for server management
_server_state = {
    "startup_time": None,
    "health_status": "starting"
}

@asynccontextmanager
async def lifespan(app):
    """Manage server lifecycle."""
    logger.info("🚀 MCP Server starting up...")
    _server_state["startup_time"] = asyncio.get_event_loop().time()
    _server_state["health_status"] = "healthy"

    # Test database connection
    try:
        async with get_session() as session:
            # Simple connection test
            await session.execute("SELECT 1")
        logger.info("✅ Database connection successful")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        _server_state["health_status"] = "degraded"

    yield

    logger.info("🛑 MCP Server shutting down...")
    _server_state["health_status"] = "shutting_down"

@mcp.tool()
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for monitoring MCP server status.

    Returns:
        Dict containing server health information
    """
    uptime = None
    if _server_state["startup_time"]:
        uptime = asyncio.get_event_loop().time() - _server_state["startup_time"]

    return {
        "status": _server_state["health_status"],
        "uptime_seconds": uptime,
        "server": "todo-evolution-mcp",
        "version": "1.0.0",
        "transport": os.getenv("TRANSPORT", "http"),
        "port": int(os.getenv("MCP_HTTP_PORT", 8001))
    }

# Import and register tools after MCP server is initialized
# This avoids circular imports
def register_tools():
    """Register all MCP tools."""
    try:
        # Import tools module
        from . import tools

        # Register tools with the MCP server
        tools.register_tools(mcp)

    except ImportError as e:
        logger.error(f"❌ Failed to import tools module: {str(e)}")
        logger.warning("⚠️ Tools module not available - creating placeholder tools")

        @mcp.tool()
        async def placeholder_add_task(title: str) -> Dict[str, Any]:
            """Placeholder for add_task tool."""
            return {"success": False, "error": "Tool not yet implemented"}

def main():
    """
    Main entry point for the MCP server with HTTP transport.
    """
    try:
        # Register all tools
        register_tools()

        # Get configuration from environment
        transport = os.getenv("TRANSPORT", "http")
        host = os.getenv("MCP_HTTP_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_HTTP_PORT", 8001))

        logger.info(f"🌟 Starting TODO-Evolution MCP Server")
        logger.info(f"📡 Transport: {transport}")
        logger.info(f"🌐 Host: {host}")
        logger.info(f"🔌 Port: {port}")
        logger.info(f"🔧 Environment: {os.getenv('ENVIRONMENT', 'development')}")

        # Run the MCP server
        mcp.run(
            transport=transport,
            host=host,
            port=port
        )

    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"💥 Server error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()