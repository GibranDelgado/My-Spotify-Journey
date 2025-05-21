import pandas as pd
from datetime import timedelta
import time
import math
import Spotify_utilities as Utilities

def Get_StreamingHistory(file, utc_hours_diff):
    def JSON_to_DF(file):
        import json
        with open(file, encoding='utf-8') as json_file:
            SH = json.load(json_file)

        return pd.DataFrame(SH)
    
    SH = JSON_to_DF(file)
    SH['startTime'] = pd.to_datetime(SH.endTime) + timedelta(hours=utc_hours_diff)
    SH['startTime'] = SH.apply(lambda x:x['startTime']-timedelta(milliseconds=x['msPlayed']), axis=1)
    SH = SH.drop(['endTime'], axis=1)
    
    return SH.loc[:,['startTime','artistName','trackName','msPlayed']]
        
def Collecting_StreamingHistory_details(token, streaming_history):
    def Searching_artist_ids(token, artists):
        print('***** Searching for artists *****')
        list_of_artists = []
        for i in artists:
            print(f'\nArtist to search: {i}')
            Result = Utilities.search_for_artist(token, i, 1, True)
            if len(Result)!=0:
                print(f'Artist found: {Result[0]["name"]}')
                if Result[0]["name"]==i:
                    list_of_artists.append({'artistName':Result[0]["name"], 'artistID':Result[0]["id"]})
                else:
                    Result = Utilities.search_for_artist(token, f'"{i}"', 1, False)
                    print(f'Artist found: {Result[0]["name"]}')
                    if Result[0]["name"]==i:
                        list_of_artists.append({'artistName':Result[0]["name"], 'artistID':Result[0]["id"]})
                    else:
                        Result = Utilities.get_all_results_artist(token, f'"{i}"')
                        for j in Result:
                            print(f'Artist found: {j["name"]}')
                            if j["name"]==i:
                                list_of_artists.append({'artistName':j["name"], 'artistID':j["id"]})
                                break
                        if j["name"]!=i:
                            list_of_artists.append('N/E')
            else:
                list_of_artists.append('N/E')
        
        list_of_artists = pd.DataFrame(list(filter(lambda results: results!='N/E', list_of_artists)))
        
        return list_of_artists
    
    def Searching_missing_artists(SH, artists, artists_found):
        Artists_not_found = pd.DataFrame(artists, columns=['artistName']).merge(artists_found, how='left', on='artistName')
        Artists_not_found = Artists_not_found.artistName[Artists_not_found.artistID.isna()]
        
        missing_artists_songs = SH.merge(pd.DataFrame(Artists_not_found, columns=['artistName']), how='inner', on='artistName')
        missing_artists_list = []

        for i in Artists_not_found:
            df = missing_artists_songs[missing_artists_songs.artistName==i]
            for j in pd.unique(df.trackName):
                Result = Utilities.search_for_song(token,f'{i} {j}', 1, False)[0]["artists"][0]
                if Result["name"]==i:
                    missing_artists_list.append({'artistName':Result["name"], 'artistID':Result["id"]})
                    break

        return pd.DataFrame(missing_artists_list)
    
    def Grouping_artists_and_songs(sh, full_artists_ids):
        Unique_artists_songs = sh.groupby(['artistName','trackName']).apply(list).reset_index()
        Unique_artists_songs = Unique_artists_songs[['artistName','trackName']]
        Unique_artists_songs = Unique_artists_songs.merge(full_artists_ids, how='left', on='artistName')
        Unique_artists_songs = Unique_artists_songs[~Unique_artists_songs['artistID'].isna()]
        
        return Unique_artists_songs

    def Getting_songs_info(token, unique_artists_songs):
        print('\n***** Searching for songs *****')
        Songs_info = []
        delay = 1/30
        
        for _,row in unique_artists_songs.iterrows():
            trackName, trackID, albumName, albumID = [], [], [], []
            clean = False
            
            try:
                Result = Utilities.search_for_song(token, row.trackName, 1, clean)
                time.sleep(delay)
            except:
                clean = True
                Result = Utilities.search_for_song(token, row.trackName, 1, clean)
                time.sleep(delay)
            if len(Result)==0:
                clean = True
                Result = Utilities.search_for_song(token, row.trackName, 1, clean)
                time.sleep(delay)
            print(f'Searching the song: {row.trackName}')
            if (Result[0]['name'].lower()==row.trackName.lower()) and Result[0]['artists'][0]['name']==row.artistName:
                trackName.append(Result[0]['name'])
                trackID.append(Result[0]['id'])
                albumName.append(Result[0]['album']['name'])
                albumID.append(Result[0]['album']['id'])
            else:
                Result = Utilities.search_for_song(token, row.trackName+" "+row.artistName, 1, clean)
                print(f'Searching the song: {row.trackName} {row.artistName}')
                time.sleep(delay)
                if (Result[0]['name'].lower()==row.trackName.lower()) and Result[0]['artists'][0]['name']==row.artistName:
                    trackName.append(Result[0]['name'])
                    trackID.append(Result[0]['id'])
                    albumName.append(Result[0]['album']['name'])
                    albumID.append(Result[0]['album']['id'])
                else:
                    Result = Utilities.search_for_song(token, "\""+row.trackName+"\"", 1, clean)
                    print(f'Searching the song: "\"{row.trackName}"\"')
                    time.sleep(delay)
                    if (Result[0]['name'].lower()==row.trackName.lower()) and Result[0]['artists'][0]['name']==row.artistName:
                        trackName.append(Result[0]['name'])
                        trackID.append(Result[0]['id'])
                        albumName.append(Result[0]['album']['name'])
                        albumID.append(Result[0]['album']['id'])
                    else:
                        Result = Utilities.get_all_results_songs(token, row.trackName+" "+row.artistName)
                        print(f'Searching the song: {row.trackName} {row.artistName}')
                        time.sleep(delay)
                        for i in Result:
                            if (i['name'].lower()==row.trackName.lower()) and i['artists'][0]['name']==row.artistName:
                                trackName.append(i['name'])
                                trackID.append(i['id'])
                                albumName.append(i['album']['name'])
                                albumID.append(i['album']['id'])
                                break
                        if i['name']!=row.trackName or i['artists'][0]['name']!=row.artistName:
                            trackName.append('N/E')
                            trackID.append('N/E')
                            albumName.append('N/E')
                            albumID.append('N/E')
            Songs_info.append({'artistName':row.artistName, 'artistID':row.artistID, 
                               'trackName':row.trackName, 'trackID':trackID, 
                               'albumName':albumName, 'albumID':albumID})
               
        return pd.DataFrame(Songs_info)    

    artists = list(pd.unique(streaming_history.artistName))
    artist_ids = Searching_artist_ids(token, artists)
    artists_ids_2 = Searching_missing_artists(streaming_history, artists, artist_ids)
    full_artists_ids = pd.concat([artist_ids, artists_ids_2], axis=0)
    unique_artists_songs = Grouping_artists_and_songs(streaming_history, full_artists_ids)
    Songs_info = Getting_songs_info(token, unique_artists_songs)

    return Songs_info

def Collecting_StreamingHistory_details_2(token, streaming_history, Songs_info):
    def Filtering_StreamingHistory(streaming_history, Songs_info):
        Songs_info_segmented = Songs_info.iloc[:,2:]

        for i in range(Songs_info_segmented.shape[1]):
            Songs_info_segmented.iloc[:,i] = list(map(lambda x:''.join(x), Songs_info_segmented.iloc[:,i]))
        Songs_info.iloc[:,2:] = Songs_info_segmented
        
        Missing_songs = Songs_info[Songs_info.trackID=='N/E'].reset_index(drop=True)
        Songs_info = Songs_info[Songs_info!='N/E']
        #Removing duplicates
        Songs_info = Songs_info.groupby(['artistName','artistID','trackName','trackID','albumName','albumID']).apply(list).reset_index()
        Songs_info = Songs_info[['artistName','artistID','trackName','trackID','albumName','albumID']]    
        
        SH_complemented = streaming_history.merge(Songs_info, how='left', on=['artistName','trackName'])
        SH_songs_not_found = SH_complemented[SH_complemented.trackID.isna()].reset_index(drop=True)
        SH_complemented = SH_complemented[~SH_complemented.trackID.isna()]
         
        return Missing_songs, SH_complemented, SH_songs_not_found
    
    def Identifying_songs_belong_top_tracks(Missing_songs):
        print('\n***** Songs that are in the most popular tracks from artist *****')
        Missing_songs_found = None

        for i in pd.unique(Missing_songs.artistName):
            Artist_missing_songs = Missing_songs.loc[Missing_songs.artistName==i, ['artistName','artistID','trackName']].reset_index(drop=True)
            uq_artist_id = Artist_missing_songs.loc[0,'artistID']
            
            top_tracks = Utilities.get_top_tracks_from_artist(token, uq_artist_id, market='MX')
            
            names = list(map(lambda x:x['name'], top_tracks))    
            track_ids = list(map(lambda x:x['id'], top_tracks)) 
            album_names = list(map(lambda x:x['album']['name'], top_tracks))
            album_ids = list(map(lambda x:x['album']['id'], top_tracks)) 
            print(f'\n{i} top tracks: {names}')
            
            top_tracks_df = pd.DataFrame({'trackName':names, 'trackID':track_ids, 'albumName':album_names, 'albumID':album_ids})
            result = Artist_missing_songs.merge(top_tracks_df, how='inner', on='trackName')
            Missing_songs_found = pd.concat([Missing_songs_found, result])
            print(f'{i} top tracks found: {list(result.trackName)}')
        
        return Missing_songs_found.reset_index(drop=True)
    
    def Get_all_albums_from_artists(token, Songs_to_search):
        artists_albums = []
        delay = 1/30
        for _,row in Songs_to_search.iterrows():
            albumNames, albumIDs, albumGroups = [], [], []
            
            albums = Utilities.get_albums_from_artist(token, row.artistID)
            albums = list(filter(lambda x:x['album_group']!='appears_on', albums))
            albums = list(filter(lambda x:x['artists'][0]['name']==row.artistName, albums))
            
            if len(albums)!=0:
                for i in albums:
                    albumNames.append(i['name']), 
                    albumIDs.append(i['id'])
                    albumGroups.append(i['album_group'])
            else:
                albumNames.append('N/E')
                albumIDs.append('N/E')
                albumGroups.append('N/E')
            
            artists_albums.append({'artistName':row.artistName,
                                   'albumNames':albumNames,
                                   'albumIDs':albumIDs,
                                   'albumGroups':albumGroups})
            time.sleep(delay)
        
        artists_albums = pd.DataFrame(artists_albums)
        artists_albums = artists_albums[list(map(lambda x:'N/E' not in x, artists_albums.albumIDs))]
        artists_albums = artists_albums.explode(['albumNames','albumIDs','albumGroups']).reset_index(drop=True)
        
        return artists_albums
    
    def Get_tracks_from_albums(token, Still_missing_songs, Artists_discography):
        print('\n***** Searching missing songs in each artist album *****')
        for i in pd.unique(Artists_discography.artistName):
            print(f'\nArtist: {i}')
            Artist_dischography = Artists_discography[Artists_discography.artistName == i]
            Artist_missing_songs = Still_missing_songs[Still_missing_songs.artistName == i]
            print(f'Searching {Artist_missing_songs.shape[0]} songs\n')
            for _,row in Artist_dischography.iterrows():
                if Artist_missing_songs.shape[0]!=0:
                    print(f'Album: {row.albumNames}')
                    Album_songs = Utilities.get_album_tracks(token, row.albumIDs)
                    for ind, j in Artist_missing_songs.iterrows():
                        print(f'Searching the song this song: {j.trackName}\n')
                        for k in Album_songs:
                            if j.trackName==k['name']:
                                Still_missing_songs.loc[ind,'trackID'] = k['id']
                                Still_missing_songs.loc[ind,'albumName'] = row.albumNames
                                Still_missing_songs.loc[ind,'albumID'] = row.albumIDs
                                Artist_missing_songs.drop([ind], axis=0, inplace=True)
                                print(f'Got it, {Artist_missing_songs.shape[0]} songs left\n')
                else:
                    break

        Still_missing_songs = Still_missing_songs[~Still_missing_songs.trackID.isna()]    

        return Still_missing_songs.reset_index(drop=True)
    
    def Searching_missing_songs_in_artist_dischography(token, Missing_songs, Missing_songs_found):
        Still_missing_songs = Missing_songs.iloc[:,:3].merge(Missing_songs_found.iloc[:,1:], how='left', on=['artistID','trackName'])
        Still_missing_songs = Still_missing_songs[Still_missing_songs.trackID.isna()]
        
        Artists_discography = Get_all_albums_from_artists(token, Missing_songs)
        Missing_songs_found_2 = Get_tracks_from_albums(token, Still_missing_songs, Artists_discography)

        return Missing_songs_found_2

    
    Missing_songs, SH_complemented, SH_songs_not_found = Filtering_StreamingHistory(streaming_history, Songs_info)
    Missing_songs_found = Identifying_songs_belong_top_tracks(Missing_songs)
    Missing_songs_found_2 = Searching_missing_songs_in_artist_dischography(token, Missing_songs, Missing_songs_found)
    
    Total_missing_songs_found = pd.concat([Missing_songs_found, Missing_songs_found_2], axis=0).reset_index(drop=True)
    
    SH_songs_not_found = SH_songs_not_found.iloc[:,:4].merge(Total_missing_songs_found, how='left', on=['artistName','trackName'])
    SH_songs_already_found = SH_songs_not_found[~SH_songs_not_found.trackID.isna()]
    
    return pd.concat([SH_complemented,SH_songs_already_found], axis=0).sort_values(by='startTime', ascending=True)

def Get_sources_songs(token, SH_complementary_info):
    artists_ids = pd.unique(SH_complementary_info.artistID)
    tracks_ids = pd.unique(SH_complementary_info.trackID)
    albums_ids = pd.unique(SH_complementary_info.albumID)
    
    def collecting_info(token, data_type, ids):
        df_results = []
        if (data_type=='tracks' or data_type=='artists'):
            lim_per_call = 50 
        elif (data_type=='audio-features'):
            lim_per_call = 100
        else:
            lim_per_call = 20
        
        for i in range(math.ceil(len(ids)/lim_per_call)):
            call_result = Utilities.get_several_info(token, data_type, ids[i*lim_per_call:(i+1)*lim_per_call])
            call_result = list(filter(lambda x:x is not None, call_result))
            for j in call_result:
                if (data_type=='tracks'):                    
                    df_results.append({'trackName':j['name'],'trackID':j['id'],'artistName':j['artists'][0]['name'],
                                      'artistID':j['artists'][0]['id'],'albumName':j['album']['name'],
                                      'albumID':j['album']['id'],'duration':j['duration_ms'],'explicit':j['explicit']})
                elif (data_type=='audio-features'):
                    df_results.append({'trackID':j['id'],'acousticness':j['acousticness'],'danceability':j['danceability'],
                                       'energy':j['energy'],'instrumentalness':j['instrumentalness'],'note':j['key'],
                                       'liveness':j['liveness'],'loudness':j['loudness'],'mode':j['mode'],'speechiness':j['speechiness'],
                                       'tempo':j['tempo'],'time_signature':j['time_signature'],'valence':j['valence']})
                elif(data_type=='albums'):
                    df_results.append({'albumName':j['name'],'albumID':j['id'],'artistName':j['artists'][0]['name'],
                                       'artistID':j['artists'][0]['id'], 'release_date':j['release_date'][:4],'album_type':j['album_type'],
                                       'label':j['label'],'total_tracks':j['total_tracks']})
                else:
                    df_results.append({'artistName':j['name'],'artistID':j['id'],'genres':j['genres'],
                                       'popularity':j['popularity'],'followers':j['followers']['total']})
        
        return pd.DataFrame(df_results)
    
    tracks = collecting_info(token, 'tracks', tracks_ids)
    audio_features = collecting_info(token, 'audio-features', tracks_ids)
    albums = collecting_info(token, 'albums', albums_ids)
    artists = collecting_info(token, 'artists', artists_ids)
    
    artists = [{'artistName': row.artistName,
                'artistID': row.artistID,
                'genre': genre if len(row.genres) > 0 else 'unknown',
                'popularity': row.popularity,
                'followers': row.followers}
              for _, row in artists.iterrows()
              for genre in (row.genres if len(row.genres) > 0 else [''])]

    artists = pd.DataFrame(artists)
        
    return [tracks, audio_features, albums, artists]

def Generate_files(path_file, SH_complementary_info, SH_dataframes_generated):
    SH_complementary_info.to_excel(f'{path_file}StreamingHistory.xlsx', index=False)
    names = ['tracks','audio_features','albums','artists']
    for i in range(len(SH_dataframes_generated)):
        SH_dataframes_generated[i].to_excel(f'{path_file}{names[i]}.xlsx', index=False)
    
def Printing_metrics(SH, SH_complementary_info):
    print(f'\nNumber of plays to search: {SH.shape[0]}')
    print(f'Number of plays found: {SH_complementary_info.shape[0]}')
    print(f'Model percentage accuracy: {round(SH_complementary_info.shape[0]*100/SH.shape[0],2)}%')