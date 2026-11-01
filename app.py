from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

# ---------- Restaurant details ----------
restaurant = {
    "name": "Spice Garden",
    "tagline": "Authentic Indian food, made fresh every day",
    "address": "Shop 12, Sector 29 Market, Gurugram, Haryana 122001",
    "phone": "+91 98765 43210",
    "email": "hello@spicegarden.example",
    "hours": "Open daily: 12:00 pm - 11:00 pm",
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

orders = {}      # order id -> order
next_order_id = 1


# ---------- Frontend pages ----------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/checkout")
def checkout():
    return render_template("checkout.html")


# ---------- API routes ----------
@app.route("/api/restaurant", methods=["GET"])
def get_restaurant():
    return jsonify(restaurant)


@app.route("/api/menu", methods=["GET"])
def get_menu():
    category = request.args.get("category")      # e.g. /api/menu?category=Drinks
    if category:
        return jsonify([d for d in menu if d["category"] == category])
    return jsonify(menu)


@app.route("/api/orders", methods=["GET"])
def get_orders():
    return jsonify(list(orders.values()))


@app.route("/api/orders", methods=["POST"])
def place_order():
    global next_order_id
    data = request.get_json()

    # Check that all fields are filled
    if not data.get("name") or not data.get("phone") or not data.get("address") or not data.get("items"):
        return jsonify({"error": "Please fill all details and add at least one dish."}), 400

    # Work out the total on the server using real menu prices
    items, total = [], 0
    for item in data["items"]:
        dish = next((d for d in menu if d["id"] == item["id"]), None)
        if dish:
            qty = int(item["qty"])
            items.append({"name": dish["name"], "qty": qty, "price": dish["price"]})
            total += dish["price"] * qty

    order = {"id": next_order_id, "name": data["name"], "phone": data["phone"],
             "address": data["address"], "items": items, "total": total}
    orders[next_order_id] = order
    next_order_id += 1
    return jsonify(order), 201


@app.route("/api/orders/<int:order_id>", methods=["DELETE"])
def cancel_order(order_id):
    if order_id in orders:
        del orders[order_id]
        return jsonify({"message": "Order cancelled"})
    return jsonify({"error": "Order not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
