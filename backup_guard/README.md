# Backup Guard

Małe narzędzie CLI do tworzenia, sprawdzania i bezpiecznego odtwarzania kopii ZIP.

## Co zabezpiecza

- zapisuje manifest plików i sumy SHA-256;
- automatycznie weryfikuje nowo utworzone archiwum;
- usuwa najstarsze kopie ponad ustaloną retencję;
- przed odtworzeniem ponownie sprawdza integralność;
- blokuje ścieżki próbujące wyjść poza katalog docelowy.

## Uruchomienie

```powershell
python -m backup_guard create .\examples\sample-data --destination .\demo-output\backups --keep 5
python -m backup_guard verify .\demo-output\backups\NAZWA_ARCHIWUM.zip
python -m backup_guard restore .\demo-output\backups\NAZWA_ARCHIWUM.zip --target .\demo-output\restore
```

Kod używa wyłącznie biblioteki standardowej Pythona. Scenariusze poprawne i
awaryjne znajdują się w [`tests/test_backup_guard.py`](../tests/test_backup_guard.py).
