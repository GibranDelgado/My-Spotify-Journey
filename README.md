# My Spotify Journey

## Dashboard
See the links below to visualize my dashboard:

- **NovyPro:** https://project.novypro.com/KmFKle  
- **Tableau Public:** https://public.tableau.com/views/Myspotifyjourney/MySpotifyJourney1?:language=es-ES&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link

## Content
The project has two folders

### Used_files
Here, you will find a `.txt` file with the queries used to analyze the data.

### Scripts
This folder includes six Python scripts listed below:

- **Getting_access_to_SpotifyAPI:**  
  This script includes a function `get_token()` to generate a token using a `client_secret` and a `client_id` retrieved from a `.env` file, and a function `get_auth_header()` that generates an `auth_header` based on a given token.

- **Spotify_utilities:**  
  Defines a series of methods to make requests to the Spotify API to retrieve information about tracks, artists, albums, etc.

- **Spotify_methods:**  
  Contains helper methods to get additional information from the tracks in the streaming history, using the classes included in `Spotify_utilities`. These methods are divided into two categories:  
  - Those that search a specific track in a list of results.  
  - Those that try to match the most possible coincidences from a list of tracks.

- **Spotify_data_extraction:**  
  In this script, additional track information is extracted in three stages:

  - **First stage:**  
    Classifies tracks based on how many belong to each artist.  
    If an artist has fewer than five songs, they fall into the `"few"` category; otherwise, into the `"many"` category.  
    The `"ArtistTracksMatchFinder"` method is used for `"many"` category tracks, and `"FirstMatchFinder"` is used for the rest.

  - **Second stage:**  
    Tracks not matched by `"ArtistTracksMatchFinder"` are passed to `"FirstMatchFinder"` and vice versa.

  - **Third stage:**  
    Missing tracks from both methods are merged into a single list, which is then used to search the artist's full discography.

  -- **Complementary information stage:**
    
