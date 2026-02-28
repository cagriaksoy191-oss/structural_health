# Project Rules

## Output Rules

- Output only technical content. No apologies, greetings, or meta-commentary.
- Use concise mode: short explanations, no redundancy.
- Always respond in Turkish unless code/technical terms require English.

## Context Management

- **AGENTS.md** — Projenin TEK KAYNAK belgesi. Mimari, modüller, kararlar, tamamlanan işler buradadır.
  - Yeni sohbet başlangıcı: "AGENTS.md dosyasını oku ve kaldığımız yerden devam et"
  - Gün sonu güncellemesi: "AGENTS.md dosyasını bugün yaptığım değişikliklere göre güncelle"
- **progress.md** — Sadece geliştirme hedefleri listesi. Ekip üyeleri buradan görev seçer.
- **CLAUDE.md** — Bu dosya. Proje kuralları (her sohbette otomatik okunur).
- When context gets heavy (>50 messages or major milestone), use the context-compression skill.
- Never keep failed attempts or dead-end explorations in conversation history.

## ⚠️ Önemli Kural

"AGENTS.md dosyasını oku" komutu verildiğinde:

- Dosyayı oku ve **sessizce hafızana al**.
- Görev yapma, kod yazma, değişiklik önerme.
- Sadece "Projeyi okudum, hazırım. Ne yapmamı istersin?" şeklinde yanıt ver.

## Architecture

- Backend: FastAPI (Python) — modular structure (routes/, services/, models/)
- Frontend: React (Vite)
- Database: Supabase
- Vector DB: Pinecone MCP
- CI/CD: GitHub Actions (self-hosted runner)
