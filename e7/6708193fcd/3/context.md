# Session Context

## User Prompts

### Prompt 1

Create following new apps: web_search-> should allow searching for some content, hardcode answers. add common queries like whats the weather in SF, latest news about some match, and so on. No need to create task or run eval for now.

### Prompt 2

Add a fake slack app, arxiv for papers, fetch ( to fetch anything from web, not fake), yahoo-finance, docs for creating, finding and saving docs, calculator for simple number calculator, and an in memory sqlite database app ( load some dummy data in memory).

### Prompt 3

commit these apps.

### Prompt 4

Now create tasks one at a time. Give me task, i'll approve then then you can create it.

### Prompt 5

yes.

### Prompt 6

yes. For next task create a multi app task, that spans 2-3 apps

### Prompt 7

yes.

### Prompt 8

yes

### Prompt 9

yes. Next create task for unused apps

### Prompt 10

yes. this is last

### Prompt 11

Now do a run and evaluate. It will take some time

### Prompt 12

[Request interrupted by user for tool use]

### Prompt 13

Just run the eval. Fresh full run is costly

### Prompt 14

We should allow it capability to run a individual task on a specific id as well, for debugging use cases

### Prompt 15

Add mcp support in claude agent sdk as well, see options = ClaudeAgentOptions(
    mcp_servers={"calc": calculator},
    allowed_tools=["mcp__calc__add", "mcp__calc__multiply"],
) . Test with one tasj first

### Prompt 16

[Request interrupted by user]

### Prompt 17

No temp fix. Give me command i'll run

### Prompt 18

I;ve ran it. Can we run eval now

