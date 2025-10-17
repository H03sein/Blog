from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'myblogsecret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/blog_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

USERS = {
    'admin': 'admin123'
}

with app.app_context():
    try:
        db.create_all()  # سعی کن جدول‌ها رو بساز
        db.session.commit()
    except Exception as e:
        print(f"خطا در اتصال به دیتابیس: {e}")  # خطای ساده برای دیباگ

@app.route('/')
def index():
    selected_category = request.args.get('category')
    if selected_category:
        posts = Post.query.filter_by(category=selected_category).order_by(Post.date_posted.desc()).all()
    else:
        posts = Post.query.order_by(Post.date_posted.desc()).all()
    
    categories = db.session.query(Post.category).distinct().all()
    return render_template('index.html', posts=posts, categories=categories, selected_category=selected_category)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in USERS and USERS[username] == password:
            session['logged_in'] = True
            session['username'] = username
            flash('ورود موفقیت‌آمیز بود', 'success')
            return redirect(url_for('admin'))
        else:
            flash('نام کاربری یا رمز عبور نادرست است', 'error')
    
    return render_template('login.html')

@app.route('/admin')
def admin():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('admin.html', posts=posts)

@app.route('/add_post', methods=['POST'])
def add_post():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    title = request.form['title']
    content = request.form['content']
    category = request.form['category']
    
    new_post = Post(title=title, content=content, category=category)
    db.session.add(new_post)
    db.session.commit()
    
    flash('مطلب جدید با موفقیت منتشر شد', 'success')
    return redirect(url_for('admin'))

@app.route('/delete_post/<int:post_id>')
def delete_post(post_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    
    flash('مطلب مورد نظر حذف شد', 'success')
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.clear()
    flash('با موفقیت از سیستم خارج شدید', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)