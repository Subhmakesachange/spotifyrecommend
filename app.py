import pickle
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

SPOTIFY_CLIENT_ID = "c60c367b4a5a4f469eb229ed02191e90"
SPOTIFY_CLIENT_SECRET = "55e468370f9042a4a11fc7520d7c5259"

credentials_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
spotify = spotipy.Spotify(client_credentials_manager=credentials_manager)

def fetch_album_cover(track_name, artist_name):
    query = f"track:{track_name} artist:{artist_name}"
    result = spotify.search(q=query, type="track")
    if result and result["tracks"]["items"]:
        track = result["tracks"]["items"][0]
        return track["album"]["images"][0]["url"]
    return "https://i.postimg.cc/0QNxYz4V/social.png"

def fetch_artist_details(artist_name):
    search_result = spotify.search(q=f"artist:{artist_name}", type="artist")
    if search_result and search_result['artists']['items']:
        artist = search_result['artists']['items'][0]
        return {
            'artist_name': artist['name'],
            'genres': artist['genres'],
            'popularity_score': artist['popularity'],
            'follower_count': artist['followers']['total'],
            'artist_image': artist['images'][0]['url'] if artist['images'] else None
        }
    return None

def song_recommendations(selected_track):
    track_index = song_data[song_data['song'] == selected_track].index[0]
    ranked_distances = sorted(list(enumerate(similarity_matrix[track_index])), reverse=True, key=lambda x: x[1])
    suggested_track_names = []
    suggested_album_covers = []
    suggested_artist_details = []

    for i in ranked_distances[1:6]:
        song_artist = song_data.iloc[i[0]].artist
        suggested_album_covers.append(fetch_album_cover(song_data.iloc[i[0]].song, song_artist))
        suggested_track_names.append(song_data.iloc[i[0]].song)
        artist_details = fetch_artist_details(song_artist)
        suggested_artist_details.append(artist_details)

    return suggested_track_names, suggested_album_covers, suggested_artist_details

st.set_page_config(page_title='🎼 Personalized Song Recommender', layout='wide')
st.markdown("""
<style>
    .main {
        background-color: #191414;  
        color: #ffffff;              
    }
    .stButton>button {
        background-color: #1db954; 
        color: white;
    }
    .stButton>button:hover {
        background-color: #1aa34a; 
    }
    .stExpander {
        background-color: #282828;  
        border: 1px solid #444;     
    }
</style>
""", unsafe_allow_html=True)

title_col, logo_col = st.columns([3, 1]) 

with title_col:
    st.title('🎵 Discover Your Next Favorite Track!')
    st.subheader("Explore personalized music recommendations tailored just for you!")



song_data = pickle.load(open('data.pkl', 'rb'))
similarity_matrix = pickle.load(open('reccomend.pkl', 'rb'))

song_options = song_data['song'].values  

selected_track = st.selectbox("Select a song from the list", song_options)

if st.button('Get Recommendations'):
    with st.spinner('Fetching your song recommendations...'):
        track_names, album_covers, artist_details = song_recommendations(selected_track)

    st.markdown("### Recommended Tracks 🎶")
    columns = st.columns(5)
    for col, track_name, cover in zip(columns, track_names, album_covers):
        with col:
            st.image(cover, use_column_width=True)
            st.caption(track_name)

    with st.expander("Learn more about these recommendations", expanded=True):
        for track_name, details in zip(track_names, artist_details):
            if details:
                st.markdown(f"**Track:** {track_name}")
                st.markdown(f"**Artist:** {details['artist_name']}")
                st.markdown(f"**Genres:** {', '.join(details['genres']) if details['genres'] else 'Not Available'}")
                st.markdown(f"**Popularity:** {details['popularity_score']}/100")
                st.markdown(f"**Followers:** {details['follower_count']}")
                if details['artist_image']:
                    st.image(details['artist_image'], width=120)
                st.markdown("---")

st.markdown("---")
st.markdown("Crafted for music enthusiasts by music enthusiasts 🎶")
