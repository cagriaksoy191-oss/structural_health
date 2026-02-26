# Context Management Kullanım Rehberi

Bu rehber, Antigravity'de uzun sohbetlerde bağlam kaybını önlemek için kurduğumuz sistemi ve günlük 4 rutini detaylı şekilde anlatır.

## Sistem Ne Yapar?

Antigravity'de uzun süre çalıştığında yapay zeka önceki mesajları "unutmaya" başlar. Bunun sebebi context window'un (bağlam penceresi) dolmasıdır. Biz 3 katmanlı bir çözüm kurduk:

| Katman | Araç | Görevi |
|--------|------|--------|
| **Kurallar** | `CLAUDE.md` | Her sohbette AI'ın nasıl davranacağını belirler |
| **Hafıza** | `progress.md` | Projenin durumunu bir dosyada tutar |
| **Dış hafıza** | MCP Memory-Bank | Bilgiyi sohbet dışında kalıcı olarak saklar |

## Rutin 1 - Sohbet Başında (Otomatik)

### Ne Yaparsın?

**Hiçbir şey.** `CLAUDE.md` dosyası proje kökünde olduğu için Antigravity her yeni sohbet açtığında bu dosyayı **otomatik olarak okur**.

### Ne İşe Yarar?

`CLAUDE.md` dosyası AI'a şu kuralları hatırlatır:

- Sadece teknik içerik üret, gereksiz özür/selam/açıklama yapma
- Kısa ve öz cevaplar ver
- Türkçe cevap ver
- Context ağırlaştığında context-compression kullan
- progress.md dosyasını güncelle
- Başarısız denemeleri geçmişte tutma

### Nasıl Çalışır?

```text
Yeni sohbet aç → Antigravity otomatik CLAUDE.md'yi okur → AI kurallara göre davranır
```

### Doğrulama

İlk sohbette şunu sorabilirsin: **"Bu projenin kuralları neler?"** — AI `CLAUDE.md`'den okuduğu kuralları sıralayacaktır.

## Rutin 2 - Sohbet Uzadığında /compress

### Ne Yaparsın?

Sohbet çok uzadığında (50+ mesaj veya büyük bir iş tamamlandığında) sohbete şunu yaz:

```text
/compress
```

### Ne İşe Yarar?

Bu komut `.agent/workflows/compress.md` dosyasındaki workflow'u tetikler. AI şunları yapar:

**Adım 1 - Anchored Iterative Summarization uygular:**

- Önemli bilgileri (dosya değişiklikleri, kararlar, sonraki adımlar) "çapa" olarak korur
- Sadece yeni birikmiş içeriği özetler
- Mevcut özete ekler (sıfırdan yazmaz)

**Adım 2 - progress.md dosyasını günceller:**

- Tamamlanan işleri `[x]` ile işaretler
- Devam eden işleri yazar
- Alınan kararları kaydeder
- Değiştirilen dosyaları listeler
- Sonraki adımları belirler

**Adım 3 - Gereksiz içeriği temizler:**

- Başarısız denemeler silinir
- Artık gerekmeyen uzun tool çıktıları kaldırılır
- progress.md'de zaten kayıtlı olan tekrarlı açıklamalar çıkarılır

### Ne Zaman Kullanmalısın?

- Sohbet 50+ mesaja ulaştığında
- Büyük bir özellik tamamlandığında
- AI "unutmaya" başladığını hissettiğinde (aynı şeyleri tekrar soruyorsa)
- Cevaplar yavaşlamaya başladığında

### Örnek Kullanım

```text
Sen: /compress
AI: Context compression uygulandı.
    Korunan: 12 dosya değişikliği, 5 karar, 3 sonraki adım
    Kaldırılan: 34 başarısız deneme, 18 tool çıktısı
    progress.md güncellendi.
```

## Rutin 3 - Yeni Thread ve progress.md Oku

### Ne Yaparsın?

Yeni bir sohbet penceresi açtığında (veya Antigravity'yi yeniden başlattığında) ilk mesaj olarak şunu yaz:

```text
progress.md dosyasını oku ve kaldığımız yerden devam et
```

### Ne İşe Yarar?

`progress.md` projenin tüm durumunu tek bir dosyada tutar:

- **Session Intent**: Proje neyle ilgili
- **Completed**: Tamamlanan tüm işler
- **In Progress**: Şu an üzerinde çalışılan işler
- **Decisions**: Alınan teknik kararlar
- **Files Modified**: Son oturumda değiştirilen dosyalar
- **Next Steps**: Sıradaki yapılacaklar

AI bu dosyayı okuduğunda, önceki sohbetin tüm bağlamını kazanır. Sanki aynı sohbete devam ediyormuş gibi çalışır.

### Ne Zaman Kullanmalısın?

- Her yeni sohbet penceresinde (CLAUDE.md otomatik okunur ama progress.md'yi sen söylemelisin)
- Antigravity'yi yeniden başlattığında
- Model değiştirdiğinde (Claude ve Gemini arası geçiş)
- Ertesi gün çalışmaya devam ederken

### Örnek Kullanım

```text
Sen: progress.md dosyasını oku ve kaldığımız yerden devam et
AI: progress.md okundu. Son duruma göre:
    - CI/CD pipeline tamamlanmış
    - Context management entegrasyonu yapılmış
    - Sıradaki iş: [Next Steps'ten okur]
    Kaldığımız yerden devam ediyorum.
```

## Rutin 4 - Gün Sonu ve Memory-Bank Checkpoint

### Ne Yaparsın?

Her gün çalışmayı bitirmeden önce sohbete şunu yaz:

```text
Create checkpoint in memory-bank
```

### Ne İşe Yarar?

Bu komut MCP Memory-Bank'ı kullanarak projenin durumunu **sohbet dışında** kalıcı olarak saklar.

**Fark nedir?**

| Özellik | progress.md | Memory-Bank |
|---------|-------------|-------------|
| **Nerede?** | Proje klasöründe dosya | MCP server'da hafıza grafiği |
| **Ne zaman kaybolur?** | Dosya silinirse | Server kapatılırsa |
| **Avantajı** | İnsan tarafından okunabilir | AI tarafından otomatik çekilebilir |
| **Kullanımı** | Manuel ("oku" demen gerekir) | Otomatik (AI ihtiyaç duyunca çeker) |

Memory-Bank, progress.md'nin **üstüne** ek bir güvenlik katmanıdır. İkisi birlikte çalışır:

- `progress.md` insanlar için (sen okuyabilirsin)
- Memory-Bank AI için (otomatik bağlam çekme)

### Ne Zaman Kullanmalısın?

- Her gün çalışmayı bitirirken
- Uzun bir sohbet sonrası
- Kritik bir milestone tamamladığında
- Birkaç gün ara vereceksen mutlaka

### Örnek Kullanım

```text
Sen: Create checkpoint in memory-bank
AI: Checkpoint oluşturuldu:
    - Proje durumu kaydedildi
    - 15 completed task, 2 in-progress
    - 7 karar ve 4 sonraki adım saklandı
```

## Günlük Akış Özeti

```text
SABAH
  1. Yeni sohbet aç (CLAUDE.md otomatik okunur)
  2. "progress.md oku ve devam et" yaz

GÜN İÇİ
  3. Normal çalış
  4. Sohbet uzadığında /compress yaz
  5. Gerekirse tekrarla

AKŞAM
  6. "Create checkpoint in memory-bank" yaz
  7. Sohbeti kapat
```

## Sorun Giderme

| Sorun | Çözüm |
|-------|-------|
| AI kuralları uygulamıyor | "CLAUDE.md dosyasını oku" de |
| /compress çalışmıyor | Sohbete `/compress` yaz (slash ile) |
| progress.md güncel değil | "progress.md'yi güncelle" de |
| Memory-bank bağlanmıyor | Antigravity'yi yeniden başlat |
| AI aynı şeyleri tekrar soruyor | Hemen `/compress` yaz |
