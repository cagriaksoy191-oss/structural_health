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

## 🧠 Pinecone MCP Zorunlu Arama Kuralı (SADECE MCP YÜKLÜYSE)

**ÖNEMLİ:** Eğer bu sohbette `mcp_pinecone-mcp-server` araçları (tools) **YOKSA**, bu adımı atla ve standart çalışmana devam et. Ekip arkadaşlarının MCP'si olmayabilir, bu durumda normal RAG/Dosya okuma veya `AGENTS.md` bilgilerini kullan.

Eğer `mcp_pinecone-mcp-server` araçları **VARSA**:

- Kullanıcı projeye ait teorik veriler, TBDY 2018 kuralları, korozyon, ASTM standartları, AFAD hesaplamaları veya sistemin çalışma mantığı ile ilgili herhangi bir soru sorduğunda **İLK OLARAK KESİNLİKLE** `mcp_pinecone-mcp-server_search-records` aracıyla `deprem-hafiza` indeksinde arama yapacaksın (`proje` veya `referanslar` namespace).
- Kendi hafızanı veya dosyalardaki kodları taramadan **ÖNCE** mutlaka ilgili konuyu Pinecone'a sorup cevabını Pinecone'dan gelen referans belgelere göre oluşturmalısın.

## Architecture

- Backend: FastAPI (Python) — modular structure (routes/, services/, models/)
- Frontend: React (Vite)
- Database: Supabase
- Vector DB: Pinecone MCP
- CI/CD: GitHub Actions (self-hosted runner)
