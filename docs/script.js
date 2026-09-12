const filters = document.querySelectorAll('.filter');
const cards = document.querySelectorAll('.project-card');

const githubPagesHost = window.location.hostname.match(/^([a-z0-9-]+)\.github\.io$/i);
const repositoryName = window.location.pathname.split('/').filter(Boolean)[0];
const repositoryUrl = githubPagesHost && repositoryName
  ? `https://github.com/${githubPagesHost[1]}/${repositoryName}`
  : 'https://github.com/An0th3r/ops-lab-portfolio';

document.querySelectorAll('[data-repo-path]').forEach((link) => {
  link.href = `${repositoryUrl}/${link.dataset.repoPath}`;
  link.target = '_blank';
  link.rel = 'noreferrer';
});

filters.forEach((button) => {
  button.addEventListener('click', () => {
    filters.forEach((item) => {
      const active = item === button;
      item.classList.toggle('is-active', active);
      item.setAttribute('aria-pressed', String(active));
    });
    const filter = button.dataset.filter;
    cards.forEach((card) => {
      const visible = filter === 'all' || card.dataset.category.split(' ').includes(filter);
      card.hidden = !visible;
    });
  });
});

const cases = {
  backup: {
    title: 'Backup z kontrolą odtworzenia',
    intro: 'Automatyzacja jest przydatna dopiero wtedy, gdy wiadomo, że kopię da się odtworzyć.',
    problem: 'Kopie wykonywane ręcznie i bez regularnej kontroli. Brak jasnej odpowiedzi, które archiwum jest poprawne.',
    solution: 'Osobne archiwum bazy i plików, rotacja według ustalonej retencji, suma kontrolna i dziennik przebiegu.',
    check: 'Test rozpakowania, import do tymczasowej bazy oraz alarm, gdy kopia nie powstanie lub ma nieprawidłowy rozmiar.',
    handoff: 'Skrypt, harmonogram, lokalizacja archiwów i krótka instrukcja ręcznego odtworzenia.'
  },
  monitoring: {
    title: 'Monitoring i alerty usług',
    intro: 'Najważniejsze sygnały w jednym raporcie, bez zalewania właściciela serwera przypadkowymi komunikatami.',
    problem: 'Awaria wychodzi na jaw dopiero po wiadomości od klienta. Brakuje informacji, czy zawiodła aplikacja, proxy czy baza.',
    solution: 'Kontrole HTTP, procesów, kontenerów, wolnego miejsca i terminu ważności certyfikatu uruchamiane cyklicznie.',
    check: 'Symulowane zatrzymanie usługi, zapełnienie progu testowego i sprawdzenie, czy alarm zawiera użyteczne dane.',
    handoff: 'Lista kontroli, progi alarmowe, kanał powiadomień i procedura pierwszej reakcji.'
  },
  hardening: {
    title: 'Audyt i utwardzenie VPS',
    intro: 'Bezpieczne zmiany etapami, z zachowaniem aktywnej sesji administracyjnej i drogą powrotu.',
    problem: 'Nieznane konta, usługi nasłuchujące publicznie, logowanie hasłem i brak uporządkowanej polityki aktualizacji.',
    solution: 'Inwentaryzacja, ograniczenie ekspozycji, klucze SSH, reguły zapory, blokowanie powtarzanych prób i przegląd logów.',
    check: 'Ponowne logowanie przed zamknięciem starej sesji, kontrola wymaganych portów i test działania aplikacji.',
    handoff: 'Raport stanu przed i po, lista zmian oraz informacja, których ryzyk nie usuwano bez zgody właściciela.'
  },
  cloudflare: {
    title: 'Cloudflare bez efektów ubocznych',
    intro: 'Konfiguracja ochrony i cache nie może psuć logowania, płatności ani panelu administracyjnego.',
    problem: 'Losowe reguły cache, pętla przekierowań HTTPS albo ochrona blokująca prawidłowych użytkowników sklepu.',
    solution: 'Porządek w DNS, właściwy tryb SSL, selektywne reguły cache i wyłączenia dla dynamicznych ścieżek.',
    check: 'Test strony anonimowej, konta użytkownika, koszyka, panelu oraz czyszczenia cache po zmianie treści.',
    handoff: 'Lista rekordów i reguł, opis wyłączeń oraz sposób szybkiego przywrócenia poprzedniego ruchu DNS.'
  },
  wordpress: {
    title: 'Migracja WordPress z planem powrotu',
    intro: 'Strona, baza, certyfikat i DNS są traktowane jako jeden proces, nie cztery niezależne zadania.',
    problem: 'Ryzyko brakujących plików, błędnych adresów w bazie, niedziałających formularzy i przerwy po zmianie DNS.',
    solution: 'Kopia źródła, przygotowanie celu, import danych, zmiana adresów, konfiguracja HTTPS i kontrolowane przełączenie.',
    check: 'Najważniejsze podstrony, media, formularze, logowanie, przekierowania i odpowiedzi serwera po zmianie.',
    handoff: 'Kopia migracyjna, dane o wersjach, lista wykonanych zmian oraz termin usunięcia starego środowiska.'
  },
  sql: {
    title: 'Odtworzenie i migracja SQL',
    intro: 'Najpierw zabezpieczenie danych i diagnoza, dopiero później reinstalacja lub migracja usługi.',
    problem: 'Niedziałająca instancja, błędna aktualizacja albo konieczność przeniesienia bazy bez pełnej wiedzy o zależnościach.',
    solution: 'Kopia katalogów i eksport logiczny, zgodna wersja silnika, kontrolowany import oraz aktualizacja połączenia aplikacji.',
    check: 'Liczba kluczowych rekordów, logi importu, prawa użytkowników, zapytanie kontrolne i start aplikacji.',
    handoff: 'Raport diagnozy, plik kopii, opis wersji i polecenia potrzebne do ponownego odtworzenia.'
  },
  deployment: {
    title: 'Powtarzalne wdrożenie bez chaosu',
    intro: 'Każde wydanie wykonuje te same kroki, a nie zależy od pamięci osoby klikającej na serwerze.',
    problem: 'Ręczne kopiowanie plików, brak informacji o aktualnej wersji i stres przy wycofaniu nieudanego wydania.',
    solution: 'Wersjonowane paczki, kontrola konfiguracji, automatyczny healthcheck i przełączenie na nową wersję po teście.',
    check: 'Próba wdrożenia poprawnej i celowo wadliwej wersji oraz potwierdzenie, że rollback przywraca usługę.',
    handoff: 'Skrypt, checklista publikacji, lokalizacja logów i instrukcja samodzielnego wycofania wersji.'
  }
};

const dialog = document.querySelector('.case-dialog');
const closeDialog = document.querySelector('.dialog-close');

document.querySelectorAll('.case-button').forEach((button) => {
  button.addEventListener('click', () => {
    const data = cases[button.dataset.case];
    if (!data) return;
    document.querySelector('#case-title').textContent = data.title;
    document.querySelector('#case-intro').textContent = data.intro;
    document.querySelector('#case-problem').textContent = data.problem;
    document.querySelector('#case-solution').textContent = data.solution;
    document.querySelector('#case-check').textContent = data.check;
    document.querySelector('#case-handoff').textContent = data.handoff;
    dialog.showModal();
  });
});

closeDialog.addEventListener('click', () => dialog.close());
dialog.addEventListener('click', (event) => {
  if (event.target === dialog) dialog.close();
});

const copyButton = document.querySelector('.copy-brief');
const copyStatus = document.querySelector('.copy-status');
copyButton.addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(copyButton.dataset.copy);
    copyStatus.textContent = 'Wzór wiadomości skopiowany.';
  } catch {
    copyStatus.textContent = 'Nie udało się skopiować. Zaznacz tekst ręcznie.';
  }
  window.setTimeout(() => { copyStatus.textContent = ''; }, 3000);
});

document.querySelectorAll('details').forEach((item) => {
  item.addEventListener('toggle', () => {
    const marker = item.querySelector('summary span');
    marker.textContent = item.open ? '−' : '+';
  });
});
