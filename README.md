# Hermes Session Cleaner

Hermes Agent session temizlik aracı: kısa konuşmaları sil, başlıksız session'lara title üret.

## Kurulum

### Yöntem 1: Hermes Skill olarak (önerilen)

```bash
hermes skills install https://git.softmediadesign.com/git_alhan/hermes-session-cleaner/raw/branch/main/SKILL.md
```

Skill yüklendikten sonra Hermes içinde tetiklemek için aşağıdaki komutları söylemen yeterli:

| Ne dersin? | Ne olur? |
|---|---|
| `temizlik yap` | Önce dry-run gösterir, onayını alır, sonra çalıştırır |
| `clean sessions` | Aynısı (İngilizce) |
| `sessionları temizle` | Aynısı |

Hermes agent skill'i otomatik yükler, `--dry-run` ile önizleme yapar, sana sonucu gösterip onay ister, sonra gerçek temizliği yapar.

### Yöntem 2: Manuel (git clone)

```bash
git clone https://git.softmediadesign.com/git_alhan/hermes-session-cleaner.git
cd hermes-session-cleaner
python3 hermes_cleaner.py --dry-run
```

### Yöntem 3: Tek komut (curl + run)

```bash
curl -O https://git.softmediadesign.com/git_alhan/hermes-session-cleaner/raw/branch/main/hermes_cleaner.py
python3 hermes_cleaner.py --dry-run
```

## Kullanım

```bash
# Neler olacağını gör (her zaman önce bunu çalıştır)
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

1. Tüm session'ları tarar (`~/.hermes/state.db`)
2. `< N` mesajlı session'ları **siler** (default: 5)
3. `>= N` mesajlı ama başlıksız session'lara **title üretir**

## Gereksinimler

- Hermes Agent kurulu olmalı (hermes_state modülü için)
- Title üretimi için Ollama'da `hermes3:latest` modeli

## Yapılandırma (Env Vars)

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `HERMES_CLEANER_MODEL` | `hermes3:latest` | Title üretimi için model |
| `HERMES_CLEANER_ENDPOINT` | `http://100.83.239.61:11434/v1/chat/completions` | Ollama API adresi |

```bash
# DeepSeek API ile kullanmak istersen:
export HERMES_CLEANER_ENDPOINT="https://api.deepseek.com/v1/chat/completions"
export HERMES_CLEANER_MODEL="deepseek-chat"
export HERMES_CLEANER_API_KEY="sk-..."
```

## Cron ile Otomatik Çalıştırma

```bash
# Hermes içinde:
/cron "her hafta pazar 03:00'te session temizliği yap"

# Veya manuel cron:
0 3 * * 0 cd /path/to/hermes-session-cleaner && python3 hermes_cleaner.py
```

## Projeler

Bu proje `hermes-session-ending` ile birlikte çalışır:

| Proje | Amaç | Ne zaman? |
|---|---|---|
| [session-ending](https://git.softmediadesign.com/git_alhan/hermes-session-ending) | Oturum sonu: title + save + reset | Her oturum sonunda ("ending") |
| session-cleaner (bu proje) | Toplu temizlik: sil + title | Haftalık bakım |
