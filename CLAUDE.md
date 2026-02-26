# Project Rules

## Output Rules

- Output only technical content. No apologies, greetings, or meta-commentary.
- Use concise mode: short explanations, no redundancy.
- Always respond in Turkish unless code/technical terms require English.

## Context Management

- When context gets heavy (>50 messages or major milestone), use the context-compression skill with Anchored Iterative Summarization strategy.
- Always maintain progress.md: update after every completed task.
- When switching models (Claude ↔ Gemini), first read progress.md and this file.
- Never keep failed attempts or dead-end explorations in conversation history.

## File Conventions

- progress.md: Living document — Completed items, In Progress, Decisions, Next Steps.
- Use /compress workflow to trigger context compression easily.
- Every evening: "Create checkpoint in memory-bank" to persist context externally.

## Architecture

- Backend: FastAPI (Python) — modular structure (routes/, services/, models/)
- Frontend: React
- Database: Supabase
- Vector DB: Pinecone MCP
- CI/CD: GitHub Actions (self-hosted runner)
