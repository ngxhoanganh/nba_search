from modules.analysis import isNBA
from modules.scraper import get_playoff_bracket, get_standings
from modules.transformer import create_html_bracket
from modules.query import Query
from modules.controller.userController import UserController
from modules.controller.postController import PostController
from modules.controller.commentController import CommentController
from datetime import datetime
from data.text_data import unsure, non_nba
from flask import Flask, render_template, request, jsonify, redirect, flash, send_file, session
import json
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Thêm secret key để dùng session nếu cần

UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Giới hạn kích thước tệp (16 MB)

# Các tuyến hiện có
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/home")
def home2():
    return render_template("home.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/blog")
def blog():
    return render_template("blogs.html")

@app.route("/authors")
def authors():
    return render_template("authors.html")

@app.route("/predictions")
def predictions():
    bracket = get_playoff_bracket()
    bracket = create_html_bracket(bracket)
    west_standings = get_standings("west")
    east_standings = get_standings("east")
    return render_template("predictions.html", bracket=bracket, west_standings=west_standings, east_standings=east_standings)

@app.route("/download/<string:id>", methods=['GET', 'POST'])
def download(id):
    if id is None:
        self.Error(400)
    try:
        blog_map = {
            "1": "https://drive.google.com/uc?export=download&id=13FmzW70fMMfTwrypxzJRG-J6woty8ePz",
            "2": "https://drive.google.com/uc?export=download&id=13FmzW70fMMfTwrypxzJRG-J6woty8ePz",
            "3": "https://drive.google.com/uc?export=download&id=13FmzW70fMMfTwrypxzJRG-J6woty8ePz"
        }
        return redirect(blog_map[id])
    except Exception as e:
        self.log.exception(e)
        self.Error(400)

@app.route("/bot-msg", methods=['POST'])
def get_bot_response():
    usr_msg = request.form['msg']
    handler = Query(usr_msg)
    response = handler.process()
    return jsonify(response)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        name = data.get('name')
        
        user_id = UserController.create_user(username, password, email, name)
        if user_id:
            print("Đăng ký thành công!")
            return jsonify({
                "message": "Đăng ký thành công!",
                "status": "success"
            }), 200
        else:
            print("Đã xảy ra lỗi. Vui lòng thử lại!")
            return jsonify({
                "message": "Đã xảy ra lỗi. Vui lòng thử lại!",
                "status": "danger"
            }), 400
    else:  # GET
        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = UserController.get_user(username, password)
        if user:
            print("Đăng nhập thành công!")
            return jsonify({
                "message": "Đăng nhập thành công!",
                "status": "success",
                "user": user.__dict__
            }), 200
        else:
            print("Tài khoản hoặc mật khẩu không đúng, vui lòng thử lại!")
            return jsonify({
                "message": "Tài khoản hoặc mật khẩu không đúng, vui lòng thử lại!",
                "status": "danger"
            }), 400
    else:  # GET
        return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    print("Đăng xuất thành công!")
    return redirect('/')

@app.route('/getallposts', methods=['POST'])
def get_posts():
    data = request.get_json()
    start = data.get('start', 0)
    limit = data.get('limit', 10)
    posts = PostController.get_posts(start, limit)
    
    if posts:
        print("Lấy bài viết thành công!")
        return jsonify({
            "message": "Lấy bài viết thành công!",
            "status": "success",
            "posts": posts
        }), 200
    else:
        print("Không có bài viết nào!")
        return jsonify({
            "message": "Không có bài viết nào!",
            "status": "danger"
        }), 400

@app.route('/new_post', methods=['GET'])
def new_post():
    return render_template('new_post.html')

@app.route('/post_detail', methods=['GET'])
def post_detail():
    post_id = request.args.get('post_id')
    if not post_id:
        print("Thiếu post_id!")
        return jsonify({
            "message": "Thiếu post_id!",
            "status": "danger"
        }), 400
    post = PostController.get_post_by_id(post_id)
    if post:
        print("Lấy chi tiết bài viết thành công!")
        return render_template('post_detail.html', post=post)
    else:
        print("Bài viết không tồn tại!")
        return jsonify({
            "message": "Bài viết không tồn tại!",
            "status": "danger"
        }), 404

@app.route('/createpost', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        data = json.loads(request.form.get('data'))
        userId = data.get('userId')
        title = data.get('title')
        content = data.get('content')
        if 'file' not in request.files:
            imagePath = None
        else:
            file = request.files['file']
            if file.filename == '':
                imagePath = None
            else:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                imagePath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        newPost = PostController.create_post(userId, title, content, imagePath)
        if newPost:
            print("Tạo bài viết thành công!")
            return jsonify({
                "message": "Tạo bài viết thành công!",
                "status": "success"
            }), 200
        else:
            print("Đã xảy ra lỗi. Vui lòng thử lại!")
            if imagePath and os.path.exists(imagePath):
                os.remove(imagePath)
            return jsonify({
                "message": "Đã xảy ra lỗi khi tạo bài viết. Vui lòng thử lại!",
                "status": "danger"
            }), 400

@app.route('/getpostbyid', methods=['POST'])
def get_post_by_id():
    data = request.get_json()
    postId = data.get('postId')

    post = PostController.get_post_by_id(postId)
    if post:
        print("Lấy bài viết thành công!")
        return jsonify({
            "message": "Lấy bài viết thành công!",
            "status": "success",
            "post": post
        }), 200
    else:
        print("Đã xảy ra lỗi. Vui lòng thử lại!")
        return jsonify({
            "message": "Đã xảy ra lỗi khi lấy bài viết. Vui lòng thử lại!",
            "status": "danger"
        }), 400

@app.route('/comment/create', methods=['POST'])
def create_comment():
    data = request.get_json()
    postId = data.get('postId')
    userId = data.get('userId')
    content = data.get('content')

    comment_id = CommentController.create_comment(postId, userId, content)
    if comment_id:
        return jsonify({
            "message": "Bình luận đã được tạo!",
            "status": "success",
            "commentId": comment_id
        }), 201
    else:
        return jsonify({
            "message": "Tạo bình luận thất bại!",
            "status": "danger"
        }), 500

@app.route('/comments/<int:post_id>', methods=['GET'])
def get_comments(post_id):
    comments = CommentController.get_comments_by_post(post_id)
    if comments:
        print("Lấy bình luận thành công!")
        return jsonify({
            "message": "Lấy bình luận thành công!",
            "status": "success",
            "comments": comments
        }), 200
    else:
        print("Chưa có bình luận nào!")
        return jsonify({
            "message": "Chưa có bình luận nào!",
            "status": "success",
            "comments": []
        }), 200

@app.route('/upvote', methods=['POST'])
def upvote_post():
    data = request.get_json()
    post_id = data.get('postId')
    user_id = data.get('userId')
    success = PostController.upvote_post(user_id, post_id)
    if success:
        return jsonify({
            "message": "Upvote thành công!",
            "status": "success"
        }), 200
    else:
        return jsonify({
            "message": "Không thể upvote bài viết!",
            "status": "danger"
        }), 400

@app.route('/download/image/<filename>')
def download_image(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(filepath, mimetype='image/jpeg')

if __name__ == "__main__":
    app.run()