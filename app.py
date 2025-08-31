from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

USERS_FILE = "users.txt"
MESSAGES_FILE = "messages.txt"

# Kullanıcı kayıt / kontrol
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    users = {}
    with open(USERS_FILE, "r") as f:
        for line in f:
            username, password = line.strip().split(",")
            users[username] = password
    return users

def save_user(username, password):
    with open(USERS_FILE, "a") as f:
        f.write(f"{username},{password}\n")
    # Kullanıcının arkadaş listesi için boş txt oluştur
    open(f"{username}.txt", "a").close()

# Mesaj işlemleri
def load_messages():
    if not os.path.exists(MESSAGES_FILE):
        return []
    messages = []
    with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(",", 2)
            if len(parts) == 3:
                sender, receiver, msg = parts
                messages.append({"from": sender, "to": receiver, "msg": msg})
    return messages

def save_message(sender, receiver, msg):
    with open(MESSAGES_FILE, "a", encoding="utf-8") as f:
        f.write(f"{sender},{receiver},{msg}\n")

# Arkadaş işlemleri
def load_friends(user):
    filename = f"{user}.txt"
    if not os.path.exists(filename):
        return []
    with open(filename, "r") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def add_friend(user, friend):
    # Kullanıcı kendi listesine eklesin
    filename_user = f"{user}.txt"
    friends = load_friends(user)
    if friend not in friends:
        with open(filename_user, "a") as f:
            f.write(friend + "\n")

    # Arkadaşın listesine de ekle
    filename_friend = f"{friend}.txt"
    if not os.path.exists(filename_friend):
        open(filename_friend, "a").close()  # dosya yoksa oluştur
    friend_list = load_friends(friend)
    if user not in friend_list:
        with open(filename_friend, "a") as f:
            f.write(user + "\n")


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        action = request.form.get("action")
        username = request.form.get("username")
        password = request.form.get("password")
        users = load_users()

        if action == "signup":
            if username in users:
                return "Kullanıcı zaten var!"
            save_user(username, password)
            session["user"] = username
            return redirect(url_for("chat"))

        elif action == "login":
            if username in users and users[username] == password:
                session["user"] = username
                return redirect(url_for("chat"))
            else:
                return "Hatalı giriş!"

    return render_template("login.html")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "user" not in session:
        return redirect(url_for("login"))

    current_user = session["user"]
    friends = load_friends(current_user)
    selected_friend = request.args.get("friend")
    messages = []

    # Mesaj gönderme
    if request.method == "POST":
        if "new_friend" in request.form:  # Arkadaş ekleme
            new_friend = request.form.get("new_friend")
            if new_friend:
                add_friend(current_user, new_friend)
            return redirect(url_for("chat"))

        elif "message" in request.form and selected_friend:
            message = request.form.get("message")
            if message:
                save_message(current_user, selected_friend, message)
            return redirect(url_for("chat", friend=selected_friend))

    # Sohbet geçmişi (sadece seçilen arkadaş ile)
    if selected_friend:
        for m in load_messages():
            if (m["from"] == current_user and m["to"] == selected_friend) or \
               (m["from"] == selected_friend and m["to"] == current_user):
                messages.append(m)

    return render_template("chat.html", 
                           user=current_user, 
                           friends=friends, 
                           selected_friend=selected_friend, 
                           messages=messages)

if __name__ == "__main__":
    app.run(debug=True)
