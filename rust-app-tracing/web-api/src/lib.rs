mod telemetry;
mod models;

use futures::StreamExt;
use rand::seq::SliceRandom;
pub use telemetry::init_telemetry;
pub use models::{Post, Comment};

use anyhow::anyhow;
use reqwest::{Client, StatusCode};
use serde::{de::DeserializeOwned};

use actix_web::{get, web, Error, HttpResponse};
use tracing::instrument;

const BASE_API_URL: &'static str = "https://jsonplaceholder.typicode.com";

// The service actix-web will run on /posts
pub fn fetch_posts_service() -> actix_web::Scope {
    web::scope("/posts")
        .service(get_posts)
}

// The get_post handler
#[instrument(level = "info", name = "get_posts", skip_all)]
#[get("")]
async fn get_posts() -> Result<HttpResponse, Error> {
    // Randomly simulate errors in request handling
    let choices = [200, 400, 401, 200, 500, 501, 200, 500];
    let mut rng = rand::thread_rng();
    let choice = choices.choose(&mut rng)
        .unwrap()
        .clone();
    match choice {
        400..=401 => Ok(HttpResponse::new(StatusCode::from_u16(choice).unwrap())),
        500..=501 => Ok(HttpResponse::new(StatusCode::from_u16(choice).unwrap())),
        _ => {
            let posts = fetch_posts(20)
                .await
                .map_err(actix_web::error::ErrorInternalServerError)?;
            Ok(HttpResponse::Ok().json(posts))
        }
    }
}

// Fetching posts with a limit.
#[instrument(level = "info", name = "fetch_posts")]
async fn fetch_posts(limit: usize) -> anyhow::Result<Vec<Post>> {
    let client = Client::new();
    let url = format!("{}/posts", BASE_API_URL);
    let mut posts: Vec<Post> = request_url(&client, &url).await?;
    posts.truncate(limit);
    let post_idx_to_ids: Vec<(usize, i64)> = posts.iter().enumerate().map(|(idx, post)| (idx, post.id)).collect();

    // fetch post comments one after another.
    // for (index, post_id) in post_idx_to_ids {
    //     let comments = fetch_comments(&client, post_id).await?;
    //     posts[index].comments = comments
    // }

    // fetch post comments concurrently.
    let tasks: Vec<_> = post_idx_to_ids
        .into_iter()
        .map(|(index, post_id)| {
            let moved_client = client.clone();
            async move {
                let comments_fetch_result = fetch_comments(&moved_client, post_id).await;
                (index, comments_fetch_result)
            }
        })
        .collect();
    let mut stream = futures::stream::iter(tasks)
        .buffer_unordered(10);
    while let Some((index, comments_fetch_result)) = stream.next().await {
        let comments = comments_fetch_result?;
        posts[index].comments = comments;
    }

    Ok(posts)
}

// Fetching comments of a specific post
#[instrument(level = "info", name = "fetch_comments", skip(client))]
async fn fetch_comments(client: &Client, post_id: i64) ->  anyhow::Result<Vec<Comment>> {
    let url = format!("{}/posts/{}/comments", BASE_API_URL, post_id);
    let comments: Vec<Comment> = request_url(&client, &url).await?;
    Ok(comments)
}

// A helper for sending get request and deserializing the json response.
async fn request_url<T: DeserializeOwned>(client: &Client, url: &str) -> anyhow::Result<T> {
    let response = client.get(url)
        .send()
        .await?;
    match response.status() {
        reqwest::StatusCode::OK =>
            response.json::<T>()
            .await
            .map_err(|err| anyhow!(err.to_string()))
        ,
        _ => Err(anyhow!(format!("Request error with statusCode `{}`", response.status()))),
    }
}
