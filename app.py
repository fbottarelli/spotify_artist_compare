import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import matplotlib.pyplot as plt
import os


# Carica le credenziali di Spotify
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
auth_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

def get_artist_info(artist_name):
    artist = sp.search(q=artist_name, type='artist')['artists']['items'][0]
    return {
        'name': artist['name'],
        'id': artist['id'],
        'followers': artist['followers']['total'],
        'popularity': artist['popularity'],
        'genres': artist['genres'],
        'image': artist['images'][0]['url'] if artist['images'] else None
    }

def get_top_tracks(artist_id):
    results = sp.artist_top_tracks(artist_id)
    tracks = results['tracks'][:10]  # Limit to top 10 tracks
    return [{
        'name': track['name'],
        'album': track['album']['name'],
        'artist': track['artists'][0]['name'],
        'release_date': track['album']['release_date'],
        'popularity': track['popularity'],
        'album_cover': track['album']['images'][0]['url'] if track['album']['images'] else None,
        'danceability': sp.audio_features(track['id'])[0]['danceability'] if sp.audio_features(track['id']) else 0,
        'loudness': sp.audio_features(track['id'])[0]['loudness'] if sp.audio_features(track['id']) else 0,
        'energy': sp.audio_features(track['id'])[0]['energy'] if sp.audio_features(track['id']) else 0,
        'valence': sp.audio_features(track['id'])[0]['valence'] if sp.audio_features(track['id']) else 0,
        'tempo': sp.audio_features(track['id'])[0]['tempo'] if sp.audio_features(track['id']) else 0,
        'artist_id': artist_id
    } for track in tracks]

def plot_features_comparison(data_tracks, artist1_info, artist2_info):
    df = pd.DataFrame(data_tracks)
    fig, ax = plt.subplots()
    colors = {artist1_info['id']: 'blue', artist2_info['id']: 'red'}

    for artist_id, group in df.groupby('artist_id'):
        ax.scatter(group['danceability'], group['loudness'], alpha=0.7, label=group['artist'].iloc[0], c=colors[artist_id])
    
    plt.title('Confronto Danceability vs. Loudness')
    plt.xlabel('Danceability')
    plt.ylabel('Loudness (dB)')
    plt.legend(title='Artist')
    st.pyplot(fig)

def plot_audio_features_boxplot(data_tracks, artist1_name, artist2_name):
    df = pd.DataFrame(data_tracks)
    fig, axs = plt.subplots(1, 4, figsize=(20, 5))  # 1 riga, 4 colonne per 4 features
    features = ['danceability', 'energy', 'valence', 'tempo']
    for i, feature in enumerate(features):
        ax = axs[i]
        artist1_data = df[df['artist'] == artist1_name][feature]
        artist2_data = df[df['artist'] == artist2_name][feature]
        ax.boxplot([artist1_data, artist2_data], labels=[artist1_name, artist2_name])
        ax.set_title(f'Distribution of {feature}')
        ax.set_ylabel(feature)

    plt.tight_layout()
    st.pyplot(fig)

def plot_audio_features_violinplot(data_tracks, artist1_name, artist2_name):
    df = pd.DataFrame(data_tracks)
    fig, axs = plt.subplots(1, 4, figsize=(20, 5))  # 1 riga, 4 colonne per 4 features
    features = ['danceability', 'energy', 'valence', 'tempo']
    for i, feature in enumerate(features):
        ax = axs[i]
        data_to_plot = [df[df['artist'] == artist1_name][feature], df[df['artist'] == artist2_name][feature]]
        ax.violinplot(data_to_plot)
        ax.set_xticks([1, 2])
        ax.set_xticklabels([artist1_name, artist2_name])
        ax.set_title(f'Distribution of {feature}')
        ax.set_ylabel(feature)

    plt.tight_layout()
    st.pyplot(fig)

def show_average_features(data_tracks):
    df = pd.DataFrame(data_tracks)
    numeric_columns = ['loudness', 'danceability', 'energy', 'valence', 'tempo', 'artist']
    df = df[numeric_columns]
    average_features = df.groupby('artist').mean()[['loudness', 'danceability', 'energy', 'valence', 'tempo']]
    st.write("Media delle Caratteristiche Audio per Artista:")
    st.dataframe(average_features)

def main():
    st.title("Confronto Artisti su Spotify")

    artist1_name = st.text_input("Inserisci il nome del primo artista")
    artist2_name = st.text_input("Inserisci il nome del secondo artista")

    if st.button("Confronta"):
        if artist1_name and artist2_name:
            artist1_info = get_artist_info(artist1_name)
            artist2_info = get_artist_info(artist2_name)
            artist1_tracks = get_top_tracks(artist1_info['id'])
            artist2_tracks = get_top_tracks(artist2_info['id'])
            data_tracks = artist1_tracks + artist2_tracks

            col1, col2 = st.columns(2)
            with col1:
                st.image(artist1_info['image'], caption=artist1_info['name'])
                st.markdown(f"**Nome:** {artist1_info['name']}")
                st.markdown(f"**Follower:** {artist1_info['followers']:,}")
                st.markdown(f"**Popolarità:** {artist1_info['popularity']}")
                st.markdown(f"**Generi:** {', '.join(artist1_info['genres'])}")
            with col2:
                st.image(artist2_info['image'], caption=artist2_info['name'])
                st.markdown(f"**Nome:** {artist1_info['name']}")
                st.markdown(f"**Follower:** {artist2_info['followers']:,}")
                st.markdown(f"**Popolarità:** {artist2_info['popularity']}")
                st.markdown(f"**Generi:** {', '.join(artist2_info['genres'])}")
            show_average_features(data_tracks)
            plot_features_comparison(data_tracks, artist1_info, artist2_info)
            plot_audio_features_boxplot(data_tracks, artist1_info['name'], artist1_info['name'])
            plot_audio_features_violinplot(data_tracks, artist1_info['name'], artist1_info['name'])
            
        else:
            st.error("Per favore inserisci i nomi di entrambi gli artisti.")

if __name__ == "__main__":
    main()
