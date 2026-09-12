# Zweryfikowany wynik testów

Data uruchomienia: 2026-09-12  
Środowisko: Python 3.13.7, Windows

```text
test_retention_keeps_only_requested_number ... ok
test_round_trip_preserves_files_and_verifies_checksums ... ok
test_unsafe_archive_path_is_rejected ... ok
test_deploy_switch_and_rollback ... ok
test_failed_healthcheck_does_not_switch_release ... ok
test_rollback_requires_previous_release ... ok
test_http_tcp_and_disk_checks_pass ... ok
test_wrong_status_and_unknown_type_are_reported ... ok

Ran 8 tests
OK
```

Dodatkowy test demonstracyjny potwierdził:

- utworzenie archiwum z dwoma plikami i poprawnym manifestem;
- ponowną weryfikację wszystkich sum kontrolnych;
- utworzenie wersjonowanego wydania;
- poprawny healthcheck pliku `index.html`;
- wskazanie aktywnego katalogu wydania.

Każdy może powtórzyć kontrolę poleceniem `python -m unittest discover -s tests -v`.
