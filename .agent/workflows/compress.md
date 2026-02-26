---
description: Context sıkıştırma — uzun sohbetlerde bağlamı temizle ve progress.md güncelle
---

# Context Compression Workflow

1. Read the context-compression skill file at `~/.gemini/antigravity/skills/context-compression/SKILL.md`

2. Apply **Anchored Iterative Summarization** strategy:
   - Identify the session intent, modified files, decisions, and next steps as "anchors"
   - Summarize only newly accumulated content
   - Merge with existing progress.md sections

3. Update `progress.md` with these sections:
   - **Session Intent**: What are we working on
   - **Completed**: Mark finished items with [x]
   - **In Progress**: Current tasks
   - **Decisions**: Key technical decisions made
   - **Files Modified**: List of files changed in this session
   - **Next Steps**: What to do next

4. Remove from context:
   - Failed attempts and dead-end explorations
   - Redundant explanations already captured in progress.md
   - Verbose tool outputs that are no longer relevant

5. Confirm compression completed with a brief summary of what was preserved and what was removed
