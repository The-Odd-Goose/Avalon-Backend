const { firestore } = require('firebase-admin');
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
    rejected: 0,
    success: 0,
    turn: 0,
    voted: [],
    bad: [],
    merlin: null, // these are references to the special characters
    percival: null,
    morgana: null,
    mordred: null
})


// here we'll define a function that creates a game for us
exports.createGame = (user) => {

    const {userId, userName, photoURL} = user;

    const game = await gamesRef.add({
        ...newGame(userId) // so we generate a new game to add
    })

    // TODO: set the player's subcollection

    const gameId = game.id;
    let playersCollection = gamesRef.doc(gameId).collection('players');

    // so we add the owner to its game
    await playersCollection.doc(userId).add({
        name: userName,
        uid: userId,
        photoURL
    })

    let ownerRef = await playersCollection.limit(1).get().then(querySnapshot => {
        return querySnapshot.docs[0].ref;
    })

    // now we'll set a reference to the owner
    gamesRef.doc(gameId).update({
        owner: ownerRef
    })

    return gameId;

}

// we'll do some preliminary checks to make sure that the userId matches up with someone who is in the game
exports.startGame = (userId) => {
    // TODO:
    // we want to set the merlin, percival, morgana and mordred references
}