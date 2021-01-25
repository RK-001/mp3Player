'''
MP3Player using tkinter and pygame

Auther : RK-001
created On : 20/1/2021


'''

from tkinter import *
from tkinter import filedialog  # to choose song from file
import pygame  # for song play, pause and other operation
import time
import tkinter.ttk as ttk  # for slider
import sqlite3  # to create playlist usin DB
import os   # required while seprating song title from complete path
from tinytag import TinyTag  # used in calculation of song lenghth


class musicPlayer:
    # Defining Constructor
    def __init__(self, root):
        # create plalist database and table in sqlite
        try:
            self.con = sqlite3.connect('playList.db')
            self.cur = self.con.cursor()
            self.cur.execute(
                '''create table if not exists playlist(path text,songTitle text)''')
        except Error as e:
            print(e)
        # some member variables
        self.paused = False
        self.stopped = False
        self.root = root

        pygame.mixer.init()   # Initialize Pygame

        self.root.title("MP3 Player")  # set window title
        self.root.geometry('600x500')  # set width and height for window

        # Create main Frame
        main_frame = Frame(self.root)
        main_frame.pack(pady=20)

        # create playlist box to hold plalist
        self.playlistBox = Listbox(main_frame, bg="black", fg="yellow",
                                   width=60, height=15, selectbackground="red", selectforeground="white")
        self.playlistBox.grid(pady=20)  # verticle paddind
        self.playlistBox.insert(
            END, "First load the playlist")
        # Create Button Frame for button controls
        control_frame = Frame(main_frame)
        control_frame.grid(pady=20)
        # Define Button Images For Controls
        backBtnImg = PhotoImage(file='images/back50.png')

        # create  button objects
        backBtn = Button(control_frame, text="prev", borderwidth=1, width=6, height=1, font=(
            "times new roman", 16, "bold"), fg="navyblue", bg="gold", command=self.playPrev)
        forwardButton = Button(control_frame, text="next", borderwidth=1, width=6, height=1, font=(
            "times new roman", 16, "bold"), fg="navyblue", bg="gold", command=self.playNext)
        playButton = Button(control_frame, text="play", borderwidth=1, width=6, height=1, font=(
            "times new roman", 16, "bold"), fg="navyblue", bg="gold", command=self.playSong)
        self.pauseButton = Button(control_frame, text="pause", borderwidth=1, width=6, height=1, font=(
            "times new roman", 16, "bold"), fg="navyblue", bg="gold", command=lambda: self.pause(self.paused))
        stopButton = Button(control_frame, text="stop", borderwidth=1, width=6, height=1, font=(
            "times new roman", 16, "bold"), fg="navyblue", bg="gold", command=self.stop)
        # put buttons in frame
        backBtn.grid(row=0, column=0, padx=10)
        forwardButton.grid(row=0, column=1, padx=10)
        playButton.grid(row=0, column=2, padx=10)
        self.pauseButton.grid(row=0, column=3, padx=10)
        stopButton.grid(row=0, column=4, padx=10)

        # Create Main Menu
        my_menu = Menu(self.root)
        root.config(menu=my_menu)

        # Create Add Song Menu Dropdows
        add_song_menu = Menu(my_menu, tearoff=0)
        my_menu.add_cascade(label="Add Songs", menu=add_song_menu)
        # Add One Song To Playlist
        add_song_menu.add_command(
            label="Add current Playlist to player", command=self.loadPlaylist)
        # Add Many Songs to Playlist
        add_song_menu.add_command(
            label="Add Songs To Playlist", command=self.addToPlaylist)

        # Create Delete Song Menu Dropdowns
        remove_song_menu = Menu(my_menu, tearoff=0)
        my_menu.add_cascade(label="Remove Songs", menu=remove_song_menu)
        remove_song_menu.add_command(
            label="Delete A Song From Playlist", command=self.deleteAsong)
        remove_song_menu.add_command(
            label="Delete All Songs From Playlist", command=self.deleteAllsongs)

        # Create Status Bar
        self.status_bar = Label(main_frame, text='', bd=1,
                                relief=GROOVE, anchor=E)
        self.status_bar.grid(row=3, column=0, pady=10)

        # Create Song Slider
        self.song_slider = ttk.Scale(
            main_frame, from_=0, to=100, orient=HORIZONTAL, length=360, value=0, command=self.slide)
        self.song_slider.grid(row=2, column=0, pady=10)
# end constructor

# Create Function To Deal With Time
    def play_time(self):
        # Check to see if song is stopped
        if self.stopped:
            return
        # Grab Current Song Time
        current_time = pygame.mixer.music.get_pos() / 1000
        # Convert Song Time To Time Format
        converted_current_time = time.strftime(
            '%M:%S', time.gmtime(current_time))

        # Reconstruct song with directory structure stuff
        song = self.playlistBox.get(ACTIVE)
        songPath = self.getPath(song)
        tag = TinyTag.get(songPath)

        # Find Current Song Length

        # song_length = song_mut.info.length
        song_length = tag.duration
        # Convert to time format
        converted_song_length = time.strftime(
            '%M:%S', time.gmtime(song_length))
        # Check to see if song is over
        if int(self.song_slider.get()) == int(song_length):
            self.stop()

        elif self.paused:
            # Check to see if paused, if so - pass
            pass

        else:
            # Move slider along 1 second at a time
            next_time = int(self.song_slider.get()) + 1

            # Output new time value to slider, and to length of song
            self.song_slider.config(to=song_length, value=next_time)

            # Convert Slider poition to time format
            converted_current_time = time.strftime(
                '%M:%S', time.gmtime(int(self.song_slider.get())))

            # Output slider
            self.status_bar.config(
                text=f'Time Elapsed: {converted_current_time} of {converted_song_length}  ')

        # Add Current Time To Status Bar
        if current_time > 0:
            self.status_bar.config(
                text=f'Time Elapsed: {converted_current_time} of {converted_song_length}  ')

        # Create Loop To Check the time every second
        self.status_bar.after(1000, self.play_time)
# FUNEND
# adding songs to playlist

    def addToPlaylist(self):
        songs = filedialog.askopenfilenames(
            title="Choose A Song", filetypes=(("All files", "*.*"), ))
        # Loop thru song list and replace directory structure and mp3 from song name
        for song in songs:
            # Strip out directory structure and .mp3 from song title and only song name will appear
            # os.path.basename(song) returns only title of file from complete path name
            # song var has complete path in it
            self.cur.execute('insert into playlist values(?,?)',
                             [song, os.path.basename(song)])
            self.con.commit()
        self.loadPlaylist()  # load the playlist
# FUNEND

# adding playlist to plabox
    def loadPlaylist(self):
        self.cur.execute('select * from playlist')
        # clear the list box if there id anything
        self.playlistBox.delete(0, END)
        result = self.cur.fetchall()
        if len(result) > 0:
            for rows in result:
                # rows[0] is first col which is path and rows[1] col hold title
                # Add To End of Playlist
                self.playlistBox.insert(END, rows[1])
        else:
            self.playlistBox.insert(
                END, "Playlist is empty : Add songs to playlist")
        # Deleting (Calling destructor)
# FUNEND

# Create Function To Delete a Song From Playlist
    def deleteAsong(self):
        # Delete Highlighted Song From Playlist UI

        selectedSong = self.playlistBox.get(ANCHOR)
        self.cur.execute(
            'delete from playlist where songTitle=?', [selectedSong])
        # save changes parmantely otherwise after closing application changes DB will be unchanged
        self.con.commit()
        self.playlistBox.delete(ANCHOR)  # delete from plaaybox UI
# FUNEND

# Create Function To Delete All Songs From Playlist
    def deleteAllsongs(self):
        self.cur.execute('delete from playlist')
        # save changes parmantely otherwise after closing application changes DB will be unchanged
        self.con.commit()
        # Delete ALL songs
        self.playlistBox.delete(0, END)
        self.playlistBox.insert(END, "Load the playlist")
# FUNEND

    # get song path from DB
    def getPath(self, title):
        res = self.cur.execute(
            "select path from playlist where songTitle=?", [title])
        songPath = res.fetchall()[0]  # we need 0th ele which is required tuple
        # songPath is still tuple but we need string path so need to use 0th ele of tuple
        return songPath[0]  # songPath[0] gives string path
# FUNEND

    # play song
    def play(self, path):
        # Load song with pygame mixer
        pygame.mixer.music.load(path)  # songPath[0] gives string path
        # Play song with pygame mixer
        # loop=0 help to play once
        pygame.mixer.music.play(loops=0)
# FUNEND

# play current song
    def playSong(self):
        selectedSong = self.playlistBox.get(ACTIVE)  # get selected song
        songPath = self.getPath(selectedSong)
        self.play(songPath)
        self.stopped = False  # as song is not stopped
        self.play_time()  # to cal song time and slide
# FUNEND

# pause or unpause song
    def pause(self, is_paused):
        self.paused = is_paused
        if self.paused:
            # Unpause
            pygame.mixer.music.unpause()
            self.paused = False
            self.pauseButton.config(text="pause")
        else:
            # Pause
            pygame.mixer.music.pause()
            self.paused = True
            self.pauseButton.config(text="start")
# FUNEND

 # stop the song
    def stop(self):
        # Stop the song
        pygame.mixer.music.stop()
        # Clear Playlist Bar
        self.playlistBox.selection_clear(ACTIVE)

        self.status_bar.config(text='')

        # Set our slider to zero
        self.song_slider.config(value=0)
        self.stopped = True
# FUNEND

# Create Function To Play The Next Song
    def playNext(self):
        # Reset Slider position and status bar
        self.status_bar.config(text='')
        self.song_slider.config(value=0)

        # Get current song number
        next_one = self.playlistBox.curselection()
        # Add One To The Current Song Number Tuple/list
        next_one = next_one[0] + 1

        # Grab the song title from the playlist
        song = self.playlistBox.get(next_one)
        # get complete path of song from DB
        songPath = self.getPath(song)
        # play the song
        self.play(songPath)
        # Clear Active Bar in Playlist
        self.playlistBox.selection_clear(0, END)
        # Move active bar to next song
        self.playlistBox.activate(next_one)
        # Set Active Bar To next song
        self.playlistBox.selection_set(next_one, last=None)
# FUNEND

# Create function to play previous song
    def playPrev(self):
        # Reset Slider position and status bar
        self.status_bar.config(text='')
        self.song_slider.config(value=0)

        # Get current song number
        prev_one = self.playlistBox.curselection()
        # Add One To The Current Song Number Tuple/list
        prev_one = prev_one[0] - 1

        # Grab the song title from the playlist
        song = self.playlistBox.get(prev_one)
        songPath = self.getPath(song)  # get complete path of selected song
        self.play(songPath)  # paly the song
        # Clear Active Bar in Playlist
        self.playlistBox.selection_clear(0, END)
        # Move active bar to next song
        self.playlistBox.activate(prev_one)
        # Set Active Bar To next song
        self.playlistBox.selection_set(prev_one, last=None)
# FUNEND
# slide func

    def slide(self, x):
        # Reconstruct song with directory structure stuff
        song = self.playlistBox.get(ACTIVE)
        songPath = self.getPath(song)

        # Load song with pygame mixer
        pygame.mixer.music.load(songPath)
        # Play song with pygame mixer
        pygame.mixer.music.play(loops=0, start=self.song_slider.get())

# FUNEND
# destructor
    def __del__(self):
        # self.cur.execute("drop table playList")
        self.con.close()


# CLASS-END
# main driver code
if __name__ == '__main__':
    root = Tk()
    musicPlayer(root)
    root.mainloop()
