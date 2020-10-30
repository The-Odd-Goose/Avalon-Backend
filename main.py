from flask import Flask, render_template
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'peepeopeeepooopeeepepoepoepopeopeoepoepoep'

data = [
    {
        'title': 'lmao xd',
        'description': 'lmaxo poopoo'
    },
    {
        'title': 'x xd',
        'description': 'lmaxo poopoo'
    }
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', data=data)

@app.route("/about")
def about():
    return render_template('about.html', data=data)

@app.route("/register")
def register():
    form = RegistrationForm()
    return render_template()


if __name__ == '__main__':
    app.run(debug=True)
