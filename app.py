import sqlite3
from flask import Flask, render_template

app = Flask(__name__)

def get_violations():
    conn = sqlite3.connect("violations.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM violations ORDER BY id DESC")
    violations = cursor.fetchall()

    conn.close()
    return violations

@app.route("/")
def dashboard():
    violations = get_violations()
    return render_template("dashboard.html", violations=violations)

if __name__ == "__main__":
    app.run(debug=True)