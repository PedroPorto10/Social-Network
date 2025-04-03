from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {"id": self.id, "username": self.username, "is_admin": self.is_admin}

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(80), db.ForeignKey('user.username'), nullable=False)
    user = db.relationship('User', back_populates='posts')

    def to_dict(self):
        return {"id": self.id, "content": self.content, "user_id": self.user_id}

User.posts = db.relationship('Post', back_populates='user')

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_name = db.Column(db.String(255), unique=True, nullable=False)
    admin_password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {"id": self.id, "admin_name": self.admin_name, "admin_password": self.admin_password, "is_admin": self.is_admin}