from requests import get
from Getting_access_to_SpotifyAPI import get_auth_header

def clean_characters(string):
    import re
    return re.sub(r'[^a-zA-Z0-9\u3040-\u30FF\u4E00-\u9FFF\u1100-\u11FF\u3130-\u318F\uAC00-\uD7AF\u0400-\u04FF\s]','',string)

class Spotify_requests:
    def __init__(self, token):
        self.token = token
    
    def __set_endpoint(self, endpoint_complement):
        url = 'https://api.spotify.com/v1/'
        return url + endpoint_complement
    
    def get_result(self, endpoint_complement):
        endpoint = self.__set_endpoint(endpoint_complement)
        return get(endpoint, headers=get_auth_header(self.token)).json()
    
class GetTracks(Spotify_requests):
    def __init__(self, token, trackName, offset, limit, clean):
        Spotify_requests.__init__(self, token)
        self.trackName = trackName
        self.offset = offset
        self.limit = limit
        self.clean = clean
    
    def access_to_results(self):
        if self.clean:
            self.trackName = clean_characters(self.trackName)
        endpoint_complement = 'search?' + f'q={self.trackName}&type=track&offset={self.offset}&limit={self.limit}'
        return self.get_result(endpoint_complement)['tracks']['items']

class GetSampleArtistTracks(Spotify_requests):
    def __init__(self, token, artistName, offset, limit, clean):
        Spotify_requests.__init__(self, token)
        self.artistName = artistName
        self.offset = offset
        self.limit = limit
        self.clean = clean
    
    def access_to_results(self):
        if self.clean:
            self.artistName = clean_characters(self.artistName)
        endpoint_complement = 'search?' + f'q=artist:{self.artistName}&type=track&offset={self.offset}&limit={self.limit}'
        return self.get_result(endpoint_complement)['tracks']['items']

class GetArtistID(Spotify_requests):
    def __init__(self, token, artistName, offset, limit, clean):
        Spotify_requests.__init__(self, token)
        self.artistName = artistName
        self.offset = offset
        self.limit = limit
        self.clean = clean
    
    def access_to_results(self):
        if self.clean:
            self.artistName = clean_characters(self.artistName)
        endpoint_complement = 'search?' + f'q={self.artistName}&type=artist&offset={self.offset}&limit={self.limit}'
        return self.get_result(endpoint_complement)['artists']['items']

class GetArtistAlbums(Spotify_requests):
    def __init__(self, token, artistID, offset, limit):
        Spotify_requests.__init__(self, token)
        self.artistID = artistID
        self.offset = offset
        self.limit = limit
    
    def access_to_results(self):
        endpoint_complement = f'artists/{self.artistID}/albums?limit={self.limit}&offset={self.offset}'
        return self.get_result(endpoint_complement)['items']

class GetAlbumTracks(Spotify_requests):
    def __init__(self, token, albumID):
        Spotify_requests.__init__(self, token)
        self.albumID = albumID
    
    def access_to_results(self):
        endpoint_complement = f'albums/{self.albumID}/tracks'
        return self.get_result(endpoint_complement)['items']
    
class GetComplementaryInfo(Spotify_requests):
    def __init__(self, token, datatype, ids):
        Spotify_requests.__init__(self, token)
        self.datatype = datatype
        self.ids = ids
        
    def access_to_results(self):
        if self.datatype not in ['tracks', 'albums', 'artists']:
            raise ValueError('Invalid option')       
        ids_string = ",".join(self.ids)
        endpoint_complement = f'{self.datatype}?ids={ids_string}'      
        return self.get_result(endpoint_complement)[self.datatype]