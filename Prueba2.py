import pandas as pd
import time
from Getting_access_to_SpotifyAPI import get_token
import Spotify_methods as Methods

def Get_StreamingHistory(file, utc_hours_diff):
    from datetime import timedelta
    
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

def Unique_tracks(SH):
    Resultant_DF = SH.groupby(['artistName', 'trackName']).apply(list).reset_index()
    
    return Resultant_DF[['artistName', 'trackName']]

def Applying_functions(token, DF, option):
    start_time = time.time()
    
    if option==1:
        func = Methods.Getting_tracks_info_in_one_result_per_call
    elif option==2:
        func = Methods.Getting_tracks_info_in_multiple_results_per_call
    elif option==3:
        func = Methods.Getting_tracks_in_multiple_artist_tracks
    elif option==4:
        func = Methods.Getting_tracks_info_in_artist_dischography
    else:
        raise ValueError('Invalid option. Choose one between 1 and 4')
    
    Succ_SH, Miss_SH = func(token, DF)
    end_time = time.time()
    
    exec_info = {'exec_time':end_time-start_time,
                 'Number_of_tracks':DF.shape[0],
                 'Tracks_found':Succ_SH.shape[0],
                 'Accuracy':Succ_SH.shape[0]*100/DF.shape[0]}
    
    return Succ_SH, Miss_SH, exec_info

def Extracting_info_first_method(token, DF, lims):
    def Splitting_SH_(DF, lims):
        import numpy as np
        
        if len(lims)!=2:
            raise ValueError('Only 2 values allowed')
        
        Tracks_by_artist = DF.groupby(['artistName']).count().reset_index()
        Tracks_by_artist = Tracks_by_artist.rename(columns={"trackName":"tracksNumber"})
        
        MaxNumTracks_artist = np.max(Tracks_by_artist.tracksNumber)
        
        if lims[0]<2:
            raise ValueError('Min lim must be greather than 2')
        elif lims[1]>MaxNumTracks_artist:
            raise ValueError(f'In this case, max limit must be less than {MaxNumTracks_artist}')
        
        labels = ['Few','Some','Many']
        Tracks_by_artist['Categories'] = pd.cut(Tracks_by_artist.tracksNumber, bins=[0]+lims+[np.inf], labels=labels, right=False)
        
        DF = DF.merge(Tracks_by_artist[['artistName','Categories']], how='left', on='artistName')
        Many_tracks = DF.loc[DF.Categories=='Many', ['artistName','trackName']]
        Some_tracks = DF.loc[DF.Categories=='Some', ['artistName','trackName']]
        Few_tracks = DF.loc[DF.Categories=='Few', ['artistName','trackName']]
        
        return Many_tracks, Some_tracks, Few_tracks
        
    Uq_artist_tracks = Unique_tracks(DF)
    Many_tracks, Some_tracks, Few_tracks = Splitting_SH_(Uq_artist_tracks, lims)
    
    Succ_SH_1, Miss_SH_1, Exec_info_1 = Applying_functions(token, Many_tracks, 4)
    Succ_SH_2, Miss_SH_2, Exec_info_2 = Applying_functions(token, Some_tracks, 3)
    Succ_SH_3, Miss_SH_3, Exec_info_3 = Applying_functions(token, Few_tracks, 1)
    
    Successful_tracks = pd.concat([Succ_SH_1, Succ_SH_2, Succ_SH_3])
    Missing_tracks = pd.concat([Miss_SH_1, Miss_SH_2, Miss_SH_3])
    Exec_info = [Exec_info_1, Exec_info_2, Exec_info_3]
    
    return Successful_tracks, Missing_tracks, Exec_info

def Extracting_info_second_method(token, DF):
    Uq_artist_tracks = Unique_tracks(DF)
    
    Succ_SH_1, Miss_SH_1, Exec_info_1 = Applying_functions(token, Uq_artist_tracks, 1)
    Succ_SH_2, Miss_SH_2, Exec_info_2 = Applying_functions(token, Miss_SH_1, 2)
    Succ_SH_3, Miss_SH_3, Exec_info_3 = Applying_functions(token, Miss_SH_2, 3)
    Succ_SH_4, Miss_SH_4, Exec_info_4 = Applying_functions(token, Miss_SH_3, 4)
        
    Successful_tracks = pd.concat([Succ_SH_1, Succ_SH_2, Succ_SH_3, Succ_SH_4])
    Exec_info = [Exec_info_1, Exec_info_2, Exec_info_3, Exec_info_4]
    
    return Successful_tracks, Miss_SH_4, Exec_info

utc_hours_diff = -6
token = get_token()
SH = Get_StreamingHistory('StreamingHistory_music_0.json', utc_hours_diff)

Successful_tracks1, Missing_tracks1, Exec_info1 = Extracting_info_first_method(token, SH, lims=[2,15])
Successful_tracks2, Missing_tracks2, Exec_info2 = Extracting_info_second_method(token, Missing_tracks1)

Final_successful_tracks = pd.concat([Successful_tracks1, Successful_tracks2])
SH_updated = SH.merge(Final_successful_tracks, how='inner', on=['artistName','trackName'])
SH_updated = SH_updated[['trackName','artistName','albumName','msPlayed',
                         'startTime','trackID','artistID','albumID']]

Info = Methods.Getting_complementary_info(token, SH_updated)