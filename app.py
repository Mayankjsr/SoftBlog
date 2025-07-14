from flask import Flask, render_template, request, redirect, url_for, flash, session
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key!

USERS_FILE = 'users.json'
BLOGS_FILE = 'blogs.json'

# Ensure users.json exists
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        json.dump([], f)

# Ensure blogs.json exists
if not os.path.exists(BLOGS_FILE):
    with open(BLOGS_FILE, 'w') as f:
        json.dump([], f)

def load_users():
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def load_blogs():
    with open(BLOGS_FILE, 'r') as f:
        return json.load(f)

def save_blogs(blogs):
    with open(BLOGS_FILE, 'w') as f:
        json.dump(blogs, f, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']

        users = load_users()

        if any(user['email'] == email for user in users):
            flash('Email already registered. Please log in.', 'error')
            return redirect(url_for('create_account'))

        users.append({
            'name': name,
            'email': email,
            'password': password
        })
        save_users(users)

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('create_account.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        users = load_users()

        for user in users:
            if user['email'] == email and user['password'] == password:
                session['user'] = {
                    'name': user['name'],
                    'email': user['email']
                }
                return redirect(url_for('user_page'))

        flash('Invalid email or password. Please try again.', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/user')
def user_page():
    if 'user' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('login'))

    name = session['user']['name']
    parts = name.split()
    if len(parts) >= 2:
        initials = parts[0][0].upper() + parts[1][0].upper()
    else:
        initials = parts[0][0].upper()

    return render_template('user.html', username=name, initials=initials)

@app.route('/create_blog', methods=['GET', 'POST'])
def create_blog():
    if 'user' not in session:
        flash('Please log in to create a blog.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title'].strip()
        content = request.form['content'].strip()
        font = request.form['font']
        background = request.form['background']

        if not title or not content:
            flash('Title and content are required.', 'error')
            return render_template("create_blog.html")

        # Save to blogs.json
        blogs = load_blogs()
        blogs.append({
            'title': title,
            'content': content,
            'font': font,
            'background': background,
            'author': session['user']['name'],
            'email': session['user']['email']
        })
        save_blogs(blogs)

        flash('Blog published!', 'success')
        return render_template("create_blog.html")

    return render_template("create_blog.html")

@app.route('/preview_blog', methods=['POST'])
def preview_blog():
    if 'user' not in session:
        flash('Please log in to preview your blog.', 'error')
        return redirect(url_for('login'))

    title = request.form['title']
    content = request.form['content']
    font = request.form['font']
    background = request.form['background']

    # Map background value to image file
    bg_map = {
        "nebula.jpg": "14121195_5430284.jpg",
        "stars.jpg": "14658085_5512545.jpg",
        "galaxy.jpg": "72657892_9805703.jpg"
    }
    bg_image = bg_map.get(background, "14121195_5430284.jpg")

    return render_template(
        "preview.html",
        title=title,
        content=content,
        font=font,
        bg_image=bg_image,
        author=session['user']['name']
    )

@app.route('/read_blogs')
def read_blogs():
    blogs = load_blogs()
    blogs = blogs[::-1]  # Show newest first
    return render_template('read_blogs.html', blogs=blogs)

# NEW: Route to preview a blog by its index
@app.route('/blog/<int:blog_id>')
def blog_preview(blog_id):
    blogs = load_blogs()
    blogs = blogs[::-1]  # Because read_blogs reverses the list
    if 0 <= blog_id < len(blogs):
        blog = blogs[blog_id]
        # Map background value to image file
        bg_map = {
            "nebula.jpg": "14121195_5430284.jpg",
            "stars.jpg": "14658085_5512545.jpg",
            "galaxy.jpg": "72657892_9805703.jpg"
        }
        bg_image = bg_map.get(blog.get('background', ''), "14121195_5430284.jpg")
        return render_template(
            "preview.html",
            title=blog['title'],
            content=blog['content'],
            font=blog['font'],
            bg_image=bg_image,
            author=blog['author']
        )
    else:
        return "Blog not found", 404

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)