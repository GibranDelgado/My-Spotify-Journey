import sys
import os
import pandas as pd

def printing_metrics(succInfo, missInfo, exeInfo):
    tracksFound = succInfo.shape[0]
    missingTracks = missInfo.shape[0]
    totalTracks = tracksFound + missingTracks
    
    print(f'Total tracks to search: {totalTracks}')
    print(f'Number of tracks found: {tracksFound}')
    print(f'Model performance: {round(tracksFound*100/totalTracks,2)}%')
    
if __name__ ==  '__main__':
    path = os.path.dirname(os.path.abspath('Main_python.py'))+'\\'
    sys.path.insert(0, os.path.join(os.path.dirname(sys.path[0]), f"{path}Scripts"))
    
    from Getting_access_to_SpotifyAPI import get_token
    import Spotify_data_extraction as SDE
    
    output_path = f'{path}Spotify_results\\'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    input_path = f'{path}Used_files\\'
    diffHoursUTC = -6
    file = f'{input_path}StreamingHistory_music_0.json'
    token = get_token(input_path)
    
    SH = SDE.StreamingHistory(file, diffHoursUTC).get_streaming_history()
    DFs = SDE.ClassifyingDataframe(SH, limit=5).classify_DF()
    
    extractingInfo = SDE.ExtractingTheData(token, DFs)    
    succInfo1, missInfo1, execInfo1 = extractingInfo.first_wave()
    succInfo2, missInfo2, execInfo2 = extractingInfo.second_wave(missInfo1, DFs)
    succInfo3, missInfo3, execInfo3 = extractingInfo.third_wave(missInfo2)
    
    succInfo = pd.concat([succInfo1, succInfo2, succInfo3])
    exeInfo = [execInfo1, execInfo3, execInfo3]
    
    SDE.GeneratingFiles().dfs_to_excels(token, succInfo, SH, output_path)    
    printing_metrics(succInfo, missInfo3, exeInfo)