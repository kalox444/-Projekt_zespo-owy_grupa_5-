fn main(){

    let url = "https://api.open-meteo.com/v1/forecast?latitude=54.341&longitude=18.362&current=temperature_2m,surface_pressure&timezone=Europe%2FWarsaw";


    let mut response = ureq::get(url).call().unwrap();

    let text = response.body_mut().read_to_string().unwrap();

    println!("{text}");


}