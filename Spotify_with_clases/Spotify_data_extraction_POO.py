import pandas as pd
import numpy as np
import json
import time
from datetime import timedelta

from Getting_access_to_SpotifyAPI import get_token
import Spotify_methods_POO as Methods

class StreamingHistory:
    def __init__(self, file, diffHoursUTC):
        self.file = file
        self.diffHoursUTC = diffHoursUTC
    
    def __JSON_to_DF(self):
        with open(self.file, encoding='utf-8') as json_file:
            SH = json.load(json_file)
        return pd.DataFrame(SH)
        
    def get_streaming_history(self):
        SH = self.__JSON_to_DF()
        SH['startTime'] = pd.to_datetime(SH.endTime) + timedelta(hours=self.diffHoursUTC)
        SH['startTime'] = SH.apply(lambda x:x.startTime - timedelta(milliseconds=x.msPlayed), axis=1)        
        return SH[['startTime','artistName','trackName','msPlayed']]

class MethodsApplier:
    def unique_artist_tracks(self, DF):
        uq_artist_tracks = SH.groupby(['artistName', 'trackName']).apply(list).reset_index()
        return uq_artist_tracks[['artistName', 'trackName']]

    def applying_method(self, token, DF, method):
        startTime = time.time()
        Succ_SH, Miss_SH = method(token, DF).structuring_the_results()
        endTime = time.time()
        
        execTime = endTime-startTime
        TracksToFind = DF.shape[0]
        TracksFound = Succ_SH.shape[0]
        exec_info = {
            'exec_time':execTime,
            'number_of_tracks_to_find':TracksToFind,
            'number_of_tracks_found':TracksFound,
            'Accuracy':TracksFound*100/TracksToFind
        }
        return Succ_SH, Miss_SH, exec_info

class ClassifyingDataframe(MethodsApplier):
    def __init__(self, SH, limit):
        self.SH = SH
        self.limit = limit
        self.labels = ['few','many']
        self.UniqueArtistTracks = self.unique_artist_tracks(self.SH)
    
    def __number_of_tracks_by_artist(self):        
        tracksByArtist = self.UniqueArtistTracks.groupby(['artistName']).count().reset_index()        
        return tracksByArtist.rename(columns={"trackName":"tracksNumber"})
    
    def __classify_artist_by_tracks_number(self):
        tracksByArtist = self.__number_of_tracks_by_artist()
        MaxNumberTracks = np.max(tracksByArtist.tracksNumber)
        
        if self.limit<2 and self.limit>MaxNumberTracks:
            raise ValueError('Limit must be greather than 2 and less than {MaxNumberTracks}')
        else:
            pass
        
        bins = [0] + [self.limit] + [np.inf]
        tracksByArtist['Categories'] = pd.cut(tracksByArtist.tracksNumber, bins=bins, labels=self.labels, right=False)
        return tracksByArtist[['artistName','Categories']]
        
    def classify_DF(self):
        tracksByArtist = self.__classify_artist_by_tracks_number()
        UqArtistTracks = self.UniqueArtistTracks.merge(tracksByArtist, how='left', on='artistName')
        
        tracksByCategory = {}
        columns = ['artistName','trackName']
        
        for category in self.labels:
            tracksByCategory[category] = UqArtistTracks.loc[UqArtistTracks['Categories']==category, columns].reset_index(drop=True)
        return tracksByCategory

class ExctractingComplementaryInfo(MethodsApplier):
    def __init__(self, token, DFs):
        self.token = token
        self.DFs = DFs
    
    def concat_the_info(self, df1, df2):
        return pd.concat([df1, df2])
    
    def first_wave(self):
        succ1, miss1, execInfo1 = self.applying_method(self.token, self.DFs['many'], Methods.ArtistTracksMatchFinder)
        succ2, miss2, execInfo2 = self.applying_method(self.token, self.DFs['few'], Methods.FirstMatchFinder)
        
        succInfo = self.concat_the_info(succ1, succ2)
        missInfo = self.concat_the_info(miss1, miss2)
        executionInfo = [execInfo1, execInfo2]
        return succInfo, missInfo, executionInfo
    
    def second_wave(self, missingInfo, DFs):
        notInMany = missingInfo.merge(DFs['many'], how='inner')
        notInFew = missingInfo.merge(DFs['few'], how='inner')
        
        succ1, miss1, execInfo1 = self.applying_method(self.token, notInMany, Methods.FirstMatchFinder)
        succ2, miss2, execInfo2 = self.applying_method(self.token, notInFew, Methods.ArtistTracksMatchFinder)
        
        succInfo = self.concat_the_info(succ1, succ2)
        missInfo = self.concat_the_info(miss1, miss2)
        execInfo = [execInfo1, execInfo2]
        return succInfo, missInfo, execInfo
    
    def third_wave(self, missingInfo):
        succ1, miss1, execInfo1 = self.applying_method(self.token, missingInfo, Methods.MultipleMatchFinder)
        return succ1, miss1, execInfo1
        
file = 'StreamingHistory_music_0.json'
diffHoursUTC = -6
token = get_token()
limit = 5

SH = StreamingHistory(file, diffHoursUTC).get_streaming_history()
DFs = ClassifyingDataframe(SH, limit).classify_DF()

extractingInfo = ExctractingComplementaryInfo(token, DFs)
succInfo1, missInfo1, exeInfo1 = extractingInfo.first_wave()
succInfo2, missInfo2, exeInfo2 = extractingInfo.second_wave(missInfo1, DFs)
succInfo3, missInfo3, exeInfo3 = extractingInfo.third_wave(missInfo2)




