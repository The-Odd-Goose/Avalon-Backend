# this module here will define some type checking functions

class UIDError(Exception):
    # the error that occurs with uids
    def __init__(self, message="A uid error has occured"):
        self.message = message

class GameIDError(Exception):
    def __init__(self, message="A game error has occured"):
        self.message = message

# this function checks if the user exists, if it does, returns the user object
def is_User(data):
    
    uid = data.get("uid")
    # checks the user ID directly if in object
    if uid == None:
        raise UIDError("UID was not given in request")

    # then needs to check the firebase to see if user is in there
    # imports the firebase function that does this
    from endpoints.firebase import doesUserExist
    user = doesUserExist(uid)

    if type(user) == str:
        raise UIDError(user)

    return user

def game_Exist(data):

    game_id = data.get("gameId")

    if game_id == None:
        raise GameIDError("Game Id was not given in request")

    # returns a game from checking if the game exists -- a game ref actually
    from endpoints.firebase import doesGameExist
    game_ref = doesGameExist(game_id)

    # if it is a string however, an error has occured
    if type(game_ref) == str:
        raise GameIDError(game_ref)

    return game_ref