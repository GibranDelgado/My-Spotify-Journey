from requests import get
from Getting_access_to_SpotifyAPI import get_auth_header

url = 'https://api.spotify.com/v1/'

def clean_characters(string):
    import re
    return re.sub(r'[^a-zA-Z0-9\u3040-\u30FF\u4E00-\u9FFF\u1100-\u11FF\u3130-\u318F\uAC00-\uD7AF\u0400-\u04FF\s]','',string)

def get_track(token, trackName, offset, clean):
    if clean:
        trackName = clean_characters(trackName)
    endpoint = url + 'search?' + f'q={trackName}&type=track&offset={offset}&limit=1'
    result = get(endpoint, headers=get_auth_header(token))
    result = result.json()['tracks']['items']
    
    return result

def get_artist(token, artistName, offset, clean):
    if clean:
        artistName = clean_characters(artistName)
    endpoint = url + 'search?' + f'q={artistName}&type=artist&offset={offset}&limit=1'
    result = get(endpoint, headers=get_auth_header(token))
    result = result.json()['artists']['items']
    
    return result

def get_tracks_from_artist(token, artistName, clean):
    if clean:
        artistName = clean_characters(artistName)
    endpoint = url + 'search?' + f'q=artist:{artistName}&type=track'
    all_results = []
    
    while endpoint:
        result = get(endpoint, headers=get_auth_header(token))
        data = result.json()
        all_results.extend(data['tracks']['items'])
        endpoint = data['tracks']['next']
    
    return all_results
    
def get_albums_from_artist(token, artistID):
    limit = 50
    offset = 0
    all_albums = []
    
    while True:
        endpoint = url + f'artists/{artistID}/albums?limit={limit}&offset={offset}'
        result = get(endpoint, headers=get_auth_header(token))
        current_albums = result.json()['items']
        all_albums.extend(current_albums)

        if len(current_albums) < limit:
            break
        else:
            offset += limit

    return all_albums

def get_album_tracks(token, albumID):
    endpoint = url + f'albums/{albumID}/tracks'
    result = get(endpoint, headers=get_auth_header(token))
    result = result.json()['items']
    
    return result

def  get_several_info(token, type_of_data, ids):
    if type_of_data not in ['tracks', 'audio-features', 'albums', 'artists']:
        raise ValueError('Invalid option')
    
    ids_string = ",".join(ids)
    endpoint = url + f'{type_of_data}?ids={ids_string}'
    
    if type_of_data=='audio-features':
        type_of_data = 'audio_features'
    
    result = get(endpoint, headers=get_auth_header(token))
    result = result.json()[type_of_data]
    
    return result