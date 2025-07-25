import asyncio
import json
import sys
from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()  # load environment variables from .env

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-001')

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server
        
        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")
            
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )
        
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        
        await self.session.initialize()
        
        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    def convert_mcp_tools_to_gemini(self, mcp_tools: List) -> List[Dict]:
        """Convert MCP tools to Gemini function calling format"""
        gemini_tools = []
        
        for tool in mcp_tools:
            function_declaration = {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
            
            # Convert input schema to Gemini format
            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                schema = tool.inputSchema
                if isinstance(schema, dict):
                    if "properties" in schema:
                        # Clean properties by removing unsupported fields
                        cleaned_properties = {}
                        for prop_name, prop_schema in schema["properties"].items():
                            cleaned_prop = {}
                            if isinstance(prop_schema, dict):
                                # Only keep supported fields for Gemini
                                if "type" in prop_schema:
                                    cleaned_prop["type"] = prop_schema["type"]
                                if "description" in prop_schema:
                                    cleaned_prop["description"] = prop_schema["description"]
                                if "enum" in prop_schema:
                                    cleaned_prop["enum"] = prop_schema["enum"]
                                # Remove unsupported fields like 'title'
                            cleaned_properties[prop_name] = cleaned_prop
                        
                        function_declaration["parameters"]["properties"] = cleaned_properties
                    
                    if "required" in schema:
                        function_declaration["parameters"]["required"] = schema["required"]
            
            gemini_tools.append({"function_declarations": [function_declaration]})
        
        return gemini_tools

    async def execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a tool call via MCP"""
        try:
            result = await self.session.call_tool(tool_name, arguments)
            
            if result.content:
                # Handle different content types
                content_parts = []
                for content in result.content:
                    if hasattr(content, 'text'):
                        content_parts.append(content.text)
                    elif hasattr(content, 'data'):
                        content_parts.append(str(content.data))
                    else:
                        content_parts.append(str(content))
                
                return "\n".join(content_parts)
            else:
                return "Tool executed successfully but returned no content"
                
        except Exception as e:
            return f"Error executing tool {tool_name}: {str(e)}"

    async def process_query(self, query: str) -> str:
        """Process a query using Gemini and available tools"""
        
        # Get available tools
        response = await self.session.list_tools()
        available_tools = response.tools
        
        # Convert tools to Gemini format
        gemini_tools = self.convert_mcp_tools_to_gemini(available_tools)
        
        try:
            # Initial request to Gemini
            if gemini_tools:
                response = self.model.generate_content(
                    query,
                    tools=gemini_tools,
                    tool_config={'function_calling_config': {'mode': 'AUTO'}}
                )
            else:
                response = self.model.generate_content(query)
            
            # Check if Gemini wants to call functions
            if response.candidates and response.candidates[0].content.parts:
                parts = response.candidates[0].content.parts
                
                final_response_parts = []
                
                for part in parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        # Execute the function call
                        function_call = part.function_call
                        tool_name = function_call.name
                        
                        # Convert arguments
                        arguments = {}
                        if hasattr(function_call, 'args') and function_call.args:
                            arguments = dict(function_call.args)
                        
                        print(f"\nExecuting tool: {tool_name} with arguments: {arguments}")
                        
                        # Execute the tool
                        tool_result = await self.execute_tool_call(tool_name, arguments)
                        
                        # Create a follow-up request with the tool result
                        follow_up_messages = [
                            {"role": "user", "parts": [{"text": query}]},
                            {"role": "model", "parts": [{"function_call": function_call}]},
                            {"role": "user", "parts": [{"function_response": {
                                "name": tool_name,
                                "response": {"result": tool_result}
                            }}]}
                        ]
                        
                        # Get final response from Gemini
                        final_response = self.model.generate_content(follow_up_messages)
                        if final_response.text:
                            final_response_parts.append(final_response.text)
                        
                    elif hasattr(part, 'text') and part.text:
                        final_response_parts.append(part.text)
                
                return "\n".join(final_response_parts) if final_response_parts else "No response generated"
            
            # If no function calls, return the text response
            return response.text if response.text else "No response generated"
            
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return f"Error: {str(e)}"

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client with Gemini Started!")
        print("Type your queries or 'quit' to exit.")
        
        while True:
            try:
                query = input("\nQuery: ").strip()
                
                if query.lower() == 'quit':
                    break
                    
                response = await self.process_query(query)
                print(f"\nResponse: {response}")
                    
            except Exception as e:
                print(f"\nError: {str(e)}")
    
    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)
        
    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())