import pandas as pd
import numpy as np
import time
import Spotify_utilities as Utilities

class DataHandlerMethods:
    def __init__(self, token, DF):
        self.token = token
        self.DF = DF
        
    def results_to_dictionary(self, results):
        return {
            'artistName':results['artists'][0]['name'],
            'trackName':results['name'],
            'albumName':results['album']['name'],
            'trackID':results['id'],
            'artistID':results['artists'][0]['id'],
            'albumID':results['album']['id']
        }
    
    def __results_to_DF(self, results, areManyResults):
        if areManyResults:
            data = [self.results_to_dictionary(i) for i in results]
        else:
            data = [self.results_to_dictionary(results)]
        return pd.DataFrame(data)

    def searching_the_results(self):
        pass

    def merge_the_results(self, df, results):
        columns = ['artistName','trackName']
        return df.loc[:, columns].merge(results, how='left', on=columns)
    
    def get_null_values(self, results):
        return results.trackID.isna()
    
    def classify_results(self, mergedResults):
        nullResults = self.get_null_values(mergedResults)
        succResults = mergedResults[~nullResults].reset_index(drop=True)
        missResults = mergedResults[nullResults].reset_index(drop=True)
        missResults = missResults[['artistName','trackName']]
        return succResults, missResults
    
    def __define_the_search(self, usedClass, token, item, offset, limit):
        try:
            results = usedClass(self.token, item, offset, limit, clean=False).access_to_results()
        except KeyError:
            results = usedClass(self.token, item, offset, limit, clean=True).access_to_results()
        return results
    
    def making_the_search(self, token, item, offset):
        subclassName = self.__class__.__name__
        classMap = {
            'FirstMatchFinder':(Utilities.GetTracks, 1),
            'MultipleMatchFinder':(Utilities.GetTracks, 50),
            'ArtistTracksMatchFinder':(Utilities.GetSampleArtistTracks, 50),
            'ArtistDischographyMatchFinder':(Utilities.GetArtistID, 50)
        }
        usedClass, limit = classMap[subclassName]
        results = self.__define_the_search(usedClass, self.token, item, offset, limit)
        delay = 1/60
        time.sleep(delay)
        return results

    def get_temp_results(self, callResults):
        if len(callResults)==1:
            tempResults = self.__results_to_DF(callResults[0], areManyResults=False)
        else:
            tempResults = self.__results_to_DF(callResults, areManyResults=True)
        return tempResults
    
    def concat_the_results(self, results, tempResults):
        return pd.concat([results,tempResults])
    
    def select_first_result(self, results):
        return results.groupby(['artistName', 'trackName']).first().reset_index()

class FirstMatchFinder(DataHandlerMethods):
    def __rename_track_artist(self, callResult):
        callResult = callResult[0]
        trackResult = callResult['name'].lower()
        artistResult = callResult['artists'][0]['name'].lower()
        return trackResult, artistResult
    
    def searching_the_results(self):
        results = None
        for i, row in self.DF.iterrows():
            print(f'Searching the track: {row.trackName} ({i+1} of {self.DF.shape[0]})')
            callResult = self.making_the_search(self.token, row.trackName, offset=0)
            
            if callResult:
                trackResult, artistResult = self.__rename_track_artist(callResult)
                targetTrack = row.trackName.lower()
                targetArtist = row.artistName.lower()
                 
                if trackResult!=targetTrack or artistResult!=targetArtist:
                    new_item = targetTrack + " " + targetArtist
                    callResult = self.making_the_search(self.token, new_item, offset=0)
                    if callResult:
                        trackResult, artistResult = self.__rename_track_artist(callResult)
                
                if trackResult==targetTrack and artistResult==targetArtist:
                    print('Track found!')
                    tempResults = self.get_temp_results(callResult)
                    results = self.concat_the_results(results, tempResults)
            else:
                pass
        print('')
        return results
    
    def structuring_the_results(self):
        results = self.searching_the_results()
        results = self.merge_the_results(self.DF, results)
        succResults, missResults = self.classify_results(results)
        return succResults, missResults
    
class MultipleMatchFinder(DataHandlerMethods):
    def __filter_the_results(self, results, trackName, artistName):
        return results[(results.trackName == trackName) & (results.artistName == artistName)]

    def searching_the_results(self):
        results = None
        for i, row in self.DF.iterrows():
            print(f'Searching the track: {row.trackName} ({i+1} of {self.DF.shape[0]})')
            offset = 0
            while True:
                if offset<1000:
                    callResults = self.making_the_search(self.token, row.trackName, offset)
                    
                    if callResults:              
                        tempResults = self.get_temp_results(callResults)
                        tempResults = self.__filter_the_results(tempResults, row.trackName, row.artistName)
                        
                        if tempResults.shape[0]>0:
                            print('Track found!')
                            results = self.concat_the_results(results, tempResults)
                            break
                        else:
                            offset+=50
                    else:
                        break
                else:
                    break
        results = self.select_first_result(results)
        print('')
        return results
    
    def structuring_the_results(self):
        results = self.searching_the_results()
        results = self.merge_the_results(self.DF, results)
        succResults, missResults = self.classify_results(results)
        return succResults, missResults

class ArtistTracksMatchFinder(DataHandlerMethods):
    def searching_the_results(self):
        artists = pd.unique(self.DF.artistName)
        results = None
        cont = 0
        
        for targetArtist in artists:
            tracksToSearch = self.DF[self.DF.artistName==targetArtist]
            print(f'Searching {tracksToSearch.shape[0]} tracks of {targetArtist} (artist number {cont+1} of {len(artists)})')
            cont+=1
            offset = 0
            while offset<1000:
                if tracksToSearch.shape[0]>0:
                    callResults = self.making_the_search(self.token, targetArtist, offset)
                    callResults = list(filter(lambda x:x is not None, callResults))
                    
                    if callResults:                            
                        tempResults = self.get_temp_results(callResults)
                        mergedResults = self.merge_the_results(tracksToSearch, tempResults)
                        nullValues = self.get_null_values(mergedResults)
                        foundTracks = mergedResults[~nullValues]
                        
                        if foundTracks.shape[0]>0:
                            distinctTracks = pd.unique(foundTracks.trackName)
                            print(f'{len(distinctTracks)} tracks found of {tracksToSearch.shape[0]}')
                            results = self.concat_the_results(results, foundTracks)
                            tracksToSearch = mergedResults.loc[nullValues, ['artistName','trackName']]
                        offset+=50
                    else:
                        break
                else:
                    break
        results = self.select_first_result(results)
        print('')
        return results
    
    def structuring_the_results(self):
        results = self.searching_the_results()
        results = self.merge_the_results(self.DF, results)
        succResults, missResults = self.classify_results(results)
        return succResults, missResults
    
class ArtistDischographyMatchFinder(DataHandlerMethods):
    def __searching_artistIDS(self):
        artistIDS = []
        for artist in pd.unique(self.DF.artistName):
            print(f'Searching the artistID of: {artist}')
            offset = 0
            while offset<1000:
                callResults = Utilities.GetArtistID(self.token, artist.lower(), offset, limit=50, clean=True).access_to_results()                
                if len(callResults)>0:
                    artistNames = pd.Series(map(lambda x:x['name'], callResults))
                    artistNames = artistNames[artistNames==artist].index
                  
                    if len(artistNames)>0:
                        print('Artist found!')
                        firstResult = callResults[artistNames[0]]
                        artistIDS.append({'artistName':firstResult['name'],
                                          'artistID':firstResult['id']})
                        break
                    else:
                        offset+=50
                else:
                    break
        return pd.DataFrame(artistIDS)
    
    def results_to_dictionary(self, results, album):
        return {
            'artistName':results['artists'][0]['name'],
            'trackName':results['name'],
            'albumName':album['name'],
            'trackID':results['id'],
            'artistID':results['artists'][0]['id'],
            'albumID':album['id']
        }
    
    def get_temp_results(self, callResults, album):
        if len(callResults)==1:            
            tempResults = [self.results_to_dictionary(callResults[0], album)]            
        else:
            tempResults = [self.results_to_dictionary(i,album) for i in callResults]
        return pd.DataFrame(tempResults)
       
    def searching_the_results(self):     
        artistIDS = self.__searching_artistIDS()
        results = None
                
        for i, row in artistIDS.iterrows():
            artist = row.artistName
            tracksToSearch = self.DF[self.DF.artistName==artist]
            
            offset = 0
            limit = 50
            
            print(f'Searching {tracksToSearch.shape[0]} tracks of {artist}')
            albums = Utilities.GetArtistAlbums(self.token, row.artistID, offset, limit).access_to_results()
            albums = list(filter(lambda x:x['album_group']!='appears_on', albums))
            
            if len(albums)>0:
                for album in albums:
                    print(f"album: {album['name']} ({artist})")
                    if tracksToSearch.shape[0]>0:
                        callResult = Utilities.GetAlbumTracks(self.token, album['id']).access_to_results()
                        tempResults = self.get_temp_results(callResult, album)
                        mergedResults = self.merge_the_results(tracksToSearch, tempResults)
                        nullValues = self.get_null_values(mergedResults)
                        foundTracks = mergedResults[~nullValues]

                        if foundTracks.shape[0]>0:
                            distinctTracks = pd.unique(foundTracks.trackName)
                            print(f'{len(distinctTracks)} tracks found of {tracksToSearch.shape[0]}')
                            results = self.concat_the_results(results, foundTracks)
                            tracksToSearch = mergedResults.loc[nullValues, ['artistName','trackName']]                        
                        offset+=50                   
                    else:
                        break                        
            else:
                continue  
        print('')
        return results
    
    def structuring_the_results(self):
        results = self.searching_the_results()
        results = self.merge_the_results(self.DF, results)
        succResults, missResults = self.classify_results(results)
        return succResults, missResults
    
class ComplementaryInfoExtractor:
    def __init__(self, token, SH, succInfo):
        self.token = token
        self.SH = SH
        self.succInfo = succInfo
        
    def __collecting_info(self, datatype, ids):
        if datatype=='tracks' or datatype=='artists':
            max_ids = 50
        else:
            max_ids = 20
        
        roundsOfCalls = int(np.ceil(len(ids)/max_ids))
        dfResults = []        
        for i in range(roundsOfCalls):
            currentIds = ids[i*max_ids:(i+1)*max_ids]
            results = Utilities.GetComplementaryInfo(self.token, datatype, currentIds).access_to_results()
            results = list(filter(lambda x:x is not None, results))
            
            for result in results:
                if datatype=='tracks':
                    dfResults.append({'trackName':result['name'], 
                                       'trackID':result['id'],
                                       'artistName':result['artists'][0]['name'], 
                                       'artistID':result['artists'][0]['id'],
                                       'albumName':result['album']['name'], 
                                       'albumID':result['album']['id'],
                                       'duration':result['duration_ms'],
                                       'explicit':result['explicit']})
                elif datatype=='albums':
                    dfResults.append({'albumName':result['name'],
                                       'albumID':result['id'],
                                       'artistName':result['artists'][0]['name'],
                                       'artistID':result['artists'][0]['id'],
                                       'release_date':result['release_date'][:4],
                                       'album_type':result['album_type'],
                                       'label':result['label'],
                                       'total_tracks':result['total_tracks']})
                else:
                    dfResults.append({'artistName':result['name'],
                                       'artistID':result['id'],
                                       'genres':result['genres'],
                                       'popularity':result['popularity'],
                                       'followers':result['followers']['total']})
            
        return pd.DataFrame(dfResults)

    def extract_the_data(self, pathFile):
        newSH = self.SH.merge(self.succInfo, how='inner', on=['artistName','trackName'])
        
        print('Getting tracks complementary info')
        tracks = self.__collecting_info('tracks', pd.unique(self.succInfo.trackID))        
        print('Getting albums complementary info')
        albums = self.__collecting_info('albums', pd.unique(self.succInfo.albumID))        
        print('Getting artists complementary info')
        artists = self.__collecting_info('artists', pd.unique(self.succInfo.artistID))        
        artists = artists.explode('genres')
        artists.loc[artists.genres.isna(), 'genres'] = 'unknown'
        
        return {
            'StreamingHistory':newSH,
            'tracks':tracks,
            'albums':albums,
            'artists':artists
        }