# OPS/LAB — automatyzacje IT z publicznym kodem

[![Portfolio](https://img.shields.io/badge/portfolio-online-5de4c7?style=for-the-badge)](https://an0th3r.github.io/ops-lab-portfolio/)
![Testy](https://img.shields.io/badge/testy-8%2F8_PASS-5de4c7?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11%2B-71a7ff?style=for-the-badge)
[![Licencja MIT](https://img.shields.io/badge/licencja-MIT-9baabc?style=for-the-badge)](LICENSE)

Repozytorium zawiera trzy małe, uruchamialne narzędzia demonstracyjne napisane
wyłącznie z użyciem biblioteki standardowej Pythona. Każde ma testy i bezpieczne
ustawienia domyślne.

**[Zobacz portfolio online](https://an0th3r.github.io/ops-lab-portfolio/)** ·
**[Wynik testów](docs/TEST-RESULTS.md)** ·
**[Opis architektury](docs/ARCHITECTURE.md)**

Strona jest publikowana bezpłatnie z katalogu `docs/` przez GitHub Pages.

## Co można tu sprawdzić

| Projekt | Co robi | Co pokazuje klientowi |
| --- | --- | --- |
| `backup_guard` | Tworzy ZIP z manifestem SHA-256, weryfikuje go, rotuje archiwa i bezpiecznie odtwarza dane | backup jest sprawdzalny, a odtworzenie blokuje niebezpieczne ścieżki |
| `service_watch` | Kontroluje HTTP, TCP, certyfikat TLS i wolne miejsce; zapisuje raport JSON lub Markdown | monitoring daje konkretną diagnozę i poprawny kod wyjścia dla automatyzacji |
| `release_guard` | Tworzy wersjonowane wydania, wykonuje healthcheck, atomowo przełącza wersję i pozwala zrobić rollback | błędne wydanie nie zastępuje działającej wersji |

## Dodatkowy projekt: animacja SVG

Trzysekundowa animacja składania płaskiej siatki w przestrzenne opakowanie,
wykonana bez zewnętrznych bibliotek. Publiczny podgląd ma znak wodny
`DEMO / PORTFOLIO`.

**[Otwórz animację](https://an0th3r.github.io/ops-lab-portfolio/animation/)** ·
**[Zobacz kod SVG](docs/animation/folding-box-demo.svg)**

## Szybki test

Wymagany jest Python 3.11 lub nowszy. Nie trzeba instalować żadnych bibliotek.

```powershell
python -m unittest discover -s tests -v
```

Oczekiwany rezultat: `Ran 8 tests` oraz `OK`.

## Przykłady

### 1. Backup z kontrolą sum

```powershell
python -m backup_guard create .\examples\sample-data --destination .\demo-output\backups --keep 5
python -m backup_guard verify .\demo-output\backups\NAZWA_ARCHIWUM.zip
python -m backup_guard restore .\demo-output\backups\NAZWA_ARCHIWUM.zip --target .\demo-output\restore
```

### 2. Monitoring i raport

```powershell
python -m service_watch --config .\examples\monitoring.json --format markdown --output .\demo-output\monitoring.md
```

Program kończy się kodem `0`, gdy wszystkie kontrole przejdą, albo `1`, gdy
co najmniej jedna kontrola wykryje problem. Dzięki temu można go uruchamiać z
Harmonogramu zadań, crona lub pipeline'u CI.

### 3. Wdrożenie i rollback

```powershell
python -m release_guard deploy .\examples\sample-app --target .\demo-output\app --health-file index.html
python -m release_guard status --target .\demo-output\app
python -m release_guard rollback --target .\demo-output\app
```

## Granice projektu

To portfolio techniczne prezentujące rozwiązania przygotowane i przetestowane
w środowisku demonstracyjnym. Narzędzia nie pobierają haseł, nie zmieniają zapory
i nie łączą się przez SSH. Przed użyciem produkcyjnym zakres backupu, retencję,
alerty i procedurę powrotu trzeba dopasować do konkretnego serwera.

## Struktura

```text
backup_guard/       tworzenie, weryfikacja i odtwarzanie kopii
service_watch/      kontrole usług i generowanie raportów
release_guard/      wersjonowane wdrożenia i rollback
tests/              testy jednostkowe oraz integracyjne
examples/           bezpieczne dane i konfiguracje demonstracyjne
docs/               strona portfolio, wynik testów i opis architektury
docs/animation/     animacja SVG i samodzielna strona podglądu
```

## Licencja

MIT — kod można przeglądać, uruchamiać i rozwijać. Dane dostępowe i informacje
o prawdziwych serwerach nie są częścią repozytorium.
