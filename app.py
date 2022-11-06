from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False

db = SQLAlchemy(app)

api = Api(app)
movies_ns = api.namespace('movies')
directors_ns = api.namespace('directors')
genres_ns = api.namespace('genres')

db.drop_all()
db.create_all()


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


movies_schema = MovieSchema(many=True)
movie_schema = MovieSchema()
directors_schema = DirectorSchema(many=True)
director_schema = DirectorSchema()
genres_schema = GenreSchema(many=True)
genre_schema = GenreSchema()


@movies_ns.route('/')
class MoviesView(Resource):

    def get(self):

        try:
            movies = Movie.query.all()

            director_id = request.args.get('director_id')
            genre_id = request.args.get('genre_id')

            if director_id:
                movies = movies.filter(Movie.director_id == director_id)

            if genre_id:
                movies = movies.filter(Movie.genre_id == genre_id)

            if director_id and genre_id:
                movies = movies.filter(Movie.director_id == director_id, Movie.genre_id == genre_id)

            return movies_schema.dump(movies), 200, {'Content-Type': 'application/json; charset=utf-8'}

        except Exception as e:
            return str(e), 404

    def post(self):

        try:
            req_json = request.json
            new_movie = Movie(**req_json)
            with db.session.begin():
                db.session.add(new_movie)
            return "", 201

        except Exception as e:
            return str(e), 404


@movies_ns.route('/<int:mid>')
class MovieView(Resource):

    def get(self, mid):

        try:
            movie = Movie.query.get(mid)
            if not movie:
                return "Такого фильма нет в базе данных", 404
            return movie_schema.dump(movie), 200, {'Content-Type': 'application/json; charset=utf-8'}

        except Exception as e:
            return str(e), 404

    def put(self, mid):

        try:
            movie = Movie.query.get(mid)

            if not movie:
                return "Такого фильма нет в базе данных", 404
            req_json = request.json
            movie.title = req_json.get("title")
            movie.description = req_json.get("description")
            movie.trailer = req_json.get("trailer")
            movie.year = req_json.get("year")
            movie.rating = req_json.get("rating")
            movie.genre_id = req_json.get("genre_id")
            movie.director_id = req_json.get("director_id")
            db.session.add(movie)
            db.session.commit()
            return "", 204

        except Exception as e:
            return str(e), 404

    def patch(self, mid):

        try:
            movie = Movie.query.get(mid)

            if not movie:
                return "Такого фильма нет в базе данных", 404

            req_json = request.json

            if "title" in req_json:
                movie.title = req_json.get("title")
            if "description" in req_json:
                movie.description = req_json.get("description")
            if "trailer" in req_json:
                movie.trailer = req_json.get("trailer")
            if "year" in req_json:
                movie.year = req_json.get("year")
            if "rating" in req_json:
                movie.rating = req_json.get("rating")
            if "genre_id" in req_json:
                movie.genre_id = req_json.get("genre_id")
            if "director_id" in req_json:
                movie.director_id = req_json.get("director_id")
            db.session.add(movie)
            db.session.commit()
            return "", 204

        except Exception as e:
            return str(e), 404

    def delete(self, mid):

        try:
            movie = Movie.query.get(mid)

            if not movie:
                return "Такого фильма нет в базе данных", 404

            db.session.delete(movie)
            db.session.commit()
            return "", 204

        except Exception as e:
            return str(e), 404


@directors_ns.route('/')
class DirectorsView(Resource):
    def get(self):

        try:
            directors = Director.query.all()
            return movies_schema.dump(directors), 200, {'Content-Type': 'application/json; charset=utf-8'}

        except Exception as e:
            return str(e), 404

    def post(self):

        try:
            req_json = request.json
            new_director = Director(**req_json)
            with db.session.begin():
                db.session.add(new_director)
            return "", 201

        except Exception as e:
            return str(e), 404


@directors_ns.route('/<int:did>')
class DirectorView(Resource):
    def get(self, did):

        try:
            director = Director.query.get(did)
            if not director:
                return "Такого продюсера нет в базе данных", 404

            return movie_schema.dump(director), 200, {'Content-Type': 'application/json; charset=utf-8'}

        except Exception as e:
            return str(e), 404

    def put(self, did):

        try:
            director = Director.query.get(did)

            if not director:
                return "Такого продюсера нет в базе данных", 404
            req_json = request.json
            director.name = req_json.get("name")
            db.session.add(director)
            db.session.commit()
            return "", 204

        except Exception as e:
            return str(e), 404

    def delete(self, did):

        try:
            director = Director.query.get(did)

            if not director:
                return "Такого продюсера нет в базе данных", 404

            db.session.delete(director)
            db.session.commit()
            return "", 204

        except Exception as e:
            return str(e), 404


@genres_ns.route('/')
class GenresView(Resource):
    def get(self):

        try:
            genres = Genre.query.all()
            return movies_schema.dump(genres), 200, {'Content-Type': 'application/json; charset=utf-8'}

        except Exception as e:
            return str(e), 404

    def post(self):

        try:
            req_json = request.json
            new_genre = Genre(**req_json)
            with db.session.begin():
                db.session.add(new_genre)
            return "", 201

        except Exception as e:
            return str(e), 404


@genres_ns.route('/<int:gid>')
class GenreView(Resource):
    def get(self, gid):

        try:
            genre = Genre.query.get(gid)
            if not genre:
                return "Такого жанра нет в базе данных", 404

            return movie_schema.dump(genre), 200, {'Content-Type': 'application/json; charset=utf-8'}

        except Exception as e:
            return str(e), 404

    def put(self, gid):

        try:
            genre = Genre.query.get(gid)

            if not genre:
                return "Такого жанра нет в базе данных", 404

            req_json = request.json
            genre.name = req_json.get("name")
            db.session.add(genre)
            db.session.commit()
            return "", 204

        except Exception as e:
            return str(e), 404

    def delete(self, gid):

        try:
            genre = Genre.query.get(gid)

            if not genre:
                return "Такого жанра нет в базе данных", 404

            db.session.delete(genre)
            db.session.commit()
            return "", 204

        except Exception as e:
            return str(e), 404


if __name__ == '__main__':
    app.run(debug=True)
