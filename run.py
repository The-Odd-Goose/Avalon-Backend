from endpoints import create_app

app = create_app()

if __name__ == '__main__':
    # TODO: turn to false when deployed
    app.run(debug=False, port=8080)