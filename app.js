const express = require("express");
const firebase = require('./firebase');

const bodyParser = require('body-parser');

const app = express();
const port = 8080;

app.listen(port, () => {
    console.log(`Listening at http://localhost:${port}`)
})

app.use(bodyParser.json()) // we'll be parsing json

// so here we'll have an endpoint to create a game
// it'll require a user of form:
// {
//  photoURL, userName, userId
// }
app.post("/createGame", (req, res) => {
    
    try {
        console.log("Trying to create a new game");

        firebase.createGame(res.json(req.body));

        res.send("Went through!");
    } catch (error) {
        res.status(500).json({
            error: "something went wrong!"
        })
    }
    
})