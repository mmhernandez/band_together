from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models import band
from flask_app import app
from flask_bcrypt import Bcrypt
import re

bcrypt = Bcrypt(app)
db = "bands"
email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
name_regex = re.compile(r'^[a-zA-Z ,.\'-]+$')
password_regex = re.compile(r'^(^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).*$)?(^(?=.*\d)(?=.*[a-z])(?=.*[@#$%^&+=]).*$)?(^(?=.*\d)(?=.*[A-Z])(?=.*[@#$%^&+=]).*$)?(^(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=]).*$)?$')

class User:
    def __init__(self, data):
        self.id = data["id"]
        self.first_name = data["first_name"]
        self.last_name = data["last_name"]
        self.email = data["email"]
        self.password = data["password"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]
        self.bands = []

    @staticmethod
    def validate_registration(data):
        is_valid = True

        #first name validation
        if len(data["first_name"]) < 1:
            flash("First name required", "first_name")
            is_valid = False
        elif len(data["first_name"]) < 2:
            flash("First name must be at least 2 characters", "first_name")
            is_valid = False
        elif not name_regex.match(data["first_name"]):
            flash("Invalid first name", "first_name")
            is_valid = False

        #last name validation
        if len(data["last_name"]) < 1:
            flash("Last name required", "last_name")
            is_valid = False
        elif len(data["last_name"]) < 2:
            flash("Last name must be at least 2 characters", "last_name")
            is_valid = False
        elif not name_regex.match(data["last_name"]):
            flash("Invalid last name", "last_name")
            is_valid = False

        #email validation
        if len(data["email"]) < 1:
            flash("Email required", "email")
            is_valid = False
        elif not email_regex.match(data["email"]):
            flash("Invalid email", "email")
            is_valid = False
        elif User.get_by_email(data):
            flash("Email already in use", "email")
            is_valid = False
        
        # password validation
        if len(data["password"]) < 1:
            flash("Password required", "password")
            is_valid = False
        elif len(data["password"]) < 8:
            flash("Password must be at least 8 characters", "password")
            is_valid = False
        elif not password_regex.match(data["password"]):
            flash("Invalid password - must include a lowercase and uppercase letter, number, and special character.", "password")
            is_valid = False

        # password confirmation validation
        elif data["password"] != data["confirm_password"]:
            flash("Passwords do not match", "confirm_password")
            is_valid = False
        
        return is_valid
    
    @staticmethod
    def validate_login(data):
        is_valid = True
        user_info = User.get_by_email(data)

        if not user_info:
            flash("Email and/or password incorrect", "login")
            is_valid = False
        elif not bcrypt.check_password_hash(user_info.password, data['password']):
            flash("Email and/or password incorrect", "login")
            is_valid = False
        return is_valid
    
    @classmethod
    def get_by_email(cls, data):
        query = '''
            SELECT *
            FROM users
            WHERE email = %(email)s;
        '''
        results = connectToMySQL(db).query_db(query, data)
        if len(results) < 1:
            return False
        return cls(results[0])
    
    @classmethod
    def get_by_id(cls, data):
        query = '''
            SELECT *
            FROM users
            WHERE id = %(id)s;
        '''
        results = connectToMySQL(db).query_db(query, data)
        return cls(results[0])

    @classmethod
    def insert(cls, data):
        query = '''
            INSERT INTO users (first_name, last_name, email, password)
            VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s);
        '''
        hashed_password = bcrypt.generate_password_hash(data["password"])
        data.update({"password": hashed_password})
        return connectToMySQL(db).query_db(query, data)

    @classmethod
    def get_one_with_bands(cls, data):
        query = '''
            SELECT * 
            FROM users U
            LEFT JOIN bands B ON U.id = B.creator_id
            WHERE U.id = %(id)s;
        '''
        results = connectToMySQL(db).query_db(query, data)
        user_obj = cls(results[0])
        if results[0]['B.id'] == None:
            return user_obj
        else:
            for row in results:
                band_data = {
                    "id" : row["B.id"],
                    "name" : row["name"],
                    "genre" : row["genre"],
                    "city" : row["city"],
                    "created_at" : row["B.created_at"],
                    "updated_at" : row["B.updated_at"],
                    "creator_id" : row["creator_id"]
                }
                band_obj = band.Band(band_data)
                user_obj.bands.append(band_obj)
            return user_obj
    
    @classmethod
    def get_one_with_joined_bands(cls, data):
        query = '''
            SELECT * 
            FROM users U
            LEFT JOIN band_joins BJ on U.id = BJ.user_id
            LEFT JOIN bands B ON B.id = BJ.band_id
            WHERE  U.id = %(id)s;
        '''
        results = connectToMySQL(db).query_db(query, data)
        user_obj = cls(results[0])
        if results[0]["BJ.id"] == None:
            return user_obj
        else:
            for row in results:
                band_data = {
                    "id" : row["B.id"],
                    "name" : row["name"],
                    "genre" : row["genre"],
                    "city" : row["city"],
                    "created_at" : row["B.created_at"],
                    "updated_at" : row["B.updated_at"],
                    "creator_id" : row["creator_id"]
                }
                band_obj = band.Band(band_data)
                user_obj.bands.append(band_obj)
            return user_obj
    