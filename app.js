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

app.post("/createGame", async (req, res) => {


    // here we'll type check somehow

    await firebase.createGame(res.json(req.body))
        .then(code => {
            res.send({
                gameId: code
            })
        })
        .catch(error => {
            res.send({
                error
            }).catch(err => {
                res.send("Something went wrong")
            })
        });
    


})