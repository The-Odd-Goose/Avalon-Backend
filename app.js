const express = require("express");
const firebase = require('./firebase');

const app = express();
const port = 8080;

app.listen(port, () => {
    console.log(`Listening at http://localhost:${port}`)
})

app.get("/", (req, res) => {
    res.send(`<p>${firebase.getGame()}</p>`)
})