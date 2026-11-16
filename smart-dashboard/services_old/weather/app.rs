#![forbid(unsafe_code)] // Dyrektywa kompilatora: całkowity zakaz używania bloku `unsafe` w całym pliku (gwarancja bezpieczeństwa pamięci).
#![deny(clippy::unwrap_used, clippy::expect_used, clippy::panic)] // Nakazuje audytorowi `cargo clippy` traktować `.unwrap()`, `.expect()` i `panic!()` jako błędy kompilacji (zakaz nagłego wywalania programu).

use std::process; // Importuje moduł `process` z biblioteki standardowej, potrzebny do zamknięcia programu (`process::exit`) przy błędzie startu.
use std::time::Duration; // Importuje typ `Duration`, który reprezentuje odcinek czasu (np. 5 sekund limitu na odpowiedź sieciową).
use serde::Deserialize; // Importuje makro `Deserialize` z biblioteki `serde`, które automatycznie zamienia surowy tekst JSON na struktury Rusta.
use serde_json::json; // Importuje makro `json!`, pozwalające wygodnie budować obiekty JSON w kodzie (odpowiednik `jsonify` w Pythonie).
use tiny_http::{Header, Method, Request, Response, Server, StatusCode}; // Importuje elementy lekkiego serwera HTTP (`tiny_http`) do odbierania i wysyłania zapytań.

const WEATHER_URL: &str = "https://api.open-meteo.com/v1/forecast?latitude=54.341&longitude=18.362&current=temperature_2m,surface_pressure&timezone=Europe%2FWarsaw"; // Stała tekstowa (`&str`) z adresem API Open-Meteo dla Żukowa; `const` oznacza wartość niezmienną wpisaną na stałe w plik wykonywalny.
const TIMEOUT: Duration = Duration::from_secs(5); // Stała określająca maksymalny czas oczekiwania na odpowiedź z serwera pogodowego (5 sekund).
const MAX_BYTES: u64 = 16_384; // Stała (64-bitowa liczba bez znaku) ograniczająca rozmiar pobieranej odpowiedzi do 16 KB (chroni RAM Raspberry Pi przed przepełnieniem).

#[derive(Deserialize)] // Atrybut automatycznie generujący kod parsujący JSON-a dla poniższej struktury `ApiResponse`.
struct ApiResponse { // Definicja głównej struktury odpowiadającej zewnętrznemu obiektowi JSON zwracanemu przez Open-Meteo.
    current: CurrentWeather, // Wymaga, aby w JSON-ie istniało pole `"current"` i pasowało do struktury `CurrentWeather` (inaczej parser zwróci błąd).
} // Koniec definicji struktury `ApiResponse`.

#[derive(Deserialize)] // Automatycznie generuje parser JSON-a dla zagnieżdżonego obiektu `"current"`.
struct CurrentWeather { // Definicja struktury opisującej dokładnie te 3 pola, których szukamy w sekcji `"current"` z API.
    temperature_2m: f64, // Wymaga, aby pole `temperature_2m` było liczbą zmiennoprzecinkową 64-bitową (`float`); odrzuci tekst lub `null`.
    surface_pressure: f64, // Wymaga, aby pole `surface_pressure` było liczbą zmiennoprzecinkową 64-bitową (`float`).
    time: String, // Wymaga, aby pole `time` było dynamicznym ciągiem znaków (`String`), np. `"2026-11-16T14:00"`.
} // Koniec definicji struktury `CurrentWeather`.

#[derive(Debug, PartialEq)] // `Debug` umożliwia wypisanie struktury w testach i logach, a `PartialEq` pozwala porównywać dwie struktury znakiem `==`.
struct Pogoda { // Definicja naszej własnej, oczyszczonej struktury danych, którą wyślemy dalej do frontendu.
    temp: i32, // Zaokrąglona temperatura zapisana jako 32-bitowa liczba całkowita ze znakiem (`int`).
    cisnienie: i32, // Zaokrąglone ciśnienie atmosferyczne jako 32-bitowa liczba całkowita (`int`).
    godzina: String, // Wycięta godzina w formacie `"HH:MM"` jako ciąg znaków (`String`).
} // Koniec definicji struktury `Pogoda`.

fn waliduj_dane(dane: CurrentWeather) -> Result<Pogoda, &'static str> { // Funkcja przejmuje na własność `dane` i zwraca pudełko `Result`: sukces (`Ok(Pogoda)`) lub statyczny komunikat błędu (`Err(&'static str)`).
    if !(-60.0..=60.0).contains(&dane.temperature_2m) { // Sprawdza, czy temperatura mieści się w fizycznym przedziale od -60.0 do +60.0 stopni Celsjusza (`..=` oznacza przedział domknięty).
        return Err("Temperatura poza zakresem fizycznym"); // Jeśli temperatura jest nierealna (np. awaria czujnika), natychmiast przerywa funkcję i zwraca błąd `Err`.
    } // Koniec bloku sprawdzającego temperaturę.
    if !(850.0..=1100.0).contains(&dane.surface_pressure) { // Sprawdza, czy ciśnienie mieści się w realnym zakresie atmosferycznym od 850 do 1100 hPa.
        return Err("Ciśnienie poza zakresem fizycznym"); // Jeśli ciśnienie jest poza normą, natychmiast przerywa funkcję i zwraca błąd `Err`.
    } // Koniec bloku sprawdzającego ciśnienie.
    let (_, godzina) = dane.time.split_once('T').ok_or("Nieprawidłowy format czasu")?; // Dzieli tekst w miejscu litery `'T'` (`_` odrzuca datę); `.ok_or(...)` zamienia brak `'T'` na `Err`, a operator `?` natychmiast przerywa funkcję przy błędzie.

    Ok(Pogoda { // Zwraca wariant sukcesu `Ok` zawierający nowo utworzoną i zweryfikowaną strukturę `Pogoda`.
        temp: dane.temperature_2m.round() as i32, // Zaokrągla temperaturę do pełnej liczby (`.round()`) i rzutuje z typu `f64` na liczbę całkowitą `i32` (`as i32`).
        cisnienie: dane.surface_pressure.round() as i32, // Zaokrągla ciśnienie do pełnej liczby i rzutuje z `f64` na `i32`.
        godzina: godzina.to_owned(), // Tworzy niezależną kopię wycinka godziny jako nowy obiekt `String` (`.to_owned()`), aby mogła opuścić funkcję.
    }) // Koniec tworzenia struktury `Pogoda` oraz zwracania wyniku `Ok`.
} // Koniec funkcji `waliduj_dane`.

fn pobierz_pogode(agent: &ureq::Agent) -> Result<Pogoda, String> { // Funkcja pożycza tylko do odczytu klienta HTTP (`&ureq::Agent`) i zwraca `Result` z gotową `Pogodą` albo opisem błędu `String`.
    let mut resp = agent.get(WEATHER_URL).call().map_err(|e| e.to_string())?; // Wysyła żądanie GET (kody 404/500 automatycznie zwracają błąd); `mut` pozwala odczytać treść, `.map_err(...)` zamienia błąd na tekst, a `?` przerywa przy awarii.
    let body = resp // Rozpoczyna odczyt treści odpowiedzi HTTP i przypisuje wynik do zmiennej `body`.
        .body_mut() // Pobiera modyfikowalny dostęp do strumienia bajtów z odpowiedzi serwera.
        .with_config() // Otwiera konfigurator czytania strumienia, aby nałożyć ograniczenia bezpieczeństwa.
        .limit(MAX_BYTES) // Ustawia twardy bezpiecznik: jeśli odpowiedź przekroczy 16 384 bajty, pobieranie zostanie natychmiast przerwane.
        .read_to_string() // Odczytuje bajty ze strumienia i sprawdza, czy tworzą poprawny tekst UTF-8.
        .map_err(|e| e.to_string())?; // Jeśli przekroczono limit bajtów lub zerwano połączenie, zamienia błąd na `String` i przerywa funkcję (`?`).

    let parsed: ApiResponse = serde_json::from_str(&body).map_err(|e| e.to_string())?; // Parsuje pożyczony tekst JSON (`&body`) do struktury `ApiResponse`; jeśli brakuje pól lub typy się nie zgadzają, zwraca błąd (`?`).
    waliduj_dane(parsed.current).map_err(str::to_owned) // Przekazuje rozpakowane dane do naszej walidacji zakresów i zamienia ewentualny statyczny błąd `&str` na `String` (`str::to_owned`).
} // Koniec funkcji `pobierz_pogode`.

fn wyslij_json(req: Request, status: u16, body: String) { // Funkcja przejmuje żądanie HTTP (`req`), kod statusu (np. 200) oraz treść JSON (`body`) i wysyła odpowiedź do klienta.
    let mut res = Response::from_string(body).with_status_code(StatusCode(status)); // Tworzy modyfikowalny obiekt odpowiedzi HTTP (`mut res`) z podanym tekstem oraz kodem statusu.
    if let Ok(header) = Header::from_bytes("Content-Type", "application/json") { // Próbuje utworzyć nagłówek HTTP `Content-Type: application/json`; jeśli się uda (`Ok(header)`), wchodzi do bloku `if`.
        res.add_header(header); // Dokleja nagłówek do odpowiedzi, aby przeglądarka i JavaScript wiedziały, że otrzymują format JSON.
    } // Koniec bloku dodawania nagłówka.
    let _ = req.respond(res); // Wysyła gotową odpowiedź przez sieć; `let _ =` świadomie ignoruje ewentualny błąd (np. gdy przeglądarka zamknęła kartę przed odbiorem).
} // Koniec funkcji `wyslij_json`.

fn main() { // Główna funkcja `main()` — punkt startowy każdego programu w języku Rust.
    let server = match Server::http("0.0.0.0:5000") { // Próbuje otworzyć gniazdo sieciowe na wszystkich interfejsach (`0.0.0.0`, wymagane w kontenerach) i porcie `5000`; `match` wymusza obsługę obu wyników.
        Ok(s) => s, // Jeśli port 5000 jest wolny, wyjmuje uruchomiony serwer z pudełka `Ok(s)` i przypisuje go do zmiennej `server`.
        Err(e) => { // Jeśli port jest zajęty lub brakuje uprawnień, przechodzi do obsługi błędu `Err(e)`.
            eprintln!("FATAL: nie można uruchomić serwera: {e}"); // Wypisuje komunikat o błędzie krytycznym na standardowe wyjście błędów (`stderr`), które zbiera Kubernetes.
            process::exit(1); // Natychmiast kończy proces z kodem `1` (sygnał dla Kubernetesa, że kontener nie wystartował i trzeba go zrestartować).
        } // Koniec gałęzi błędu `Err`.
    }; // Koniec wyrażenia `match` dla startu serwera.

    let config = ureq::Agent::config_builder().timeout_global(Some(TIMEOUT)).build(); // Tworzy konfigurację klienta HTTP z globalnym limitem czasu 5 sekund na całe połączenie.
    let agent = ureq::Agent::new_with_config(config); // Buduje wielokrotnego użytku klienta HTTP (`agent`), który zarządza pulą połączeń z zewnętrznym API.
    println!("INFO: weather-service (Rust) działa na porcie 5000"); // Wypisuje informację startową na standardowe wyjście (`stdout`).

    for req in server.incoming_requests() { // Nieskończona pętla blokująca, która odbiera kolejne przychodzące żądania HTTP (`req`) jedno po drugim.
        let path = req.url().split('?').next().unwrap_or(""); // Bierze adres URL żądania, odcina ewentualne parametry po znaku `?` i pobiera pierwszą część (czystą ścieżkę, np. `"/api/weather"`).
        match (req.method(), path) { // Sprawdza jednocześnie metodę HTTP (np. `GET`) oraz ścieżkę URL (odpowiednik `@app.route` z Flaska).
            (&Method::Get, "/health") => wyslij_json(req, 200, json!({"status": "ok"}).to_string()), // Jeśli przyszło `GET /health` (od Kubernetesa), odsyła kod `200` i `{"status":"ok"}`.
            (&Method::Get, "/api/weather") => match pobierz_pogode(&agent) { // Jeśli przyszło `GET /api/weather`, wywołuje `pobierz_pogode` i dopasowuje wynik `Result`.
                Ok(p) => wyslij_json(req, 200, json!({"temp": p.temp, "cisnienie": p.cisnienie, "godzina": p.godzina}).to_string()), // Przy sukcesie (`Ok(p)`) odsyła kod `200` i JSON ze sformatowanymi danymi pogodowymi.
                Err(err) => { // Przy jakimkolwiek błędzie sieci, timeoutu lub walidacji danych wchodzi w gałąź `Err(err)`.
                    eprintln!("ERROR: {err}"); // Zapisuje dokładną przyczynę awarii do logów kontenera (`kubectl logs`).
                    wyslij_json(req, 502, json!({"temp": "brak sieci", "cisnienie": "-", "godzina": "-"}).to_string()); // Odsyła kod `502 Bad Gateway` oraz bezpieczny JSON zastępczy, żeby kafelek na stronie nie padł.
                } // Koniec gałęzi błędu pobierania pogody.
            }, // Koniec obsługi ścieżki `"/api/weather"`.
            _ => wyslij_json(req, 404, json!({"error": "NOT_FOUND"}).to_string()), // Wzorzec `_` łapie każdą inną ścieżkę lub metodę (np. `POST`) i zwraca błąd `404 Not Found`.
        } // Koniec bloku `match` routingu.
    } // Koniec pętli odbierającej żądania HTTP.
} // Koniec funkcji `main()`.

#[cfg(test)] // Dyrektywa kompilacji warunkowej: ten moduł jest kompilowany wyłącznie podczas `cargo test` i nie trafia do finalnego pliku binarnego.
mod tests { // Deklaracja wewnętrznego modułu zawierającego testy jednostkowe.
    use super::*; // Importuje wszystkie funkcje i struktury z nadrzędnego pliku, aby testy miały do nich dostęp.

    #[test] // Atrybut oznaczający poniższą funkcję jako automatyczny test jednostkowy.
    fn test_poprawna_pogoda() { // Definicja testu sprawdzającego poprawne zaokrąglanie i wycinanie godziny.
        let wejscie = CurrentWeather { temperature_2m: 11.6, surface_pressure: 1003.4, time: "2026-11-16T14:00".into() }; // Tworzy sztuczne dane wejściowe z API; `.into()` automatycznie zamienia tekst `&str` na `String`.
        assert_eq!(waliduj_dane(wejscie), Ok(Pogoda { temp: 12, cisnienie: 1003, godzina: "14:00".into() })); // Sprawdza (`assert_eq!`), czy funkcja zwróciła dokładnie `12`, `1003` i `"14:00"`; jeśli nie, test obleje.
    } // Koniec testu `test_poprawna_pogoda`.

    #[test] // Oznacza kolejną funkcję jako osobny test jednostkowy.
    fn test_odrzuca_awarie_czujnika() { // Definicja testu sprawdzającego odporność na uszkodzone odczyty czujnika.
        let awaria = CurrentWeather { temperature_2m: 999.0, surface_pressure: 1000.0, time: "2026-11-16T14:00".into() }; // Symuluje błędny odczyt temperatury `999.0` stopni Celsjusza.
        assert!(waliduj_dane(awaria).is_err()); // Potwierdza (`assert!`), że funkcja `waliduj_dane` poprawnie odrzuciła te dane, zwracając `Err`.
    } // Koniec testu `test_odrzuca_awarie_czujnika`.
} // Koniec modułu testów `tests`.