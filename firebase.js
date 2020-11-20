const admin = require('firebase-admin');
// TODO: delete this when ready to deploy, not required
const serviceAccount = require('./service-account.json')

admin.initializeApp({
    // for when we deploy to google cloud platform
    // credential: admin.credential.applicationDefault()
    credential: admin.credential.cert(serviceAccount)

});

const db = admin.firestore();
const gamesRef = db.collection("games");

// here we'll define the function that enters the game for us
exports.enterGame = (userId, gameId) => {

    return {
        gameId
    };
}

// so this will be how the new game is
// players array will hold all the players, while turn is which player in that array's turn to suggest a new batch of players
// and voted will be an array of currently proposed ppl to go on the mission with
const newGame = (userId) => ({
    fail: 0,
    players: [userId],
    rejected: 0,
    success: 0,
    turn: 0,
    voted: []
})

// here we'll define a function that creates a game for us
exports.createGame = (userId) => {

    const gameId = 

    await gamesRef.doc().add({
        newGame()
    })
}