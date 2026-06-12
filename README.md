# Hermes Session Cleaner

Hermes Agent session temizlik aracı: kısa konuşmaları sil, başlıksız session'lara title üret.

## Kullanım

```bash
# Neler olacağını gör (dry-run)
python3 hermes_cleaner.py --dry-run

# Gerçek temizlik
python3 hermes_cleaner.py

# Sadece 3 mesajdan az olanları sil
python3 hermes_cleaner.py --min-messages 3

# Sadece silme yap, title üretme
python3 hermes_cleaner.py --no-title

# Sadece title üret, silme
python3 hermes_cleaner.py --no-delete --max-titles 50
```

## Nasıl Çalışır

1. Tüm session'ları tarar
2. `< N` mesajlı session'ları siler (default: 5)
3. `>= N` mesajlı ama başlıksız session'lara title üretir (hermes3:latest ile)

## Gereksinimler

- Hermes Agent kurulu olmalı
- Ollama'da `hermes3:latest` modeli (env ile değiştirilebilir)
- `HERMES_CLEANER_MODEL` ve `HERMES_CLEANER_ENDPOINT` env override'ları
