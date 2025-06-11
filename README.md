# My Spotify Journey
Thank you for your interest in my project. This time I decided to emulate the famous annual Spotify Wrapped, with additional information layers to make an in-depth analysis of my streaming history and create a customized dashboard of my musical preferences, with the advantage of using data from anytime of the year.

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
  Contains methods used to retrieve complementary information about the tracks that make up the streaming history, using the classes provided by the "Spotify_utilities" script. These methods are divided in two categories:  
  - Those who search a specific track in a list of results.  
  - Those that try to match as many tracks as posible from a list of results.

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

  - **Complementary information stage:**  
    In this stage, additional information about artists and albums was extracted using the IDs of the tracks obtained in the three previous stages.
- **Getting_specific_query:**  
  This script includes a method `number_of_queries()` that returns the number of queries from the `queries.txt` file, and a method `specific_query()`that returns a query based on a query number, passed as a parameter.

- **Database_tables_and_queries_creation:**  
  This script contains the methods to emulate a traditional relational database using SQLite.  
  - First of all, the `createDB()` function creates a database based on the name given as a parameter.
  - There is a private method `insert_df_as_table()` that reads a dataframe passed as a parameter and reinterprets each datatype of the dataframe as its equivalent in SQLite. Then it creates the table and inserts the dataframe's information into it.  
  - The `create_all_tables()` method applies the private method `insert_df_as_table()` to every Excel file included in a specified folder path.  
  - Once the tables have been generated and filled, it's time to generate the view files. These are created reading every query included in the `queries.txt` file, then being executed in the database and then the results are saved as an Excel file.

## Get your own spotify data
  - In the `"references"` section you will find a link to request your streaming history data. You will be able to download your data within five days. Once you have downloaded your data, you will get a `"my_spotify_data"` zip file. The only file you will need from there is the `"StreamingHistory_music_0"` json file. Copy it and place it in the `"Used_files"` folder.
  - In order to use the Spotify Web API, you will have to create an account on Spotify to developers. 
      - In the `"references"` section you will find a link where you can log in with your spotify account.
      - If you click in your username, a drop-down list will appear. Just click on `"dashboard"` and then create an app.
      - At the moment of creating your app, in the `"Which API/SDKs are you planning to use?"` section, only select the `"Web API"` option. The rest of them will not be necessary.
      - I recommend you fill the `"Redirect URIs"` section like this: `"http://127.0.0.1:8000/callback"`.
  - Once you have created your app, go to `"settings"`, copy the "Client ID" and "Client secret" and then put them into a `".env"` file like this:
      - client_id=(here will be your client id)
      - client_secret=(here will be your client secret)
  - Then copy this file and place it in the "Used files" folder.

## About the use
  - Execute the "Main_python.py" script. This is going to create a new `"Spotify_results"` folder, with the additional information about the tracks, albums and artists of your streaming history.  
  `In the Main_python script there's a variable called "diffHoursUTC". This represents the hour difference from the UTC.`  
  `If you want to use the UTC timezone, set this value to 0; otherwise, set this value according to the location of your preference.`

  - Execute the "Main_sqlite.py" script. This is going to create a new "Queries_results" folder, with the necessary views to create your customized Spotify wrapped dashboard.  
  `If you want to add or modify a query, don't forget to keep the numering format followed in the document.`

## Libraries
These libraries were used. If you are working in the anaconda environment, you will not need the first three.
```
pip install pandas
pip install numpy
pip install requests
pip install python-dotenv
```

## References
  - **Request your data:** https://www.spotify.com/us/account/privacy/
  - **Spotify for developers:** https://developer.spotify.com/
