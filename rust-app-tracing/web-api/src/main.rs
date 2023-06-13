use actix_web::{App, HttpServer};

use tracing_actix_web::TracingLogger;
use web_api::{init_telemetry, fetch_posts_service};

const EXPORTER_ENDPOINT: &'static str = "http://localhost:7281";


#[actix_web::main]
async fn main() -> std::io::Result<()> {
    init_telemetry(EXPORTER_ENDPOINT);

    HttpServer::new(move || {
        App::new()
            .wrap(TracingLogger::default())
            .service(fetch_posts_service())
    })
    .bind(("127.0.0.1", 9000))?
    .run()
    .await
}
