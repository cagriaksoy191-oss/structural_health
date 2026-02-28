---
description: Context sıkıştırma — uzun sohbetlerde bağlamı temizle ve AGENTS.md güncelle
---

# Context Compression Workflow

1. Read the context-compression skill file at `~/.gemini/antigravity/skills/context-compression/SKILL.md`

2. Apply **Anchored Iterative Summarization** strategy:
   - Identify the session intent, modified files, decisions, and next steps as "anchors"
   - Summarize only newly accumulated content
   - Merge with existing AGENTS.md sections

3. Update `AGENTS.md` with these sections:
   - **Tamamlanan Geliştirmeler**: Mark finished items with [x]
   - **Mimari Kararlar**: Key technical decisions made
   - **Son Değişiklikler**: List of files changed in this session

4. If new development goals emerged, add them to `progress.md`

5. Remove from context:
   - Failed attempts and dead-end explorations
   - Redundant explanations already captured in AGENTS.md
   - Verbose tool outputs that are no longer relevant

6. Confirm compression completed with a brief summary of what was preserved and what was removed
