__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
from bs4 import BeautifulSoup
import requests
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

os.getenv('OPENAI_API_KEY')


class Corpus():
    
    def __init__(self, artists):
        self.artists=artists
        self.dir="./vectorStore"
        self.vector_store=self._check_vector_store()
        
    def _check_vector_store(self):
        try:
            vectorstore=Chroma(persist_directory=self.dir, embedding_function=OpenAIEmbeddings())
            
        except:
            top_ten=self.getTopTen()
            lyrics,metas=self.lyricsScraper(top_ten=top_ten)
            RCTS=RecursiveCharacterTextSplitter()
            docs=RCTS.create_documents(lyrics, metadatas=metas)
            vectorstore=Chroma.from_documents(docs, persist_directory=self.dir)

        return vectorstore
    
    def getTopTen(self):
        
        top_tens={}
        for artist in self.artists:
            top_ten=[]
            parent_url=f"https://genius.com/artists/{artist}"
            parent_html=requests.get(parent_url).text
            parent_soup=BeautifulSoup(parent_html, 'html.parser')

            body=parent_soup.body


            for song in body.findAll('div', {'class':'mini_card-title'}):
                song_name=str.lower(song.text)
                cleaned_string = re.sub(r'[^a-zA-Z\s-]', '', song_name)
                top_ten.append(cleaned_string.replace(' ', '-'))
                
            top_tens[artist]=top_ten

        return top_tens

    def lyricsScraper(self, top_ten):
        top_ten_lyrics=[]
        metas=[]

        for artist, songs in top_ten.items():
            for song in songs:
                metadata={}
                url=f"https://genius.com/{artist}-{song}-lyrics"

                # Make a GET request to fetch the raw HTML content
                html_content = requests.get(url).text
                lyric=[]

                # Parse the html content
                soup = BeautifulSoup(html_content, "html.parser")

                first=soup.body.div.main

                if first:
                    after=first.findAll('div', {'class':'SectionScrollSentinel__Container-eoe1bv-0 icvVds'})
                    after_2=after[0].findAll('div', {'id': 'lyrics-root-pin-spacer'})
                    lyrics_container=after_2[0].findAll('div', {'class':"Lyrics__Container-sc-1ynbvzw-1 kUgSbL" ,'data-lyrics-container':"true"})

                    for line in lyrics_container:
                        lyric.append(line.get_text(separator=" ").replace('"', ''))

                    lyric=' '.join(lyric)
                    metadata={'source': url, 'song': song, 'writer': ' '.join([name.capitalize() for name in artist.split('-')])}

                    metas.append(metadata)
                    top_ten_lyrics.append(lyric)
                    print(artist,song)

        return top_ten_lyrics,metas
    

