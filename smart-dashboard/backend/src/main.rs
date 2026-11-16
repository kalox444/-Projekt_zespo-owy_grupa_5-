mod weather;





use serde::Serialize;




fn pakowanie_struktury_do_json<T: Serialize>(dane: T) -> String { // cowkoleik T co ma naklejke serialize bierzemy i przyjmyjemy jako "dane"
    match serde_json::to_string(&dane){
        Ok(tekst) => tekst,
        Err(blad) =>  format!("Blad podczas parsowania strukry na json w main.rs -- {}", blad),
    }

}
