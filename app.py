from flask import Flask, redirect, render_template, request
from psycopg2.extras import RealDictCursor

import seed
from config import DATABASES, connect, pick_shard

app = Flask(__name__)


def insert_row(db_name, shard, values):
    db = DATABASES[db_name]
    columns = ", ".join(db["columns"])
    sql = "INSERT INTO " + db["table"] + " (" + columns + ") VALUES (%s, %s, %s)"

    conn = connect(db_name, shard)
    conn.cursor().execute(sql, values)
    conn.commit()
    conn.close()


def delete_row(db_name, shard, id):
    db = DATABASES[db_name]

    conn = connect(db_name, shard)
    conn.cursor().execute("DELETE FROM " + db["table"] + " WHERE id = %s", [id])
    conn.commit()
    conn.close()


@app.route("/")
def home():
    return redirect("/library")


@app.route("/<db_name>")
def show(db_name):
    if db_name not in DATABASES:
        return "Database not found", 404
    db = DATABASES[db_name]

    rows = []
    for shard in range(len(db["ports"])):
        conn = connect(db_name, shard)
        c = conn.cursor(cursor_factory=RealDictCursor)
        c.execute("SELECT * FROM " + db["table"] + " ORDER BY id")
        for row in c.fetchall():
            row["shard"] = shard
            rows.append(row)
        conn.close()

    return render_template("index.html", databases=DATABASES, db_name=db_name, db=db, rows=rows)


@app.route("/<db_name>/add", methods=["POST"])
def add(db_name):
    db = DATABASES[db_name]
    values = [request.form[col] for col in db["columns"]]

    shard = pick_shard(db_name, values[0])
    insert_row(db_name, shard, values)
    return redirect("/" + db_name)


@app.route("/<db_name>/update/<int:shard>/<int:id>", methods=["POST"])
def update(db_name, shard, id):
    db = DATABASES[db_name]
    values = [request.form[col] for col in db["columns"]]

    new_shard = pick_shard(db_name, values[0])
    if new_shard != shard:
        delete_row(db_name, shard, id)
        insert_row(db_name, new_shard, values)
    else:
        a, b, c = db["columns"]
        sql = "UPDATE " + db["table"] + " SET " + a + " = %s, " + b + " = %s, " + c + " = %s WHERE id = %s"

        conn = connect(db_name, shard)
        conn.cursor().execute(sql, values + [id])
        conn.commit()
        conn.close()

    return redirect("/" + db_name)


@app.route("/<db_name>/delete/<int:shard>/<int:id>", methods=["POST"])
def delete(db_name, shard, id):
    delete_row(db_name, shard, id)
    return redirect("/" + db_name)


@app.route("/reset", methods=["POST"])
def reset():
    seed.create_all()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
