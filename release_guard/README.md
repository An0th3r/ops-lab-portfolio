# Release Guard

Narzędzie CLI do tworzenia wersjonowanych wydań i bezpiecznego przełączania
aktywnej wersji aplikacji.

## Zasada działania

1. Kopiuje nowe wydanie do osobnego katalogu.
2. Wykonuje healthcheck wskazanego pliku.
3. Przełącza aktywną wersję dopiero po pozytywnym wyniku.
4. Zachowuje poprzednią wersję, aby można było wykonać rollback.

## Uruchomienie

```powershell
python -m release_guard deploy .\examples\sample-app --target .\demo-output\app --health-file index.html
python -m release_guard status --target .\demo-output\app
python -m release_guard rollback --target .\demo-output\app
```

Nieudany healthcheck i operację rollbacku pokrywają
[`tests/test_release_guard.py`](../tests/test_release_guard.py).
