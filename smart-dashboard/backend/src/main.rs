mod weather;





use serde::Serialize;
use serde_json::json;
use tiny_http::{Header, Method, Request, Response, Server, StatusCode};




fn pakowanie_struktury_do_json<T: Serialize>(dane: T) -> String { // cowkoleik T co ma naklejke serialize bierzemy i przyjmyjemy jako "dane"


}
