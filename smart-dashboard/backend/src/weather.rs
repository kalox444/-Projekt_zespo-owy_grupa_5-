use serde::{Deserialize, Serialize}; // Z json -> na strukture rust, z rust -> json


#[derive(Deserialize)] // rozpakowanie jsona do surowego tekstu
struct ApiResponse {
    current: DanePobraneAPI,
}



#[derive(Deserialize)]
struct DanePobraneAPI {
    temperature_2m: f64,
    surface_pressure: f64,
    time: String,
}


#[derive(Serialize)]
pub struct Pogoda_do_html {
    pub temp: i32,
    pub cisnienie: i32,
    pub godzina: String,
}




pub fn pobierz_pogoda_meteo() -> Result<Pogoda_do_html, String> {

    let url = "https://api.open-meteo.com/v1/forecast?latitude=54.341&longitude=18.362&current=temperature_2m,surface_pressure&timezone=Europe%2FWarsaw";


    // let mut response = ureq::get(url).call().unwrap();

    // let text = response.body_mut().read_to_string().unwrap();

    // println!("{text}");


    // wyslamy zadanie pobrania jsona
    let mut response = match ureq::get(url).call() { // ureql.get buduje, a call faktycznie wysyla
        Ok(resp) => resp,
        Err(err) => {
            return Err(format!("blad poczas pobierania api meter {err}"));
        }
    };

    


    //pobieramy bajty i sklejamy w stringa
    //println!("{:?}", response) // wypisanie calego tekstu jaki dostajemy z meteo
    let text = match response.body_mut().read_to_string() {
        Ok(t) => t,
        Err(err) => {
            return Err(format!("blad poczas czytania tresci meteo {err} "));
        }
    };

    //println!("Czyste dane pgoodowe to {}", text);



    // bierzmy tego dlugiego stringa
    let dane: ApiResponse = match serde_json::from_str(&text) { // pozyczjamy &text do czytania, wynik w "dane" o ksztaltcie ApiResponse
        Ok(parsed) => parsed,
        Err(err) => {
            return Err(format!("blad podczas odpakowywania json {err}"));
        }
    };




    //pakowanie do html
    let temp = dane.current.temperature_2m.round() as i32;
    let cisnienie = dane.current.surface_pressure.round() as i32;
    let godzina = match dane.current.time.split_once('T') {
        Some((_, godzina_po_t)) => godzina_po_t.to_string(),
        None => "brak".to_string(),
    };

    //println!("Żukowo ({godzina}): {temp}°C, {cisnienie} hPa");



    Ok(Pogoda_do_html{
        temp,
        cisnienie,
        godzina,
    })

}