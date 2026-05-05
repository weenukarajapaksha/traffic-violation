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

from flask import request

@app.route("/")
def dashboard():
    plate = request.args.get("plate")

    conn = sqlite3.connect("violations.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if plate:
        cursor.execute("SELECT * FROM violations WHERE plate_number LIKE ?", (f"%{plate}%",))
    else:
        cursor.execute("SELECT * FROM violations ORDER BY id DESC")

    violations = cursor.fetchall()
    conn.close()

    return render_template("dashboard.html", violations=violations)

import csv
from flask import Response

@app.route("/download")
def download():
    conn = sqlite3.connect("violations.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM violations")

    def generate():
        data = cursor.fetchall()
        yield "id,plate,violation,time\n"
        for row in data:
            yield f"{row[0]},{row[1]},{row[2]},{row[3]}\n"

    return Response(generate(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=report.csv"})


if __name__ == "__main__":
    app.run(debug=True)