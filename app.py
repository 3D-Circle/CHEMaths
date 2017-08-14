from flask import Flask, render_template

app = Flask(__name__, static_folder='web-app/build', static_url_path='')

@app.route('/')
def root():
    return app.send_static_file('index.html')

if __name__ == "__main__":
    app.run()