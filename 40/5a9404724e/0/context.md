# Session Context

## User Prompts

### Prompt 1

We have concept of world and tasks. The way to create a world is by creating an app which exposes tools. a world is collection of those apps. Lets start by creating dummy apps. Starting with email_app. It should have functions, list_emails, get_email, mark_as_read, search_email, etc etc. Do not create more than 7-8 functions in each app. Refer to fastmcp python library to create an mcp server. the structure should be like. 
class SampleApp(BaseApplication):
    """A sample application providing ...

### Prompt 2

Create a main mcp server. refer to mounting documentation at from fastmcp import FastMCP

# Create focused subservers
weather_server = FastMCP("Weather")

@weather_server.tool
def get_forecast(city: str) -> str:
    """Get weather forecast for a city."""
    return f"Sunny in {city}"

@weather_server.resource("data://cities")
def list_cities() -> list[str]:
    """List supported cities."""
    return ["London", "Paris", "Tokyo"]

# Create main server and mount the subserver
main = FastMCP("MainA...

### Prompt 3

❯ uv run python worlds/server.py
Traceback (most recent call last):
  File "/home/mbajaj/src/ga-bench/worlds/server.py", line 5, in <module>
    from worlds.apps.email_app import EmailApp
ModuleNotFoundError: No module named 'worlds'
 is the error i'm getting. check pyproject

### Prompt 4

Lets create a task for to test if agent can search all spam emails and delete them

### Prompt 5

Lets update the run and agents to use mcp server based tools. Lets start with react, refer to https://docs.langchain.com/oss/python/langchain/mcp

### Prompt 6

Why is langchain specific instruction in run.py. The creating tool should be problem for the react agent, you should only pass the mcp server transport or url. client = MultiServerMCPClient(
    {
        "math": {
            "transport": "stdio",
            "command": "python",
            "args": ["/path/to/math_server.py"],
        }
    }
) so that the custom handling of langchain agent is done there.

### Prompt 7

once done, try running it as well and  see if it actually does tool call correctly and finds the answers

### Prompt 8

Nice. Add an app for calendar as well, and add one task for calendar too.

### Prompt 9

even if it is in subrprocess, the agent is only started once for a task, that subprocess maintains email state in memory so it shouldnt be a problem.

### Prompt 10

[Request interrupted by user for tool use]

### Prompt 11

Lets do a simple solution, start the mcp server on http in run.py ( modify to use stateless http on server.py by default) and pass the correct mcp to the agent.

### Prompt 12

The tasks prompt should always clearly specify the output as well. which it doesn't do right now hence the flaky failure. Update the tasks for both correctly

### Prompt 13

Update @CLAUDE.md README.md with how to create app, taskAs well as prompt writing instruction, golden rule instruction, and so on Once done commit the changes.

