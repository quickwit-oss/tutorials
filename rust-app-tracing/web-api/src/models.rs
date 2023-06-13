use serde::{Serialize, Deserialize};

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Post {
    pub user_id: i64,
    pub id: i64,
    pub title: String,
    pub body: String,
    #[serde(default)]
    pub comments: Vec<Comment>,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Comment {
    pub post_id: i64,
    pub id: i64,
    pub name: String,
    pub email: String,
    pub body: String,
}
