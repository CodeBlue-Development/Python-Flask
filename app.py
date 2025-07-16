from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# MySQL configuration
mysql_config = {
    'host': '68.178.174.206',
    'user': 'marketer_ctr_user',
    'password': 'Codeblue@1299',
    'database': 'marketer_ctr',
}

TABLE_NAME = "tool_users"
PRIMARY_KEY = "id"

def get_db_connection():
    return mysql.connector.connect(**mysql_config)

@app.route("/")
def dashboard():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SHOW COLUMNS FROM `{TABLE_NAME}`")
        columns = [col["Field"] for col in cursor.fetchall() if col["Field"] != "secret"]
        column_str = ", ".join([f"`{col}`" for col in columns])
        cursor.execute(f"SELECT {column_str} FROM `{TABLE_NAME}`")
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template("dashboard.html", table_name=TABLE_NAME, columns=columns, rows=rows)

@app.route("/add", methods=["GET", "POST"])
def add_row():
    fields = ["id", "email", "password", "is_admin", "is_super_admin", "is_active"]

    if request.method == "POST":
        form_data = request.form.to_dict()
        columns = ", ".join([f"`{key}`" for key in form_data])
        placeholders = ", ".join(["%s"] * len(form_data))
        values = list(form_data.values())

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO `{TABLE_NAME}` ({columns}) VALUES ({placeholders})", values)
            conn.commit()
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for("dashboard"))

    return render_template("add.html", table_name=TABLE_NAME, fields=fields)

@app.route("/edit/<int:row_id>", methods=["GET", "POST"])
def edit_row(row_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        if request.method == "POST":
            form_data = request.form.to_dict()
            updates = ", ".join([f"`{key}` = %s" for key in form_data])
            values = list(form_data.values()) + [row_id]

            cursor.execute(f"UPDATE `{TABLE_NAME}` SET {updates} WHERE {PRIMARY_KEY} = %s", values)
            conn.commit()
            return redirect(url_for("dashboard"))

        cursor.execute(f"SELECT * FROM `{TABLE_NAME}` WHERE {PRIMARY_KEY} = %s", (row_id,))
        row = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    return render_template("edit.html", table_name=TABLE_NAME, row=row)

@app.route("/toggle/<int:row_id>/<column>/<int:state>", methods=["POST"])
def toggle_flag(row_id, column, state):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE `{TABLE_NAME}` SET `{column}` = %s WHERE {PRIMARY_KEY} = %s", (state, row_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("edit_row", row_id=row_id))

@app.route("/delete/<int:row_id>", methods=["POST"])
def delete_row(row_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM `{TABLE_NAME}` WHERE {PRIMARY_KEY} = %s", (row_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True)


