# Service Watch

Narzędzie CLI do wykonywania kontroli HTTP, TCP, TLS i wolnego miejsca na dysku.

## Wynik

- czytelny raport JSON albo Markdown;
- osobny wynik każdej kontroli wraz z komunikatem diagnostycznym;
- kod wyjścia `0`, gdy wszystkie kontrole przejdą;
- kod wyjścia `1`, gdy przynajmniej jedna kontrola wykryje problem.

## Uruchomienie

```powershell
python -m service_watch --config .\examples\monitoring.json --format markdown --output .\demo-output\monitoring.md
```

Format konfiguracji pokazuje plik
[`examples/monitoring.json`](../examples/monitoring.json), a zachowanie programu
sprawdzają [`tests/test_service_watch.py`](../tests/test_service_watch.py).
