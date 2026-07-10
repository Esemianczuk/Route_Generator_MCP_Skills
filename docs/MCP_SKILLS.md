# MCP Skills Guide

The skill bundle is a thin, versioned instruction layer for agent clients. It does not replace MCP tools; it teaches the model which tool family to choose, how to preserve session state, and how to avoid repeated mistakes such as generating a new route for a summary question or rendering rain maps when wind is the actual weather issue.

## Recommended Client Behavior

- Load skill metadata at startup.
- Inject only the selected compact bundle for a conversation.
- Show skill selection/usage alongside tool calls.
- Keep route ids and artifacts in backend session state; do not require users to paste raw ids.

## Route Resources

Future clients can expose these resources:

- `route://guides/skills-and-external-recipes`
- `route://guides/ingredient-planning`
- `route://guides/local-poi-workflows`
- `route://guides/weather-and-performance`

