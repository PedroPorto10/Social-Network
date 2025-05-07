from flask import request, jsonify, render_template, redirect, url_for, flash, session
from app import app, db
from models import User, Post, Admin

app.secret_key = 'poseidon'

@app.route('/', methods=['GET'])
def form():
    return render_template('login.html')



@app.route('/login_hub', methods=['GET'])
def login_hub():
    return render_template('login.html')



@app.route('/signup_hub', methods=['GET'])
def signup_hub():
    return render_template('signup.html')



@app.route('/index', methods=['GET'])
def index():
    if 'username' not in session:
        return redirect(url_for('login_hub'))

    username = session['username']
    users = [u.username for u in User.query.filter(User.username != username).all()]

    posts = Post.query.order_by(Post.id.desc()).all()

    return render_template('index.html', username=username, users=users, posts=posts)



@app.route('/user_profile', methods=['GET'])
def user_profile():
    if 'username' in session:
        username = session['username']
        posts = Post.query.order_by(Post.id.desc()).all()
        users = [u.username for u in User.query.filter(User.username != username).all()]
        return render_template('profile.html', username=session['username'], users=users, posts=posts)
    return redirect(url_for('login_hub'))



@app.route('/createUser', methods=['POST'])
def create_user():
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']

    if User.query.filter_by(username=username).first():
        flash("Usuário já existe.", "error")
        return redirect(url_for('signup_hub'))

    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    session['username'] = username
    return redirect(url_for('index'))



@app.route('/verifyUser', methods=['POST'])
def verify_user():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username, password=password).first()
    if user:
        session['username'] = user.username
        user_list = [u.username for u in User.query.filter(User.username != username).all()]
        return redirect(url_for('index'))

    admin = Admin.query.filter_by(admin_name=username, admin_password=password).first()
    if admin:
        return redirect(url_for('admin_dashboard'))

    flash("Nome de usuário ou senha incorretos.", "error")
    return redirect(url_for('login_hub'))



@app.route('/createPost', methods=['POST'])
def create_post():
    if 'username' not in session:
        flash("Você precisa estar logado para postar.", "error")
        return redirect(url_for('login_hub'))

    username = session['username']
    user = User.query.filter_by(username=username).first()

    if not user:
        flash("Usuário não encontrado.", "error")
        return redirect(url_for('login_hub'))

    content = request.form.get('content')

    if not content.strip():
        flash("O post não pode estar vazio.", "error")
        return redirect(url_for('index'))

    new_post = Post(content=content, username=username)
    db.session.add(new_post)
    db.session.commit()

    flash("Post publicado com sucesso!", "success")
    return redirect(url_for('index'))



# Controller para alterar o nome e/ou senha do usuário
@app.route('/users', methods=['PUT'])
def edit_user():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username'), password=data.get('password')).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    user.username = data.get('new_username', user.username)
    user.password = data.get('new_password', user.password)
    db.session.commit()
    return jsonify({"message": "User updated"}), 200



# Controller para deletar usuário
@app.route('/users', methods=['DELETE'])
def delete_user():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username'), password=data.get('password')).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200



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
    