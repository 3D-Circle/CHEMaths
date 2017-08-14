from flask import Flask

app = Flask(__name__, static_folder='web-app/build')

@app.route('/', methods=['GET'])
def main_page:
    return render_template('index.html', name="homepage")


if __name__ == "__main__":
    app.run()