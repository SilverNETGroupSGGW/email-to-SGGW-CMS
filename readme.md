# Email to SGGW CMS
To łącznik pomiędzy dowolną pocztą elektroniczną z imap a systemem CMS SGGW. Wszystko napisane w pythonie z restrykcyjnym sprawdzaniem typów.
## Instalacja
### Docker
1. Zainstaluj [docker](https://docs.docker.com/engine/install/) oraz [docker-compose](https://docs.docker.com/compose/install/)
2. Sklonuj repozytorium
3. W pliku `docker-compose.yml` ustaw zmienne środowiskowe:
    - `EMAIL_HOST` - adres serwera imap, domyślnie `imap.gmail.com`
    - `EMAIL_USERNAME` - nazwa użytkownika
    - `EMAIL_PASSWORD` - hasło użytkownika
    - `EMAIL_TIMEOUT` - czas pomiędzy sprawdzaniem skrzynki w sekundach, domyślnie `20`
    - `API_URL` - adres API CMS, domyślnie `https://kampus-sggw-api.azurewebsites.net/api`
    - `API_USERNAME` - nazwa użytkownika CMS
    - `API_PASSWORD` - hasło użytkownika CMS
    - `ALLOWED_SENDERS` - lista adresów email, z których będą akceptowane wiadomości, domyślnie pusta
    - `EMAIL_PREFIX` - prefix adresu email, domyślnie pusty
4. Uruchom kontener poleceniem `docker-compose up -d`
5. Sprawdź czy wszystko działa poleceniem `docker-compose logs -f`

### Bezpośrednio
1. Zainstaluj [python](https://www.python.org/downloads/) w wersji 3.11 lub wyższej
2. Sklonuj repozytorium
3. Zainstaluj zależności poleceniem `pip install -r requirements.txt`
4. Ustaw zmienne środowiskowe:
    - `EMAIL_HOST` - adres serwera imap, domyślnie `imap.gmail.com`
    - `EMAIL_USERNAME` - nazwa użytkownika
    - `EMAIL_PASSWORD` - hasło użytkownika
    - `EMAIL_TIMEOUT` - czas pomiędzy sprawdzaniem skrzynki w sekundach, domyślnie `20`
    - `API_URL` - adres API CMS, domyślnie `https://kampus-sggw-api.azurewebsites.net/api`
    - `API_USERNAME` - nazwa użytkownika CMS
    - `API_PASSWORD` - hasło użytkownika CMS
5. Uruchom skrypt poleceniem `python main.py`

## Pull requesty
Pull requesty są mile widziane, ale proszę o zachowanie stylu kodu. Dla wygody załączony jest również folder .vscode z ustawieniami edytora oraz .devcontainer z konfiguracją kontenera deweloperskiego.