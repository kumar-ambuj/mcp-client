# MCP Client with Google Gemini API

A Python client that integrates Google Gemini's advanced language model with the Model Context Protocol (MCP) to enable intelligent tool calling and server interactions.

## 🌟 Features

- **Google Gemini Integration**: Leverages Gemini 2.0 Flash for intelligent responses
- **MCP Tool Support**: Seamlessly connects to MCP servers and executes tools
- **Function Calling**: Automatic tool detection and execution based on user queries
- **Interactive Chat**: Real-time conversational interface
- **Multi-language Server Support**: Works with both Python (.py) and Node.js (.js) MCP servers
- **Error Handling**: Robust error management and recovery

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API key
- MCP server script

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd mcp-gemini-client
```

2. Install dependencies:
```bash
pip install google-generativeai python-dotenv mcp
```

Or using uv:
```bash
uv add google-generativeai python-dotenv mcp
```

3. Set up environment variables:
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### Usage

Run the client with your MCP server:

```bash
python client.py path/to/your/server.py
```

Or with uv:
```bash
uv run client.py path/to/your/server.py
```

### Example

```bash
# Start the client with a weather server
uv run client.py "/path/to/weather/weather.py"

# Chat interface
Query: What's the weather alert for California?
# Gemini automatically calls the get_alerts tool and provides results

Query: Get weather forecast for New York
# Gemini processes and calls appropriate tools
```

## 🛠️ How It Works

1. **Server Connection**: Connects to your MCP server via stdio transport
2. **Tool Discovery**: Automatically discovers available tools from the server
3. **Schema Conversion**: Converts MCP tool schemas to Gemini-compatible format
4. **Intelligent Routing**: Gemini decides which tools to call based on user queries
5. **Tool Execution**: Executes tools via MCP and returns results to Gemini
6. **Response Generation**: Gemini processes tool results and generates human-readable responses

## 📋 Supported MCP Servers

The client works with any MCP-compliant server, including:

- **Weather Services**: Get forecasts, alerts, and conditions
- **File Operations**: Read, write, and manipulate files
- **Database Queries**: Execute database operations
- **API Integrations**: Call external APIs
- **Custom Tools**: Any tool following MCP specifications

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Your Google Gemini API key | Yes |

### Server Requirements

Your MCP server must:
- Follow MCP protocol specifications
- Be executable via Python or Node.js
- Provide tool definitions with proper schemas

## 📖 API Reference

### MCPClient Class

#### Methods

- `connect_to_server(server_script_path: str)`: Connect to an MCP server
- `process_query(query: str) -> str`: Process user query with Gemini and tools
- `chat_loop()`: Start interactive chat session
- `cleanup()`: Clean up resources

#### Tool Integration

The client automatically:
- Converts MCP schemas to Gemini function declarations
- Handles tool parameter validation
- Manages conversation context with tool results

## 🎯 Example Use Cases

### Weather Information
```
Query: "What are the weather alerts for Texas?"
# Calls get_alerts tool with state="TX"
```

### Multi-step Operations
```
Query: "Get the weather forecast for coordinates 40.7128, -74.0060"
# Calls get_forecast tool with lat/lon parameters
```

### Natural Language Processing
```
Query: "Is there any severe weather expected in California today?"
# Intelligently calls appropriate weather tools and analyzes results
```

## 🔍 Troubleshooting

### Common Issues

**Schema Validation Errors**
- Ensure your MCP server provides valid JSON schemas
- Check that required fields are properly defined

**Connection Issues**
- Verify server script path is correct
- Ensure server script is executable
- Check server dependencies are installed

**API Errors**
- Verify your Gemini API key is valid
- Check your API quota and usage limits
- Ensure internet connectivity

### Debug Mode

Enable verbose logging by modifying the client:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Google Gemini](https://ai.google.dev/) for the powerful language model
- [Model Context Protocol](https://github.com/modelcontextprotocol) for the standardized tool interface
- [Anthropic](https://www.anthropic.com/) for MCP development

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](../../issues) section
2. Create a new issue with detailed information
3. Include error messages, server logs, and reproduction steps

---

**Made with ❤️ for the MCP community**
