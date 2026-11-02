from datetime import datetime

from flask import Flask, jsonify, request, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "change-this-secret-key"   # change this before deploying

# ---------- Restaurant details ----------
restaurant = {
    "name": "Spice Garden",
    "tagline": "Authentic Indian food, made fresh every day",
    "address": "Shop 12, Sector 29 Market, Gurugram, Haryana 122001",
    "phone": "+91 98765 43210",
    "email": "hello@spicegarden.example",
    "hours": "Open daily: 12:00 pm - 11:00 pm",
    # Shown in the "About Us" section on the front page - edit this text freely
    "about": "Spice Garden is a family-run restaurant serving authentic Indian food in the heart of "
             "Sector 29 Market, Gurugram. Our recipes come from home kitchens across India, and every "
             "dish is cooked fresh to order with hand-ground spices. Whether you are joining us for a "
             "family dinner or ordering in, we want every meal to feel like home.",
    "highlights": ["Fresh ingredients daily", "Traditional family recipes", "Dine-in & home delivery"],
}

# ---------- Menu (6 dishes in each category) ----------
menu = [
    # Starters
    {"id": 1, "category": "Starters", "name": "Paneer Tikka", "price": 250, "desc": "Smoky tandoori cottage cheese"},
    {"id": 2, "category": "Starters", "name": "Hara Bhara Kebab", "price": 220, "desc": "Spinach and green pea patties"},
    {"id": 3, "category": "Starters", "name": "Chicken 65", "price": 280, "desc": "Spicy fried chicken with curry leaves"},
    {"id": 4, "category": "Starters", "name": "Veg Samosa", "price": 80, "desc": "Crispy pastry with spiced potato"},
    {"id": 5, "category": "Starters", "name": "Aloo Tikki Chaat", "price": 120, "desc": "Potato patties with chutneys and curd"},
    {"id": 6, "category": "Starters", "name": "Fish Amritsari", "price": 320, "desc": "Gram flour battered fried fish"},
    # Main Dish
    {"id": 7, "category": "Main Dish", "name": "Butter Chicken", "price": 380, "desc": "Creamy tomato gravy, tender chicken"},
    {"id": 8, "category": "Main Dish", "name": "Paneer Butter Masala", "price": 320, "desc": "Soft paneer in rich buttery gravy"},
    {"id": 9, "category": "Main Dish", "name": "Dal Makhani", "price": 280, "desc": "Slow-cooked black lentils with butter"},
    {"id": 10, "category": "Main Dish", "name": "Veg Biryani", "price": 240, "desc": "Fragrant basmati rice with vegetables"},
    {"id": 11, "category": "Main Dish", "name": "Chicken Biryani", "price": 330, "desc": "Dum biryani with raita"},
    {"id": 12, "category": "Main Dish", "name": "Chole Bhature", "price": 180, "desc": "Spicy chickpeas with fluffy bhature"},
    # Drinks
    {"id": 13, "category": "Drinks", "name": "Masala Chai", "price": 60, "desc": "Ginger and cardamom tea"},
    {"id": 14, "category": "Drinks", "name": "Sweet Lassi", "price": 90, "desc": "Thick chilled yogurt drink"},
    {"id": 15, "category": "Drinks", "name": "Mango Lassi", "price": 110, "desc": "Lassi blended with ripe mango"},
    {"id": 16, "category": "Drinks", "name": "Fresh Lime Soda", "price": 80, "desc": "Sweet, salted or mixed"},
    {"id": 17, "category": "Drinks", "name": "Jaljeera", "price": 70, "desc": "Tangy cumin and mint cooler"},
    {"id": 18, "category": "Drinks", "name": "Cold Coffee", "price": 120, "desc": "Creamy iced coffee"},
    # Dessert
    {"id": 19, "category": "Dessert", "name": "Gulab Jamun", "price": 90, "desc": "Warm milk dumplings in sugar syrup"},
    {"id": 20, "category": "Dessert", "name": "Rasmalai", "price": 120, "desc": "Soft cheese discs in saffron milk"},
    {"id": 21, "category": "Dessert", "name": "Gajar Halwa", "price": 130, "desc": "Carrot pudding with nuts"},
    {"id": 22, "category": "Dessert", "name": "Kulfi Falooda", "price": 150, "desc": "Indian ice cream with vermicelli"},
    {"id": 23, "category": "Dessert", "name": "Jalebi", "price": 100, "desc": "Crispy spirals soaked in syrup"},
    {"id": 24, "category": "Dessert", "name": "Kheer", "price": 110, "desc": "Creamy rice pudding"},
]

# ---------- In-memory storage (cleared when the server restarts) ----------
orders = {}            # order id -> order
next_order_id = 1
users = {}             # email -> {"name": ..., "password": hashed}
saved_addresses = {}   # email -> [address, address, ...]


def current_user():
    return session.get("email")


# ---------- Frontend pages ----------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/checkout")
def checkout():
    return render_template("checkout.html")


# ---------- Restaurant + menu ----------
@app.route("/api/restaurant", methods=["GET"])
def get_restaurant():
    return jsonify(restaurant)


@app.route("/api/menu", methods=["GET"])
def get_menu():
    category = request.args.get("category")      # e.g. /api/menu?category=Drinks
    if category:
        return jsonify([d for d in menu if d["category"] == category])
    return jsonify(menu)


# ---------- User accounts ----------
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    if not name or "@" not in email or len(password) < 4:
        return jsonify({"error": "Enter your name, a valid email and a password (at least 4 characters)."}), 400
    if email in users:
        return jsonify({"error": "This email is already registered. Please log in."}), 409
    users[email] = {"name": name, "password": generate_password_hash(password)}
    session["email"] = email
    return jsonify({"name": name}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    user = users.get(email)
    if not user or not check_password_hash(user["password"], data.get("password", "")):
        return jsonify({"error": "Wrong email or password."}), 401
    session["email"] = email
    return jsonify({"name": user["name"]})


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})


@app.route("/api/me", methods=["GET"])
def me():
    email = current_user()
    if email not in users:
        return jsonify({"loggedIn": False})
    return jsonify({"loggedIn": True, "name": users[email]["name"], "email": email})


# ---------- Saved addresses ----------
@app.route("/api/addresses", methods=["GET"])
def get_addresses():
    email = current_user()
    if email not in users:
        return jsonify({"error": "Please log in."}), 401
    return jsonify(saved_addresses.get(email, []))


@app.route("/api/addresses", methods=["POST"])
def add_address():
    email = current_user()
    if email not in users:
        return jsonify({"error": "Please log in."}), 401
    text = (request.get_json(silent=True) or {}).get("address", "").strip()
    if not text:
        return jsonify({"error": "Address is empty."}), 400
    addresses = saved_addresses.setdefault(email, [])
    if text not in addresses:
        addresses.append(text)
    return jsonify(addresses), 201


# ---------- Orders ----------
def build_items(raw_items):
    """Check the cart and work out the total using real menu prices."""
    if not isinstance(raw_items, list) or not raw_items:
        return None, 0
    items, total = [], 0
    for item in raw_items:
        try:
            dish_id, qty = int(item["id"]), int(item["qty"])
        except (KeyError, TypeError, ValueError):
            return None, 0
        dish = next((d for d in menu if d["id"] == dish_id), None)
        if not dish or qty < 1 or qty > 50:
            return None, 0
        items.append({"name": dish["name"], "qty": qty, "price": dish["price"]})
        total += dish["price"] * qty
    return items, total


def check_payment(pay):
    """Mock payment: only checks the details look valid. Nothing is charged
    and a full card number is never stored. Returns a label, or None."""
    if not isinstance(pay, dict):
        return None
    method = pay.get("method")
    if method == "cash":
        return "Cash"
    if method == "upi" and "@" in str(pay.get("upi", "")):
        return "UPI: " + str(pay["upi"]).strip()
    if method == "card":
        number = str(pay.get("number", "")).replace(" ", "")
        cvv = str(pay.get("cvv", ""))
        if number.isdigit() and len(number) == 16 and cvv.isdigit() and len(cvv) in (3, 4):
            return "Card ending " + number[-4:]
    if method == "netbanking" and pay.get("bank"):
        return "Net Banking: " + str(pay["bank"])
    return None


@app.route("/api/orders", methods=["GET"])
def get_orders():
    """Order history: only the logged-in user's own orders, newest first."""
    email = current_user()
    if email not in users:
        return jsonify({"error": "Please log in."}), 401
    mine = [o for o in orders.values() if o["user"] == email]
    return jsonify(sorted(mine, key=lambda o: o["id"], reverse=True))


@app.route("/api/orders", methods=["POST"])
def place_order():
    global next_order_id
    email = current_user()
    if email not in users:
        return jsonify({"error": "Please log in to place an order."}), 401

    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    order_type = data.get("type")                    # "delivery" or "dinein"
    address = data.get("address", "").strip()
    table = str(data.get("table", "")).strip()

    # Check that all fields are filled
    if not name or not phone:
        return jsonify({"error": "Please enter your name and phone number."}), 400
    if not (phone.isdigit() and len(phone) == 10):
        return jsonify({"error": "Please enter a valid 10-digit phone number."}), 400
    if order_type == "delivery":
        if not address:
            return jsonify({"error": "Please enter a delivery address."}), 400
        where = "Delivery to: " + address
    elif order_type == "dinein":
        if not table:
            return jsonify({"error": "Please enter your table number."}), 400
        where = "Dine-in: Table " + table
    else:
        return jsonify({"error": "Please choose Home Delivery or Dine-in."}), 400

    items, total = build_items(data.get("items"))
    if items is None:
        return jsonify({"error": "Your cart is empty or has an invalid item."}), 400

    payment = check_payment(data.get("payment"))
    if payment is None:
        return jsonify({"error": "Please check your payment details."}), 400

    order = {"id": next_order_id, "user": email, "name": name, "phone": phone,
             "type": order_type, "where": where, "address": address, "table": table,
             "items": items, "total": total, "payment": payment,
             "time": datetime.now().strftime("%d %b %Y, %I:%M %p")}
    orders[next_order_id] = order
    next_order_id += 1
    return jsonify(order), 201


@app.route("/api/orders/<int:order_id>", methods=["DELETE"])
def cancel_order(order_id):
    order = orders.get(order_id)
    if not order or order["user"] != current_user():
        return jsonify({"error": "Order not found"}), 404
    del orders[order_id]
    return jsonify({"message": "Order cancelled"})


if __name__ == "__main__":
    app.run(debug=True)
