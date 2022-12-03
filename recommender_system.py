import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from collections import defaultdict
import numpy as np
import pandas as pd
from collections import defaultdict
from sklearn.metrics import euclidean_distances
from scipy.spatial.distance import cdist
import difflib
from sklearn.pipeline import Pipeline
import pickle
import warnings
warnings.filterwarnings("ignore")
with open('./notebook/model.pkl','rb') as f:
    song_cluster_pipeline=pickle.load(f)
data=pd.read_csv('./notebook/dataset/data.csv')
print(data.columns)
number_cols=data.select_dtypes(np.number)
print(number_cols.columns)



sp= spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id='a435e93552804b0288cd270ca405c9cc',client_secret='f0855466db3045aab0ac7249c4f21cfd'))

#finding songs which are not present in the spotify dataset
def find_song(name,year):
    song_data=defaultdict()
    print("1")
    results=sp.search(q='track:{} year :{}'.format(name,year),limit=1)
    if results['tracks']['items']==[]:
        return None
    
    results=results['tracks']['items'][0]
    track_id=results['id']
    audio_features=sp.audio_features(track_id)[0]
    
    song_data['name']=[name]
    song_data['year']=[year]
    song_data['explicit']=[int(results['explicit'])]
    song_data['duration_ms']=[results['duration_ms']]
    song_data['popularity']=[results['popularity']]
    
    for key,value in audio_features.items():
        song_data[key]=value
      
    song_data_df=pd.DataFrame(song_data)
    
    
    return song_data_df

def get_song_data(song,spotify_df):
    
    try:
        song_data=spotify_df[(spotify_df['name']==song['name']) & (spotify_df['year']==song['year'])].iloc[0]
        return song_data
    except IndexError:
        return find_song(song['name'],song['year'])

#generating vector of song list

def get_mean_vector(song_list,spotify_df):
    song_vectors=[]
    
    for song in song_list:
        song_data=get_song_data(song,spotify_df)
        if song_data is None:
            #rint("Song not found")
            continue
        song_vector=song_data[number_cols.columns].values
        song_vectors.append(song_vector)
     
    song_matrix=np.array(list(song_vectors))
    return np.mean(song_matrix,axis=0)


def flatten_dict_list(dict_list):
    
    flattened_dict=defaultdict()
    for key in dict_list[0].keys():
        flattened_dict[key]=[]
     
    for dictionary in dict_list:
        for key, value in dictionary.items():
            flattened_dict[key].append(value)
            
    return flattened_dict
                           
     #function that takes input from user and displays the recommend songs

def recommender(song_list):
    
    rec_song_list_column = ['name','year','artists']
    song_dict=flatten_dict_list(song_list)
    #print(song_dict)
    
    song_center=get_mean_vector(song_list,data)
    # print(song_center)
    scaler=song_cluster_pipeline.steps[0][1]
    scaled_data=scaler.transform(data[number_cols.columns])
    scaled_song_center=scaler.transform(song_center.reshape(1,-1))
    #print(scaled_song_center)
    distance=cdist(scaled_song_center,scaled_data,'cosine')
    index=list(np.argsort(distance)[:,:10][0]) #top 10 closest nodes in the cluster
    
    rec_songs=data.iloc[index]
    rec_songs=rec_songs[~rec_songs['name'].isin(song_dict['name'])]
    return rec_songs[rec_song_list_column].to_dict(orient='records')                      

# if __name__ =='__main__':
#     print(recommender([#{'name': 'Come As You Are', 'year':1991},
#                 #{'name': 'Smells Like Teen Spirit', 'year': 1991},
#                 #{'name': 'Lithium', 'year': 1992},
#                 #{'name': 'All Apologies', 'year': 1993},
#                 {'name': 'Story of My Life', 'year': 2013}]))