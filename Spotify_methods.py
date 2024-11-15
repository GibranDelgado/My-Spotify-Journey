import pandas as pd
import time
import Spotify_utilities as Utilities

delay = 1/60

def Merge_the_results(DF, Results):
    columns = ['artistName','trackName']    

    return DF.loc[:, columns].merge(Results, how='left', on=columns)

def Separate_results(Results):
    Successful_tracks_results = Results[~Results.trackID.isna()].reset_index(drop=True)
    Missing_tracks_results = Results[Results.trackID.isna()].reset_index(drop=True)
    
    return Successful_tracks_results, Missing_tracks_results

def Saving_the_results(Result, Multiple_results):
    if Multiple_results:
        artistName = list(map(lambda x:x['artists'][0]['name'], Result))
        trackName = list(map(lambda x:x['name'], Result))
        albumName = list(map(lambda x:x['album']['name'], Result))
        trackID = list(map(lambda x:x['id'], Result))
        artistID = list(map(lambda x:x['artists'][0]['id'], Result))
        albumID = list(map(lambda x:x['album']['id'], Result))
        
        Temp_results = pd.DataFrame({'artistName':artistName, 'trackName':trackName, 
                                     'albumName':albumName, 'trackID':trackID, 
                                     'artistID':artistID, 'albumID':albumID})
    else:
        artistName = Result['artists'][0]['name']
        trackName = Result['name']
        albumName = Result['album']['name']
        trackID = Result['id']
        artistID = Result['artists'][0]['id']
        albumID = Result['album']['id']
        
        Temp_results = pd.DataFrame({'artistName':artistName, 'trackName':trackName, 
                                     'albumName':albumName, 'trackID':trackID, 
                                     'artistID':artistID, 'albumID':albumID}, index=[0])

    return Temp_results
    
#Method 1
def Getting_tracks_info_in_one_result_per_call(token, DF):
    def Making_the_search(token, trackName):
        try:
            Result = Utilities.get_track(token, trackName, offset=0, clean=False)
        except:
            Result = Utilities.get_track(token, trackName, offset=0, clean=True)
        
        if Result:
            Result = Result[0]
        return Result
    
    Results = None   
    print('\n***** Searching the tracks  *****')
    for i,row in DF.iterrows():
        print(f'Searching the track: {row.trackName}')
        Result = Making_the_search(token, row.trackName)
        time.sleep(delay)
        
        if Result['name'].lower()!=row.trackName or Result['artists'][0]['name']!=row.artistName:
            Result = Making_the_search(token, row.trackName+" "+row.artistName)

        if Result['name'].lower()==row.trackName.lower() and Result['artists'][0]['name']==row.artistName:
            Temp_results = Saving_the_results(Result, Multiple_results=False)
            Results = pd.concat([Results, Temp_results])
                
    Results = Merge_the_results(DF, Results)    
    Successful_results, Missing_results = Separate_results(Results)
    
    return Successful_results, Missing_results

#Method 2
def Getting_tracks_info_in_multiple_results_per_call(token, DF):
    Results = None
    print('\n***** Searching the tracks  *****')
    for _,row in DF.iterrows():
        print(f'Searching the track: {row.trackName}')
        offset = 0
        #Cuidado, aqui estoy moviendole al offset, solo agarra el primer resultado de muchos que debería tomar
        All_tracks = Utilities.get_track(token, row.trackName, offset, clean=False)
        time.sleep(delay)

        while True:
            if offset<1000:
                if All_tracks:
                    if len(All_tracks)==1:
                        Temp_results = Saving_the_results(All_tracks[0], Multiple_results=False)
                    else:
                        Temp_results = Saving_the_results(All_tracks, Multiple_results=True)
                    
                    Temp_results = Temp_results[(Temp_results.trackName == row.trackName) &
                                                (Temp_results.artistName == row.artistName)]
                    if Temp_results.shape[0]>0:
                        Results = pd.concat([Results, Temp_results])
                        break
                    else:
                        offset+=50
                else:
                    break
            else:
                break
    
    Results = Results.groupby(['artistName', 'trackName']).first().reset_index()
    Results = Merge_the_results(DF, Results)
    Successful_results, Missing_results = Separate_results(Results)

    return Successful_results, Missing_results

#Method 3
def Getting_tracks_in_multiple_artist_tracks(token, DF):
    from operator import itemgetter
    
    Artists = pd.unique(DF.artistName)

    Results = None
    print('\n***** Searching in the artist tracks *****')
    for artist in Artists:
        print(f'Searching the artist: {artist}')
        
        tracks = Utilities.get_tracks_from_artist(token, artist, clean=False)
        tracks = list(filter(lambda x:x is not None, tracks)) #Filter those results different from None
        
        artistNames_results = pd.Series(map(lambda x:x['artists'][0]['name'], tracks))
        index_matching_results = artistNames_results[artistNames_results==artist].index
        time.sleep(delay)
        
        if len(index_matching_results)>0:
            Matched_results = itemgetter(*index_matching_results)(tracks)
            
            if len(index_matching_results)==1:
                Temp_results = Saving_the_results(Matched_results, Multiple_results=False)
                Results = pd.concat([Results, Temp_results])
            else:
                Temp_results = Saving_the_results(Matched_results, Multiple_results=True)
                Results = pd.concat([Results, Temp_results])
    
    Results = Results.groupby(['artistName', 'trackName']).first().reset_index()
    Results = Merge_the_results(DF, Results)
    Successful_results, Missing_results = Separate_results(Results)
    
    return Successful_results, Missing_results
        
#Method 4
def Getting_tracks_info_in_artist_dischography(token, DF):
    def Searching_artist_ids(token, Artists):
        list_of_artists = []
        
        for artist in Artists:
            print(f'\nSearching the artistID of: {artist}')
            Result = Utilities.get_artist(token, artist, offset=0, clean=False)
            time.sleep(delay)
        
            if not Result or Result[0]['name']!=artist:
                Result = Utilities.get_artist(token, artist, offset=0, clean=True)
                time.sleep(delay)
            
            if Result and Result[0]['name']==artist:
                print(f'Artist found: {Result[0]["name"]}')
                list_of_artists.append({'artistName':Result[0]["name"], 'artistID':Result[0]["id"]})
            else:
                offset = 0
                while True:
                    if offset<1000:
                        Result = Utilities.get_artist(token, artist, offset, clean=False)
                        time.sleep(delay)
                        
                        if len(Result)>0:
                            artist_results = pd.Series(map(lambda x:x['name'], Result))
                            artist_results = artist_results[artist_results==artist].index
                            
                            if len(artist_results)>0:
                                print(f'Artist found: {artist}')
                                list_of_artists.append({'artistName':Result[artist_results[0]]['name'], 
                                                        'artistID':Result[artist_results[0]]['id']})
                                break                           
                            else:
                                offset+=50
                        else:
                            break
                    else:
                        break
        
        return pd.DataFrame(list_of_artists)
    
    def Searching_in_artist_dischography(token, DF, Artists_info):
        Results = None
        DF_artist_tracks = DF[['artistName','trackName']]
        
        for _,row in Artists_info.iterrows():
            print(f'\nSearching in {row.artistName} dischography')
            Tracks_to_search = DF_artist_tracks[DF_artist_tracks.artistName==row.artistName]
            albums = Utilities.get_albums_from_artist(token, row.artistID)
            
            if albums:
                for album in albums:
                    print(f"album: {album['name']}")
                    
                    if Tracks_to_search.shape[0]>0:
                        album_tracks = Utilities.get_album_tracks(token, album['id'])
                        time.sleep(delay)
                        album_tracks = pd.DataFrame({'artistName':list(map(lambda x:x['artists'][0]['name'], album_tracks)),
                                               'trackName':list(map(lambda x:x['name'], album_tracks)),
                                               'albumName':album['name'],
                                               'trackID':list(map(lambda x:x['id'], album_tracks)),
                                               'artistID':list(map(lambda x:x['artists'][0]['id'], album_tracks)),
                                               'albumID':album['id']})
                        
                        Tracks_results = Tracks_to_search.merge(album_tracks, how='left', on=['artistName','trackName'])
                        Tracks_found = Tracks_results[~Tracks_results.trackID.isna()]
                        
                        if Tracks_found.shape[0]>0:
                            Results = pd.concat([Results, Tracks_found])
                            Tracks_to_search = Tracks_results.loc[Tracks_results.trackID.isna(), ['artistName','trackName']]
                    else:
                        break
        
        Results = Merge_the_results(DF, Results)
        Successful_results, Missing_results = Separate_results(Results)
        
        return Successful_results, Missing_results
            
    Artists_info = Searching_artist_ids(token, pd.unique(DF.artistName))
    Successful_results, Missing_results = Searching_in_artist_dischography(token, DF, Artists_info)
    
    return Successful_results, Missing_results

def Getting_complementary_info(token, DF):    
    def Collecting_info(token, type_of_data, ids):
        import numpy as np
        
        if type_of_data=='tracks' or type_of_data=='artists':
            max_ids = 50
        elif type_of_data=='audio-features':
            max_ids = 100
        else:
            max_ids = 20
        
        rounds_of_calls = int(np.ceil(len(ids)/max_ids))
        df_results = []
        
        for i in range(rounds_of_calls):
            current_ids = ids[i*max_ids:(i+1)*max_ids]
            Results = Utilities.get_several_info(token, type_of_data, current_ids)
            Results = list(filter(lambda x:x is not None, Results))
            
            for result in Results:
                if type_of_data=='tracks':
                    df_results.append({'trackName':result['name'], 
                                       'trackID':result['id'],
                                       'artistName':result['artists'][0]['name'], 
                                       'artistID':result['artists'][0]['id'],
                                       'albumName':result['album']['name'], 
                                       'albumID':result['album']['id'],
                                       'duration':result['duration_ms'],
                                       'explicit':result['explicit']})
                elif type_of_data=='audio-features':
                    df_results.append({'trackID':result['id'],
                                       'acousticness':result['acousticness'],
                                       'danceability':result['danceability'],
                                       'energy':result['energy'],
                                       'instrumentalness':result['instrumentalness'],
                                       'note':result['key'],
                                       'liveness':result['liveness'],
                                       'loudness':result['loudness'],
                                       'mode':result['mode'],
                                       'speechiness':result['speechiness'],
                                       'tempo':result['tempo'],
                                       'time_signature':result['time_signature'],
                                       'valence':result['valence']})
                elif type_of_data=='albums':
                    df_results.append({'albumName':result['name'],
                                       'albumID':result['id'],
                                       'artistName':result['artists'][0]['name'],
                                       'artistID':result['artists'][0]['id'],
                                       'release_date':result['release_date'][:4],
                                       'album_type':result['album_type'],
                                       'label':result['label'],
                                       'total_tracks':result['total_tracks']})
                else:
                    df_results.append({'artistName':result['name'],
                                       'artistID':result['id'],
                                       'genres':result['genres'],
                                       'popularity':result['popularity'],
                                       'followers':result['followers']['total']})
                    
        return pd.DataFrame(df_results)       
    
    track_ids = pd.unique(DF.trackID)
    artist_ids = pd.unique(DF.artistID)
    album_ids = pd.unique(DF.albumID)
    
    tracks = Collecting_info(token, 'tracks', track_ids)
    audio_features = Collecting_info(token, 'audio-features', track_ids)
    albums = Collecting_info(token, 'albums', album_ids)
    artists = Collecting_info(token, 'artists', artist_ids)
    
    return [tracks, audio_features, albums, artists]