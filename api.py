from markupsafe import escape
from flask import Flask

from analysis import analyze

app = Flask(__name__)


@app.get("/equity/<symbol>")
def perform_analysis(symbol):
    results = analyze(symbol)

    return {
        "sharpe": results["sharpe"],
        "beta": results["beta"],
        "piotroski": results["piotroski"],
        "altman": results["altman"],
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)