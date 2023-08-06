from sandman.model import register, Model

class Artist(Model):
    __tablename__ = 'Artist'


class Album(Model):
    __tablename__ = 'Album'

class Playlist(Model):
    __tablename__ = 'Playlist'

class Genre(Model):
    __tablename__ = 'Genre'
    __endpoint__ = 'styles'
    __methods__ = ('GET', 'DELETE')

    @staticmethod
    def do_GET(resource=None):
        if isinstance(resource, list):
            return True
        elif resource and resource.GenreId == 1:
            return False
        return True

register((Artist, Album, Playlist))
register(Genre)
