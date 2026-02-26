# Project Progress

## Session Intent

Yapısal Sağlık İzleme (Structural Health Monitoring) projesi — FastAPI backend, React frontend, ML modelleri (ANFIS, risk analizi, beton dayanım tahmini), Supabase veritabanı, Pinecone vektör arama.

## Completed

- [x] Modular FastAPI refactoring (main.py → routes/, services/, models/)
- [x] CI/CD pipeline (GitHub Actions) — self-hosted runner active
- [x] Pinecone MCP integration
- [x] Supabase MCP integration
- [x] TestSprite test coverage setup
- [x] Frontend (React) connected to backend
- [x] ML model training (concrete_model, risk_model, ANFIS)
- [x] Workflow scripts (/sabah, /gunsonu, /test, /gonder, /kontrol, /runner)
- [x] Context management entegrasyonu (CLAUDE.md, progress.md, memory-bank, /compress)

## In Progress

- [ ] (Yeni görev eklendiğinde buraya yaz)

## Decisions

- Anchored Iterative Summarization stratejisi kullanılacak (context-compression)
- MCP Memory-Bank ile dış hafıza kullanılacak
- CLAUDE.md otomatik okunacak, PROJECT-RULES.md kaldırıldı
- Artifact-driven development: progress.md merkez belge

## Files Modified (Son Oturum)

- mcp_config.json: memory-bank MCP server eklendi
- CLAUDE.md: Oluşturuldu (proje kuralları)
- progress.md: Oluşturuldu (bu dosya)
- .agent/workflows/compress.md: Oluşturuldu (/compress workflow)
- PROJECT-RULES.md: Silindi (CLAUDE.md ile değiştirildi)

## Next Steps

- Yeni sohbet aç ve CLAUDE.md otomatik okunduğunu test et
- /compress workflow'unu test et
- Uzun sohbet sonrası context-compression'ı dene
