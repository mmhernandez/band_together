from flask import flash
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import user

db = "bands"

class Band:
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.genre = data["genre"]
        self.city = data["city"]
        self.created_at = data["created_at"]
        self.updated_at = data["updated_at"]
        self.creator_id = data["creator_id"]
        self.creator = None
        self.can_join = True
    
    @staticmethod
    def validate_band(data):
        is_valid = True

        # name validation
        if len(data["name"]) < 1:
            flash("Band name required", "name")
            is_valid = False
        elif len(data["name"]) < 2:
            flash("Band name must be at least 2 characters", "name")
            is_valid = False
        
        # genre validation
        if len(data["genre"]) < 1:
            flash("Music genre required", "genre")
            is_valid = False
        elif len(data["genre"]) < 2:
            flash("Music genre must be at least 2 characters", "genre")
            is_valid = False

        # city validation
        if len(data["city"]) < 1:
            flash("Home City required", "city")
            is_valid = False
        elif len(data["city"]) < 2:
            flash("Home City must be at least 2 characters", "city")
            is_valid = False

        return is_valid
    
    @classmethod
    def insert_band(cls, data):
        query = '''
            INSERT INTO bands (name, genre, city, creator_id)
            VALUES (%(name)s, %(genre)s, %(city)s, %(creator)s);
        '''
        connectToMySQL(db).query_db(query, data)

    @classmethod
    def get_all_with_creator(cls, session_user_id):
        query = '''
            SELECT *
            FROM bands B
            LEFT JOIN users U on U.id = B.creator_id
        '''
        results = connectToMySQL(db).query_db(query)
        bands = []
        if len(results) < 1:
            return bands
        else:
            bands = []
            for row in results:
                band_obj = cls(row)
                user_obj = {
                    "id" : row["U.id"],
                    "first_name" : row["first_name"],
                    "last_name" : row["last_name"],
                    "email" : row["email"],
                    "password" : row["password"],
                    "created_at" : row["U.created_at"],
                    "updated_at" : row["U.updated_at"]
                }
                band_obj.creator = user.User(user_obj)
                join_bool = cls.band_joins({"band_id": band_obj.id, "creator_id": session_user_id})
                band_obj.can_join = join_bool
                bands.append(band_obj)
        return bands
    
    @classmethod
    def get_by_id(cls, data):
        query = '''
            SELECT * 
            FROM bands
            WHERE id = %(id)s;
        '''
        results = connectToMySQL(db).query_db(query, data)
        return cls(results[0])
    
    @classmethod
    def update_band(cls, data):
        query = '''
            UPDATE bands
            SET name = %(name)s,
                genre = %(genre)s,
                city = %(city)s
            WHERE id = %(id)s;
        '''
        connectToMySQL(db).query_db(query, data)

    @classmethod
    def delete_band(cls, data):
        query = '''
            DELETE FROM bands
            WHERE id = %(id)s;
        '''
        connectToMySQL(db).query_db(query, data)

    @classmethod
    def band_joins(cls, data):
        query = '''
            SELECT COUNT(id) AS count
            FROM band_joins
            WHERE band_id = %(band_id)s
                AND user_id = %(creator_id)s;
        '''
        result = connectToMySQL(db).query_db(query, data)
        if result[0]['count'] == 0:
            return True
        return False
    
    @classmethod
    def add_join(cls, data):
        query = '''
            INSERT INTO band_joins (band_id, user_id)
            VALUES (%(band_id)s, %(user_id)s)
        '''
        connectToMySQL(db).query_db(query, data)
    
    @classmethod
    def delete_band_join(cls, data):
        query = '''
            DELETE FROM band_joins
            WHERE band_id = %(band_id)s
                AND user_id = %(user_id)s;
        '''
        connectToMySQL(db).query_db(query, data)