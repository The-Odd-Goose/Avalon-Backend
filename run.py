from endpoints import create_app

app = create_app()
# TODO: add in better errors!
if __name__ == '__main__':
    # TODO: turn to false when deployed
    app.run(debug=True, port=8080)