# Architektura demonstracyjna

```text
backup_guard
  źródła -> archiwum tymczasowe -> manifest SHA-256 -> weryfikacja -> rotacja
                                                        |
                                                        v
                                              bezpieczne odtworzenie

service_watch
  monitoring.json -> HTTP / TCP / TLS / DISK -> wspólny wynik -> JSON / Markdown
                                                          |
                                                          v
                                                     exit code 0/1

release_guard
  katalog źródłowy -> nowe wersjonowane wydanie -> healthcheck
                                                   |        |
                                                sukces    błąd
                                                   |        |
                                                   v        v
                                           atomowe przełączenie  brak zmiany
                                                   |
                                                   v
                                                rollback
```

## Założenia bezpieczeństwa

- Backup jest uznawany za poprawny dopiero po sprawdzeniu wszystkich sum.
- Odtwarzanie blokuje ścieżki absolutne i próby wyjścia poza katalog docelowy.
- Błąd pojedynczej kontroli monitoringu nie przerywa pozostałych kontroli.
- Nieznany rodzaj kontroli jest błędem, a nie pominiętym wpisem.
- Nowa wersja nie staje się aktywna przed healthcheckiem.
- Stan aktywnego wydania jest zapisywany atomowo.

