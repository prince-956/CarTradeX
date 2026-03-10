from flask import Flask, render_template, request, jsonify, session, flash, url_for, redirect
from db import execute_query
import os
import uuid
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import re



UPLOAD_FOLDER = "static/images/cars"    # path to store images
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "avif"}

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

@app.route("/about")
def about():
    return render_template("about.html")



# =========================== LOGIN / SIGNUP / LOGOUT ===========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = execute_query("""
            SELECT user_id, name, email, password, role FROM users
            WHERE email = %s
            """,
            (email,), fetch=True
        )

        if not user:
            flash("Email not registered", "danger")
            return redirect(url_for("login"))

        user = user[0]   # becoz execute_query(in db.py) returns list

        if not check_password_hash(user["password"], password):
            flash("Incorrect password", "danger")
            return redirect(url_for("login"))
        
        session["logged_in"] = True
        session["user_id"] = user["user_id"]
        session["name"] = user["name"]
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

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        hashed_password = generate_password_hash(password)
        confirmPassword = request.form.get("confirmPassword", "")

        if not name:
            flash("Name required.", "danger")
            return render_template("signup.html")

        if not email.endswith("@gmail.com"):
            flash("Email must end with @gmail.com", "danger")
            return render_template("signup.html")

        if not re.fullmatch(r"\d{10}", phone):
            flash("Phone number must be exactly 10 digits.", "danger")
            return render_template("signup.html")

        password_pattern = r"^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,10}$"
        if not re.fullmatch(password_pattern, password):
            flash("Password must be 6-10 characters with 1 uppercase, 1 digit, and 1 special character.", "danger")
            return render_template("signup.html")

        if password != confirmPassword:
            flash("Passwords do not match!", "danger")
            return render_template("signup.html")

        existing = execute_query(
            "SELECT user_id FROM users WHERE email = %s",
            (email,),
            fetch=True
        )

        if existing:
            flash("Email already registered. Please login.", "danger")
            return render_template("signup.html")

        execute_query("""
            INSERT INTO users (name, email, phone, password)
            VALUES (%s, %s, %s, %s)
        """, (name, email, phone, hashed_password))

        flash("Account created successfully! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")



# ============================== BUY ==============================
# @app.route("/buy")
# def buy():
#     query = "SELECT * FROM cars WHERE status='AVAILABLE'"
#     cars = execute_query(query, fetch=True)
#     return render_template("buy.html", cars=cars)
@app.route("/buy")
def buy():

    filters = request.args.to_dict(flat=False)

    conditions = []
    params = []

    if "brand" in filters:
        conditions.append("brand=%s")
        params.append(filters["brand"][0])

    if "city" in filters:
        conditions.append("city=%s")
        params.append(filters["city"][0])

    if "kms" in filters:
        kms = filters["kms"][0].replace("B", "")
        conditions.append("kms_driven <= %s")
        params.append(kms)

    if "price" in filters:
        price = filters["price"][0].replace("+", "")
        conditions.append("price <= %s")
        params.append(price)

    query = "SELECT * FROM cars WHERE status='AVAILABLE'"

    if conditions:
        query += " AND " + " AND ".join(conditions)

    cars = execute_query(query, params, fetch=True) or []

    return render_template("buy.html", cars=cars)


# @app.route("/buy_car/<int:car_id>", methods=["POST"])
# def buy_car(car_id):
#     if not session.get("logged_in"):
#         return redirect(url_for("login"))

#     print(" Buy route called for car:", car_id)

#     query = """
#     UPDATE cars 
#     SET status = 'SOLD' 
#     WHERE car_id = %s;
#     """

#     execute_query(query, (car_id,)) 

#     print(" Car marked SOLD in DB:", car_id)
#     return {"message": "success"}, 200
@app.route("/buy_car/<int:car_id>", methods=["POST"])
def buy_car(car_id):
    if not session.get("logged_in"):
        return jsonify({"success": False, "redirect": url_for("login")}), 401

    # Check if car is available
    car = execute_query(
        "SELECT status FROM cars WHERE car_id = %s",
        (car_id,), fetch=True
    )
    
    if not car or car[0]["status"] != "AVAILABLE":
        return jsonify({"success": False, "message": "Car not available"}), 400

    # Redirect to payment page
    return jsonify({"success": True, "redirect": url_for("buyer_payment_page", car_id=car_id)}), 200





# ============================== SELL ==============================
@app.route("/sell")
def sell():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    return render_template("sell.html")

@app.route("/sell-car", methods=["POST"])
def sell_car():
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
        number_plate = request.form.get("number_plate")
        image = request.files.get("images")
        filename = secure_filename(image.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        image_path = f"cars/{unique_name}"
        image.save(os.path.join("static/images", image_path))

        execute_query("""
            INSERT INTO sell_requests
            (user_id, brand, model, year, city, fuel_type, transmission, kms_driven, owners, price, image, number_plate)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (user_id, brand, model, year, city, fuel_type, transmission, kms, owners, price, image_path, number_plate)
        )
        return jsonify({"success": True})
    
    except Exception as e:
        print("SELL ERROR:", e)
        return jsonify({"success": False, "error": str(e)})

# @app.route("/seller-dashboard")
# def seller_dashboard():
#     if not session.get("logged_in"):
#         return redirect(url_for("login"))

#     user_id = session["user_id"]

#     requests = execute_query("""
#         SELECT * FROM sell_requests
#         WHERE user_id = %s
#         ORDER BY requested_at DESC
#     """, (user_id,), fetch=True)

#     total = len(requests)
#     pending = len([r for r in requests if r["status"] == "PENDING"])
#     approved = len([r for r in requests if r["status"] == "APPROVED"])
#     rejected = len([r for r in requests if r["status"] == "REJECTED"])

#     return render_template("seller_dashboard.html",
#                            requests=requests,
#                            total=total,
#                            pending=pending,
#                            approved=approved,
#                            rejected=rejected)
@app.route("/my-profile")
def my_profile():

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    user_id = session["user_id"]

    user_data = execute_query("""
        SELECT name, email, phone
        FROM users
        WHERE user_id = %s
    """, (user_id,), fetch=True)

    user = user_data[0] if user_data else None

    sell_listings = execute_query("""
    SELECT *
    FROM sell_requests
    WHERE user_id = %s
    ORDER BY requested_at DESC
    """, (user_id,), fetch=True) or []

    bought_cars = execute_query("""
    SELECT *
    FROM cars
    WHERE buyer_id = %s
    ORDER BY created_at DESC
    """, (user_id,), fetch=True) or []


    return render_template(
        "my_profile.html",
        user=user,
        sell_listings=sell_listings,
        bought_cars=bought_cars
    )



# ============================== FILTERS ==============================
@app.route("/filter")
def filter_cars():

    filters = request.args.to_dict(flat=False)

    conditions = []
    params = []

    # Sorting
    sort_by = filters.pop("sort", ["newest"])[0]


    # -------------------------
    # BRAND (single or multiple)
    # -------------------------
    if "brand" in filters:
        brands = filters["brand"]
        placeholders = ",".join(["%s"] * len(brands))
        conditions.append(f"brand IN ({placeholders})")
        params.extend(brands)


    # -------------------------
    # YEAR
    # -------------------------
    if "year" in filters:
        years = []
        for val in filters["year"]:
            try:
                years.append(int(val.replace("A", "")))
            except:
                pass

        if years:
            conditions.append("year >= %s")
            params.append(min(years))


    # -------------------------
    # KMS
    # -------------------------
    if "kms" in filters:
        kms_vals = []
        for val in filters["kms"]:
            try:
                kms_vals.append(int(val.replace("B", "")))
            except:
                pass

        if kms_vals:
            conditions.append("kms_driven <= %s")
            params.append(max(kms_vals))


    # -------------------------
    # FUEL TYPE (multi select)
    # -------------------------
    if "fuel_type" in filters:
        fuels = filters["fuel_type"]
        placeholders = ",".join(["%s"] * len(fuels))
        conditions.append(f"fuel_type IN ({placeholders})")
        params.extend(fuels)


    # -------------------------
    # TRANSMISSION
    # -------------------------
    if "transmission" in filters:
        trans = filters["transmission"]
        placeholders = ",".join(["%s"] * len(trans))
        conditions.append(f"transmission IN ({placeholders})")
        params.extend(trans)


    # -------------------------
    # CITY
    # -------------------------
    if "city" in filters:
        cities = filters["city"]
        placeholders = ",".join(["%s"] * len(cities))
        conditions.append(f"city IN ({placeholders})")
        params.extend(cities)


    # -------------------------
    # OWNERS
    # -------------------------
    if "owners" in filters:
        owners = filters["owners"]

        if "3" in owners:
            conditions.append("owners >= 3")
        else:
            placeholders = ",".join(["%s"] * len(owners))
            conditions.append(f"owners IN ({placeholders})")
            params.extend(owners)


    # -------------------------
    # BASE QUERY
    # -------------------------
    query = "SELECT * FROM cars WHERE status='AVAILABLE'"

    if conditions:
        query += " AND " + " AND ".join(conditions)


    # -------------------------
    # SORTING
    # -------------------------
    sort_map = {
        "newest": "ORDER BY created_at DESC",
        "price-low": "ORDER BY price ASC",
        "price-high": "ORDER BY price DESC",
        "mileage-low": "ORDER BY kms_driven ASC",
        "year-new": "ORDER BY year DESC"
    }

    query += " " + sort_map.get(sort_by, "ORDER BY created_at DESC")


    cars = execute_query(query, params, fetch=True) or []

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
        SELECT car_id, brand, model, year, city, fuel_type, transmission, kms_driven, owners, price, image, number_plate
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
    if not session.get("logged_in"):
        return redirect(url_for("login"))

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

# @app.route("/admin/approve/<int:request_id>", methods=["POST"])
# def approve_request(request_id):
#     if not session.get("logged_in") or session.get("role") != "ADMIN":
#         flash("Unauthorized access!", "danger")
#         return redirect(url_for("login"))

#     request_data = execute_query("""
#         SELECT brand, model, year, city, fuel_type, transmission, kms_driven, owners, price, image, number_plate
#         FROM sell_requests
#         WHERE request_id = %s
#         """, 
#         (request_id,), fetch=True
#     )

#     if not request_data:
#         flash("Sell request not found!", "danger")
#         return redirect(url_for("admin"))

#     car = request_data[0]

#     execute_query("""
#         UPDATE sell_requests
#         SET status = 'APPROVED'
#         WHERE request_id = %s
#         """,
#         (request_id,)
#     )
@app.route("/admin/approve/<int:request_id>", methods=["POST"])
def approve_request(request_id):
    if not session.get("logged_in") or session.get("role") != "ADMIN":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))

    request_data = execute_query("""
        SELECT brand, model, year, city, fuel_type, transmission, kms_driven, owners, price, image, number_plate
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
        (brand, model, year, city, fuel_type, transmission, kms_driven, owners, price, image, status, number_plate)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (car["brand"], car["model"], car["year"], car["city"], car["fuel_type"], car["transmission"],
        car["kms_driven"], car["owners"], car["price"], car["image"], "AVAILABLE", car["number_plate"]
        )
    )

    flash("Car approved & added to marketplace!", "success")
    return redirect(url_for("admin"))

#     execute_query("""
#         INSERT INTO cars
#         (brand, model, year, city, fuel_type, transmission, kms_driven, owners, price, image, status, number_plate)
#         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
#         """,
#         (car["brand"], car["model"], car["year"], car["city"], car["fuel_type"], car["transmission"],
#         car["kms_driven"], car["owners"], car["price"], car["image"], "AVAILABLE", car["number_plate"]
#         )
#     )

#     flash("Car approved & added to marketplace!", "success")
#     return redirect(url_for("admin"))

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

@app.route("/admin/request/<int:request_id>")
def admin_view_request(request_id):
    request = execute_query("""
        SELECT sr.*, u.name, u.phone
        FROM sell_requests sr
        JOIN users u ON sr.user_id = u.user_id
        WHERE sr.request_id = %s
    """, (request_id,), fetch=True)

    if not request:
        return "No data found"

    return render_template("admin_view_request.html", request=request[0])



# ============================== TRANSACTION SYSTEM ==============================

# SELLER TRANSACTION (Admin pays seller)
@app.route("/transaction/seller/<int:request_id>")
def seller_transaction_page(request_id):
    if not session.get("logged_in") or session.get("role") != "ADMIN":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))

    # Get sell request + seller details
    data = execute_query("""
        SELECT sr.*, u.name, u.phone
        FROM sell_requests sr
        JOIN users u ON sr.user_id = u.user_id
        WHERE sr.request_id = %s
    """, (request_id,), fetch=True)

    if not data:
        flash("Request not found!", "danger")
        return redirect(url_for("admin"))

    return render_template("transaction.html", data=data[0])


@app.route("/process_transaction/<int:request_id>", methods=["POST"])
def process_transaction(request_id):
    if not session.get("logged_in") or session.get("role") != "ADMIN":
        flash("Unauthorized!", "danger")
        return redirect(url_for("login"))

    admin_id = session.get("user_id")
    amount = request.form.get("amount")
    sender_account = request.form.get("sender_account")
    receiver_account = request.form.get("receiver_account")

    # Get sell request data
    req_data = execute_query("""
        SELECT user_id, brand, model, year, city, fuel_type, transmission,
               kms_driven, owners, price, image, number_plate, status
        FROM sell_requests
        WHERE request_id = %s
    """, (request_id,), fetch=True)

    if not req_data:
        flash("Request not found!", "danger")
        return redirect(url_for("admin"))

    req = req_data[0]

    # Prevent duplicate approval
    if req["status"] == "APPROVED":
        flash("Already approved!", "warning")
        return redirect(url_for("admin"))

    seller_id = req["user_id"]
    owners = req.get("owners") or 1


    # Step 1: Insert car into cars table and get car_id
    car_result = execute_query("""
        INSERT INTO cars
        (brand, model, year, city, fuel_type, transmission, kms_driven,
         owners, price, image, status, number_plate, seller_id, approved_by)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'AVAILABLE',%s,%s,%s)
        RETURNING car_id
    """, (
        req["brand"], req["model"], req["year"], req["city"],
        req["fuel_type"], req["transmission"], req["kms_driven"],
        owners, req["price"], req["image"],
        req["number_plate"], seller_id, admin_id
    ), fetch=True)

    if not car_result:
        flash("Failed to add car!", "danger")
        return redirect(url_for("admin"))

    car_id = car_result[0]["car_id"]

    # Step 2: Insert transaction (Admin pays seller)
    execute_query("""
        INSERT INTO transactions
        (buyer_id, seller_id, car_id, amount, txn_type, status,
         buyer_account, seller_account, approved_by, remarks, request_id)
        VALUES (%s,%s,%s,%s,'SELL','COMPLETED',%s,%s,%s,%s,%s)
    """, (
        admin_id, seller_id, car_id, amount,
        sender_account, receiver_account, admin_id,
        "Seller payment for car approval", request_id
    ))

    # Step 3: Update sell_requests status to PAID
    execute_query("""
        UPDATE sell_requests
        SET status = 'PAID'
        WHERE request_id = %s
    """, (request_id,))

    flash("Seller paid! Now you can approve the car.", "success")
    return redirect(url_for("admin"))


# BUYER TRANSACTION (User buys car)
@app.route("/buy/payment/<int:car_id>")
def buyer_payment_page(car_id):
    if not session.get("logged_in"):
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    # Get car details
    car = execute_query("""
        SELECT car_id, brand, model, year, price, status, seller_id, approved_by
        FROM cars
        WHERE car_id = %s
    """, (car_id,), fetch=True)

    if not car:
        flash("Car not found!", "danger")
        return redirect(url_for("buy"))

    if car[0]["status"] != "AVAILABLE":
        flash("Car is not available!", "warning")
        return redirect(url_for("buy"))

    return render_template("buyer_payment.html", car=car[0])


@app.route("/process_buy_transaction/<int:car_id>", methods=["POST"])
def process_buy_transaction(car_id):
    if not session.get("logged_in"):
        flash("Unauthorized!", "danger")
        return redirect(url_for("login"))

    buyer_id = session.get("user_id")
    buyer_account = request.form.get("buyer_account")
    amount = request.form.get("amount")

    # Get car details
    car = execute_query("""
        SELECT seller_id, approved_by, status, price
        FROM cars
        WHERE car_id = %s
    """, (car_id,), fetch=True)

    if not car:
        flash("Car not found!", "danger")
        return redirect(url_for("buy"))

    car_data = car[0]

    # Prevent buying already sold car
    if car_data["status"] == "SOLD":
        flash("Car already sold!", "warning")
        return redirect(url_for("buy"))

    seller_id = car_data["seller_id"]
    approved_by = car_data["approved_by"]

    # Get admin account (hardcoded or from admin user)
    admin_account = "ADMIN-ACC-001"

    # Step 1: Insert transaction (User pays admin)
    execute_query("""
        INSERT INTO transactions
        (buyer_id, seller_id, car_id, amount, txn_type, status,
         buyer_account, seller_account, approved_by, remarks)
        VALUES (%s,%s,%s,%s,'BUY','COMPLETED',%s,%s,%s,%s)
    """, (
        buyer_id, seller_id, car_id, amount,
        buyer_account, admin_account, approved_by,
        "Car purchase payment"
    ))

    # Step 2: Update car status to SOLD
    execute_query("""
        UPDATE cars
        SET status = 'SOLD',
            buyer_id = %s
        WHERE car_id = %s
    """, (buyer_id, car_id))

    # Step 3: Pay seller automatically
    execute_query("""
        INSERT INTO transactions
        (buyer_id, seller_id, car_id, amount, txn_type, status,
         buyer_account, seller_account, approved_by, remarks)
        VALUES (%s,%s,%s,%s,'SELLER_PAYMENT','COMPLETED',%s,%s,%s,%s)
    """, (
        approved_by, seller_id, car_id, amount,
        admin_account, f"SELLER-ACC-{seller_id}", approved_by,
        "Automatic seller payment after car sale"
    ))

    flash("Payment successful! Car is now yours.", "success")
    return redirect(url_for("my_profile"))

# if __name__=="__main__":
#     app.run(debug=True)
#     return redirect(url_for("my_profile"))

if __name__=="__main__":
    app.run(debug=True)