from flask import Flask, render_template, request, jsonify, session, flash, url_for, redirect
from db import execute_query
import os
import uuid
from werkzeug.utils import secure_filename



UPLOAD_FOLDER = "static/images/cars"    # path to store images
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)   # creates folder if not exist
# if exist then does nothing bcoz exist_ok=True

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS



app = Flask(__name__)
app.secret_key = "cartradex-secret"



# =================================== HOME ===================================
@app.route("/")
def home():
    if session.get("logged_in") and session.get("role")=="ADMIN":
        return redirect(url_for("admin"))
    return render_template("home.html")



# =========================== LOGIN / SIGNUP / LOGOUT ===========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = execute_query("""
            SELECT user_id, email, password, role FROM users
            WHERE email = %s
            """,
            (email,), fetch=True
        )

        if not user:
            flash("Email not registered", "danger")
            return redirect(url_for("login"))

        user = user[0]   # becoz execute_query(in db.py) returns list

        if password != user["password"]:
            flash("Incorrect password", "danger")
            return redirect(url_for("login"))
        
        session["logged_in"] = True
        session["user_id"] = user["user_id"]
        session["email"] = user["email"]
        session["role"] = user["role"]

        flash("Login Successful!", "success")

        if user["role"] == "ADMIN":
            return redirect(url_for("admin"))
        else:
            return redirect(url_for("home"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for("home"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        confirmPassword = request.form.get("confirmPassword")

        existing = execute_query(
            "SELECT user_id FROM users WHERE email = %s",
            (email,),
            fetch=True
        )

        if existing:
            flash("Email already registered. Please login.", "danger")
            return render_template("login.html")

        if password != confirmPassword:
            flash("Passwords do not match!", "danger")
            return render_template("signup.html")

        execute_query(
            """
            INSERT INTO users (name, email, phone, password, role)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (name, email, phone, password, "USER")
        )

        flash("Account created successfully! Please login.", "success")
        return render_template("login.html")

    return render_template("signup.html")



# ============================== BUY ==============================
@app.route("/buy")
def buy():
    query = "SELECT * FROM cars WHERE status='AVAILABLE'"
    cars = execute_query(query, fetch=True)
    return render_template("buy.html", cars=cars)

@app.route("/buy_car/<int:car_id>", methods=["POST"])
def buy_car(car_id):
    print(" Buy route called for car:", car_id)

    query = """
    UPDATE cars 
    SET status = 'SOLD' 
    WHERE car_id = %s;
    """

    execute_query(query, (car_id,)) 

    print(" Car marked SOLD in DB:", car_id)
    return {"message": "success"}, 200




# ============================== SELL ==============================
@app.route("/sell")
def sell():
    return render_template("sell.html")

@app.route("/sell-car", methods=["POST"])
def sell_car():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    try:
        user_id = session.get("user_id")
        brand = request.form.get("brand")
        model = request.form.get("model")
        year = int(request.form.get("year"))
        city = request.form.get("city")
        fuel_type = request.form.get("fuel_type").upper()
        transmission = request.form.get("transmission").upper()
        kms = int(request.form.get("kms"))
        owners_raw = request.form.get("owners")
        owners = 4 if owners_raw == "3+" else int(owners_raw)
        price = int(request.form.get("price"))
        image = request.files.get("images")
        filename = secure_filename(image.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        image_path = f"cars/{unique_name}"
        image.save(os.path.join("static/images", image_path))

        execute_query("""
            INSERT INTO sell_requests
            (user_id, brand, model, year, city, fuel_type, transmission, kms_driven, owners, price, image)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (user_id, brand, model, year, city, fuel_type, transmission, kms, owners, price, image_path)
        )
        return jsonify({"success": True})
    
    except Exception as e:
        print("SELL ERROR:", e)
        return jsonify({"success": False, "error": str(e)})

@app.route("/seller-dashboard")
def seller_dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    user_id = session["user_id"]

    requests = execute_query("""
        SELECT * FROM sell_requests
        WHERE user_id = %s
        ORDER BY requested_at DESC
    """, (user_id,), fetch=True)

    total = len(requests)
    pending = len([r for r in requests if r["status"] == "PENDING"])
    approved = len([r for r in requests if r["status"] == "APPROVED"])
    rejected = len([r for r in requests if r["status"] == "REJECTED"])

    return render_template("seller_dashboard.html",
                           requests=requests,
                           total=total,
                           pending=pending,
                           approved=approved,
                           rejected=rejected)


# ============================== FILTERS ==============================
@app.route("/filter")
def filter_cars():
    filters = request.args.to_dict(flat=False)
    conditions = []
    params = []

    sort_by = filters.pop("sort", ["newest"])[0]

    for key, values in filters.items():
        val = values[0]

        if val == "All":
            continue

        if key == "price":
            if val == "30000A":
                conditions.append("price >= 30000")
            elif val == "50000A":
                conditions.append("price >= 50000")
            continue

        if key == "year":
            if val == "2024A":
                conditions.append("year >= 2024")
            elif val == "2023A":
                conditions.append("year >= 2023")
            elif val == "2022A":
                conditions.append("year >= 2022")
            continue

        if key == "mileage":
            if val == "0-25000":
                conditions.append("kms_driven BETWEEN 0 AND 25000")
            elif val == "25000-50000":
                conditions.append("kms_driven BETWEEN 25000 AND 50000")
            elif val == "50000-75000":
                conditions.append("kms_driven BETWEEN 50000 AND 75000")
            elif val == "75001+":
                conditions.append("kms_driven >= 75001")
            continue

        if key == "city":
            conditions.append("city = %s")
            params.append(val)
            continue

        if key == "owners":
            conditions.append("owners = %s")
            params.append(val)
            continue

        conditions.append(f"{key} = %s")
        params.append(val)

    # Base query
    query = "SELECT * FROM cars WHERE status='AVAILABLE'"

    if conditions:
        query += " AND " + " AND ".join(conditions)
        
    sort_map = {
        "newest": "ORDER BY created_at DESC",
        "price-low": "ORDER BY price ASC",
        "price-high": "ORDER BY price DESC",
        "mileage-low": "ORDER BY kms_driven ASC",
        "year-new": "ORDER BY year DESC"
    }

    query += " " + sort_map.get(sort_by, "ORDER BY created_at DESC")

    cars = execute_query(query, params, fetch=True)

    if not cars:
        cars = []

    return render_template("car_cards.html", cars=cars)

# ============================== VIEW CAR DETAILS ==============================
@app.route("/car/<int:car_id>")
def car_details(car_id):
    if not session.get("logged_in"):
        in_wishlist = False
    else:
        existing = execute_query(
            "SELECT * FROM wishlist WHERE user_id = %s AND car_id = %s",
            (session["user_id"], car_id),
            fetch=True
        )

        in_wishlist = bool(existing)

    cars = execute_query("""
        SELECT car_id, brand, model, year, city, fuel_type, transmission, kms_driven, owners, price, image
        FROM cars
        WHERE car_id = %s
        """,
        (car_id,), fetch=True
    )

    if not cars:
        return f"Car not found for id {car_id}", 404
    
    car = cars[0]

    return render_template(
        "car_details.html",
        car=car,
        in_wishlist=in_wishlist
    )



# ============================== WISHLIST ==============================
@app.route("/wishlist")
def wishlist():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    user_id = session["user_id"]

    cars = execute_query("""
        SELECT c.car_id, c.brand, c.model, c.year, c.price, c.city, c.image
        FROM cars c INNER JOIN wishlist w 
        ON c.car_id = w.car_id
        WHERE w.user_id = %s
        """,
        (user_id,), fetch=True
    )

    if not cars:
        cars = []

    print("WISHLIST CARS:", cars) 

    return render_template("wishlist.html", cars=cars)

@app.route("/api/wishlist")
def wishlist_api():
    user_id = session.get("user_id")

    cars = execute_query("""
        SELECT c.car_id, c.brand, c.model, c.year, c.price, c.city, c.image
        FROM cars c JOIN wishlist w 
        ON c.car_id = w.car_id
        WHERE w.user_id = %s
        """,
        (user_id,)
    )

    return jsonify({"cars": cars})

@app.route("/add_to_wishlist/<int:car_id>", methods=["POST"])
def add_to_wishlist(car_id):
    if not session.get("logged_in"):
        return jsonify({
            "success": False,
            "redirect": url_for("login"),
            "message": "Please login to add to wishlist"
        }), 401

    user_id = session["user_id"]

    existing = execute_query(
        "SELECT * FROM wishlist WHERE user_id = %s AND car_id = %s",
        (user_id, car_id),
        fetch=True
    )

    if existing:
        return jsonify({"success": False, "message": "Already in wishlist"})

    execute_query(
        "INSERT INTO wishlist (user_id, car_id) VALUES (%s, %s)",
        (user_id, car_id)
    )

    return jsonify({"success": True, "message": "Added to wishlist"})

@app.route("/remove_from_wishlist/<int:car_id>", methods=["POST"])
def remove_from_wishlist(car_id):
    user_id = session.get("user_id", 1)

    execute_query(
        "DELETE FROM wishlist WHERE user_id = %s AND car_id = %s",
        (user_id, car_id)
    )

    flash("Removed from wishlist", "info")
    return redirect(url_for("wishlist"))

@app.route("/toggle_wishlist/<int:car_id>", methods=["POST"])
def toggle_wishlist(car_id):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    
    user_id = session["user_id"]

    existing = execute_query(
        "SELECT * FROM wishlist WHERE user_id = %s AND car_id = %s",
        (user_id, car_id),
        fetch=True
    )

    if existing:    
        execute_query(
            "DELETE FROM wishlist WHERE user_id = %s AND car_id = %s",
            (user_id, car_id)
        )
        flash("Removed from wishlist", "info")
    else:
        execute_query(
            "INSERT INTO wishlist (user_id, car_id) VALUES (%s, %s)",
            (user_id, car_id)
        )
        flash("Added to wishlist ❤️", "success")

    return redirect(url_for("car_details", car_id=car_id))



# =================================== ADMIN ===================================
@app.route("/admin")
def admin():
    if not session.get("logged_in") or session.get("role") != "ADMIN":
        flash("Access denied!", "danger")
        return redirect(url_for("login"))

    stats = {
        "total_users": get_total_users() or 0,
        "total_listings": len(get_all_listings()),
        "pending": len(get_pending_listings()),
        "revenue": get_monthly_revenue() or 0
    }

    return render_template(
        "admin.html",
        stats=stats,
        recent_listings=get_recent_listings(),
        users=get_all_users(),
        listings=get_all_listings(),
        pending=get_pending_listings()
    )

def get_total_users():
    result = execute_query("SELECT COUNT(*) AS cnt FROM users", fetch=True)
    return result[0]["cnt"] if result else 0

def get_total_listings():
    result = execute_query("SELECT COUNT(*) AS cnt FROM cars", fetch=True)
    return result[0]["cnt"] if result else 0

def get_pending_count():
    result = execute_query("SELECT COUNT(*) AS cnt FROM cars WHERE status='PENDING'", fetch=True)
    return result[0]["cnt"] if result else 0

def get_monthly_revenue():
    # result = execute_query("""
    #     SELECT COALESCE(SUM(amount),0) AS revenue 
    #     FROM transactions 
    #     WHERE txn_type='BUY' 
    #     AND DATE_TRUNC('month', created_at) = DATE_TRUNC('month', CURRENT_DATE)
    # """, fetch=True)
    # return result[0]["revenue"] if result else 0
    result = execute_query("SELECT COUNT(*) AS cnt FROM cars WHERE status='SOLD'", fetch=True)
    return result[0]["cnt"] if result else 0

def get_recent_listings():
    data = execute_query("""
        SELECT brand, model, price, status, requested_at FROM sell_requests
        ORDER BY requested_at DESC LIMIT 5
        """,
        fetch=True
    )

    return data if data else []

def get_all_users():
    return execute_query("""
        SELECT user_id, name, email, phone, role FROM users
        """, fetch=True
    ) or []

def get_all_listings():
    data = execute_query("""
        SELECT s.request_id, s.brand, s.model, s.price, s.status, s.requested_at, u.name AS seller_name
        FROM sell_requests s JOIN users u ON s.user_id = u.user_id
        ORDER BY s.requested_at DESC
        """,
        fetch=True
    )

    return data if data else []

def get_pending_listings():
    data = execute_query("""
        SELECT request_id, user_id, brand, model, price, requested_at FROM sell_requests
        WHERE status = 'PENDING'
        ORDER BY requested_at DESC
        """,
        fetch=True
    )

    return data if data else []

@app.route("/admin/approve/<int:request_id>", methods=["POST"])
def approve_request(request_id):
    if not session.get("logged_in") or session.get("role") != "ADMIN":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))

    request_data = execute_query("""
        SELECT brand, model, year, city, fuel_type, transmission, kms_driven, owners, price, image
        FROM sell_requests
        WHERE request_id = %s
        """, 
        (request_id,), fetch=True
    )

    if not request_data:
        flash("Sell request not found!", "danger")
        return redirect(url_for("admin"))

    car = request_data[0]

    execute_query("""
        UPDATE sell_requests
        SET status = 'APPROVED'
        WHERE request_id = %s
        """,
        (request_id,)
    )

    execute_query("""
        INSERT INTO cars
        (brand, model, year, city, fuel_type, transmission, kms_driven, owners, price, image, status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (car["brand"], car["model"], car["year"], car["city"], car["fuel_type"], car["transmission"],
        car["kms_driven"], car["owners"], car["price"], car["image"], "AVAILABLE"
        )
    )

    flash("Car approved & added to marketplace!", "success")
    return redirect(url_for("admin"))

@app.route("/admin/reject/<int:request_id>", methods=["POST"])
def reject_request(request_id):
    if not session.get("logged_in") or session.get("role") != "ADMIN":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))

    execute_query("""
        UPDATE sell_requests
        SET status = 'REJECTED'
        WHERE request_id = %s
        """,
        (request_id,)
    )

    flash("Car sell request rejected!", "warning")
    return redirect(url_for("admin"))

if __name__=="__main__":
    app.run(debug=True)






# @app.route("/filter")
# def filter_cars():
#     filters = request.args.to_dict(flat=False)
#     conditions = []
#     params = []
#     for key, values in filters.items():
#         if key == "price":
#             if values[0] == "30000A":
#                 conditions.append("price >= 30000")
#             elif values[0] == "50000A":
#                 conditions.append("price >= 50000")
#             continue

#         if key == "year":
#             if values[0] == "2024A":
#                 conditions.append("year >= 2024")
#             elif values[0] == "2023A":
#                 conditions.append("year >= 2023")
#             elif values[0] == "2022A":
#                 conditions.append("year >= 2022")
#             continue

#         placeholders = ",".join(["%s"] * len(values))
#         conditions.append(f"{key} IN ({placeholders})")
#         params.extend(values)

#     query = "SELECT * FROM cars WHERE status='AVAILABLE'"

#     if conditions:
#         query += " AND " + " AND ".join(conditions)

#     cars = execute_query(query, params, fetch=True)

#     if not cars:
#         cars = []

#     return render_template("car_cards.html", cars=cars)
