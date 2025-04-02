from flask import request, jsonify, render_template, redirect, url_for, flash
from app import app, db
from models import User, Post, Admin

# Rota para abrir a página inicial do site (página de login)
@app.route('/', methods=['GET'])
def form():
    return render_template('login.html')



# Rota para direcionar o usuário para a página de login
@app.route('/login_hub', methods=['GET'])
def login_hub():
    return render_template('login.html')



# Rota para retornar o template 'signup.html'
@app.route('/signup_hub', methods=['GET'])
def signup_hub():
    return render_template('signup.html')



# Controller de criação de usuário
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(username=data['username'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created"}), 201



# Rota para criar usuário na página de signup
@app.route('/createUser', methods=['POST'])
def createUser():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            # flash("Usuário ja existe.", "error")
            return render_template('signup.html')
        else:
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            return render_template('index.html', username=username)
    return render_template('signup.html')



# Controller de login para usuários existentes
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.password == data['password']:
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"message": "Invalid credentials"}), 401



# Rota para verificar login no banco de dados
@app.route('/verifyUser', methods=['POST'])
def verifyUser():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            return render_template('index.html', username=username)
        # else:
        #     flash("Nome de usuário ou senha incorretos.", "error")
        admin = Admin.query.filter_by(admin_name=username, admin_password=password).first()
        if admin:
            return render_template('admin.html')
    return render_template('login.html')



# Controller de listagem de usuários
@app.route('/users', methods=['GET'])
def list_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])



# Controller de busca de usuário por id
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if user:
        return jsonify(user.to_dict())
    return jsonify({"message": "User not found"}), 404



# Controller de edição de usuário
@app.route('/users', methods=['PUT'])
def edit_user():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username, password=password).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    if 'new_username' in data:
        user.username = data['new_username']
    if 'new_password' in data:
        user.password = data['new_password']
    
    db.session.commit()
    return jsonify({"message": "User updated"}), 200



# Controller de deleção de usuário
@app.route('/users', methods=['DELETE'])
def delete_user():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username, password=password).first()
    if not user:
        return jsonify({"message": "User not found or invalid credentials"}), 404
    if 'username' in data and 'password' in data:
        db.session.delete(user)
        
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200



# Controller de criação de post
@app.route('/users/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    new_post_content = data.get('content')

    user = User.query.filter_by(username=username, password=password).first()
    if not user:
        return jsonify({"message": "User not found or invalid credentials"}), 404

    new_post = Post(content=new_post_content, user_id=user.id)
    db.session.add(new_post)
    db.session.commit()

    return jsonify({"message": "Post created"}), 201



# Controller de listagem de todos os posts
@app.route('/users/posts', methods=['GET'])
def list_posts():
    posts = Post.query.all()
    return jsonify([post.to_dict() for post in posts])


# Controller de listagem de posts por id
@app.route('/users/posts/<int:id>', methods=['GET'])
def get_post(id):
    post = Post.query.get(id)
    if post:
        return jsonify(post.to_dict())
    return jsonify({"message": "Post not found"}), 404



# Controller de edição de post
@app.route('/users/posts', methods=['PUT'])
def edit_post():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    old_content = data.get('old_content')

    user = User.query.filter_by(username=username, password=password).first()
    if not user:
        return jsonify({"message": "User not found or invalid credentials"}), 404

    post = Post.query.filter_by(content=old_content, user_id=user.id).first()
    if not post:
        return jsonify({"message": "Post not found"}), 404

    post.content = data['new_content']
    db.session.commit()
    return jsonify({"message": "Post updated"}), 200



# Controller de deleção de post
@app.route('/users/posts', methods=['DELETE'])
def delete_post():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    content = data.get('content')
    
    user = User.query.filter_by(username=username, password=password).first()
    if not user:
        return jsonify({"message": "User not found or invalid credentials"}), 404
    
    post = Post.query.filter_by(content=content, user_id=user.id).first()
    if not post:
        return jsonify({"message": "Post not found"}), 404
    
    db.session.delete(post)
    db.session.commit()
    return jsonify({"message": "Post deleted"}), 200



# Controller de edição de usuário através de um admin
@app.route('/admins/users', methods=['PUT'])
def admin_edit_user():
    data = request.get_json()
    
    admin_name = data.get('admin_name')
    admin_password = data.get('admin_password')
    
    old_username = data.get('old_username')
    new_username = data.get('new_username')
    
    admin = Admin.query.filter_by(admin_name=admin_name, admin_password=admin_password).first()
    if not admin:
        return jsonify({"message": "Admin not found or invalid credentials"}), 404
    
    user = User.query.filter_by(username=old_username).first()
    if not user:
        return jsonify({"message": "User not found or invalid username"}), 404
    
    user.username = new_username
    db.session.commit()
    
    return jsonify({"message": "User edited by admin"}), 200
    
    

# Controller de deleção de usuário através de um admin
@app.route('/admins/users', methods=['DELETE'])
def admin_delete_user():
    data = request.get_json()
    
    admin_name = data.get('admin_name')
    admin_password = data.get('admin_password')
    
    username = data.get('username')
    
    admin = Admin.query.filter_by(admin_name=admin_name, admin_password=admin_password).first()
    if not admin:
        return jsonify({"message": "Admin not found or invalid credentials"}), 404
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted by admin"}), 200



# Controller de edição de post através de um admin
@app.route('/admins/users/posts', methods=['PUT'])
def admin_edit_post():
    data = request.get_json()
    
    admin_name = data.get('admin_name')
    admin_password = data.get('admin_password')
    
    username = data.get('username')
    
    old_content = data.get('old_content')
    
    admin = Admin.query.filter_by(admin_name=admin_name, admin_password=admin_password).first()
    if not admin:
        return jsonify({"message": "Admin not found or invalid credentials"}), 404
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "User not found or doesn't match with post"}), 404
    
    post = Post.query.filter_by(content=old_content, user_id=user.id).first()
    if not post:
        return jsonify({"message": "Post not found"}), 404

    post.content = data['new_content']
    db.session.commit()
    return jsonify({"message": "Post updated by admin"}), 200



# Controller de deleção de post através de um admin
@app.route('/admins/users/posts', methods=['DELETE'])
def admin_delete_post():
    data = request.get_json()
    
    admin_name = data.get('admin_name')
    admin_password = data.get('admin_password')
    
    username = data.get('username')
    
    content = data.get('content')
    
    admin = Admin.query.filter_by(admin_name=admin_name, admin_password=admin_password).first()
    if not admin:
        return jsonify({"message": "Admin not found or invalid credentials"}), 404
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "User not found or invalid credentials"}), 404
    
    post = Post.query.filter_by(content=content, user_id=user.id).first()
    if not post:
        return jsonify({"message": "Post not found"}), 404
    
    db.session.delete(post)
    db.session.commit()
    return jsonify({"message": "Post deleted by admin"}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    