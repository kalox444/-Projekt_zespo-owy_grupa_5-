mod weather;





use serde::Serialize;
use tiny_http::{Server, Response};





fn pakowanie_struktury_do_json<T: Serialize>(dane: T) -> String { // cowkoleik T co ma naklejke serialize bierzemy i przyjmyjemy jako "dane"
    match serde_json::to_string(&dane){
        Ok(tekst) => tekst,
        Err(blad) =>  format!("Blad podczas parsowania strukry na json w main.rs -- {}", blad),
    }

}



fn main(){
    let server = match Server::http("127.0.0.1:9999"){
        Ok(dziala) => dziala,
        Err(blad) => {
            eprintln!("blad podczas uruchamiania serwera {}", blad);
            std::process::exit(1);
        }
    };


    println!("serwer dziala na htttp://127.0.0.1:9999");
    

    for req in server.incoming_requests() {
        let odpowiedz = match req.url() {
            "/weather" => match weather::pobierz_pogoda_meteo() {
                Ok(struktura) => pakowanie_struktury_do_json(struktura),
                Err(blad) => {
                    eprintln!("Blad w /weather: {}", blad);
                    blad
                }
            },
            
            _ => "404 - nie ma takiej strony".to_string(),
        };
        let _ = req.respond(Response::from_string(odpowiedz)); // wysylanie do html
    }

}

