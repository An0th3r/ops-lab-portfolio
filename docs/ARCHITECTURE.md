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

ai_assistant
  widget na stronie -> API Cloudflare Worker -> ograniczenie zapytań
                                                |
                                                v
                                 prywatna baza wiedzy + model AI
                                                |
                                                v
                                    odpowiedź bez ujawniania klucza
```

## Założenia bezpieczeństwa

- Backup jest uznawany za poprawny dopiero po sprawdzeniu wszystkich sum.
- Odtwarzanie blokuje ścieżki absolutne i próby wyjścia poza katalog docelowy.
- Błąd pojedynczej kontroli monitoringu nie przerywa pozostałych kontroli.
- Nieznany rodzaj kontroli jest błędem, a nie pominiętym wpisem.
- Nowa wersja nie staje się aktywna przed healthcheckiem.
- Stan aktywnego wydania jest zapisywany atomowo.
- Przeglądarka nie otrzymuje klucza ani prywatnej bazy wiedzy asystenta.
- Endpoint czatu akceptuje wyłącznie wskazane domeny, krótki kontekst i ograniczoną liczbę zapytań.
- Rozmowy nie są zapisywane w bazie przez demonstracyjną wersję Workera.

Kod backendu asystenta, prompt i baza wiedzy pozostają prywatne. Publiczne są
wyłącznie opis architektury oraz zminimalizowany plik widgetu wymagany przez
przeglądarkę.
