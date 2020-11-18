const admin = require('firebase-admin');
// TODO: delete this when ready to deploy, not required
const serviceAccount = require('./service-account.json')

admin.initializeApp({
    // for when we deploy to google cloud platform
    // credential: admin.credential.applicationDefault()
    credential: admin.credential.cert(serviceAccount)

});

const db = admin.firestore();

