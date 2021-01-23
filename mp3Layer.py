from tkinter import *
from tkinter import filedialog
import pygame
import time
from mutagen.mp3 import MP3
import tkinter.ttk as ttk
import sqlite3

con = sqlite3.connect('song.db')
cur = con.cursor()
cur.execute('''create table if not exists songs (path text)''')

root = Tk()
root.title("MP3 Player")
root.geometry('600x500')

# Initialize Pygame
pygame.mixer.init()

# Create main Frame
main_frame = Frame(root)
main_frame.pack(pady=20)
# create playlist box
playlistBox = Listbox(main_frame, bg="black", fg="yellow",
                      width=60, height=15, selectbackground="red", selectforeground="white")
playlistBox.grid(pady=20)  # verticle paddind


# Create Function To Deal With Time


def play_time():
    # Check to see if song is stopped
    if stopped:
        return

    # Grab Current Song Time
    current_time = pygame.mixer.music.get_pos() / 1000
    # Convert Song Time To Time Format
    converted_current_time = time.strftime('%M:%S', time.gmtime(current_time))

    # Reconstruct song with directory structure stuff
    song = playlistBox.get(ACTIVE)
    song = f'/home/rk/study/Courses/Data science Girlscript/Basic python/mp3Player/audio/{song}.ogg'

    # Find Current Song Length
    song_mut = MP3(song)
    global song_length
    song_length = song_mut.info.length
    # Convert to time format
    converted_song_length = time.strftime('%M:%S', time.gmtime(song_length))

    # Check to see if song is over
    if int(song_slider.get()) == int(song_length):
        stop()

    elif paused:
        # Check to see if paused, if so - pass
        pass

    else:
        # Move slider along 1 second at a time
        next_time = int(song_slider.get()) + 1
        # Output new time value to slider, and to length of song
        song_slider.config(to=song_length, value=next_time)

        # Convert Slider poition to time format
        converted_current_time = time.strftime(
            '%M:%S', time.gmtime(int(song_slider.get())))

        # Output slider
        status_bar.config(
            text=f'Time Elapsed: {converted_current_time} of {converted_song_length}  ')

    # Add Current Time To Status Bar
    if current_time > 0:
        status_bar.config(
            text=f'Time Elapsed: {converted_current_time} of {converted_song_length}  ')

    # Create Loop To Check the time every second
    status_bar.after(1000, play_time)


# Create Function To Add One Song To Playlist


def loadPlaylist():
    cur.execute('select * from songs')
    for rows in cur.fetchall():
        song = rows[0].replace(
            "/home/rk/study/Courses/Data science Girlscript/Basic python/mp3Player/audio/", "")
        song = song.replace(".ogg", "")
        # Add To End of Playlist
        playlistBox.insert(END, song)


# Create Function To Add Many Songs to Playlist


def addToPlaylist():
    songs = filedialog.askopenfilenames(
        initialdir='audio/', title="Choose A Song", filetypes=(("mp3 Files", "*.ogg"), ))

    # Loop thru song list and replace directory structure and mp3 from song name
    for song in songs:
        # Strip out directory structure and .mp3 from song title and only song name will appear
        cur.execute('insert into songs values(?)', [song])
        con.commit()

    # Create Function To Delete One Song From Playlist


def delete_song():
    # Delete Highlighted Song From Playlist
    playlistBox.delete(ANCHOR)

# Create Function To Delete All Songs From Playlist


def delete_all_songs():
    # Delete ALL songs
    playlistBox.delete(0, END)

# create play funstion


def playSong():
    # Set Stopped to False since a song is now playing
    global stopped
    stopped = False

    # Reconstruct song with directory structure stuff
    song = playlistBox.get(ACTIVE)  # select selected song
    # while adding song we have remove path and song title has displayed
    # but now we need sfile path for song. which is hard quoted here same to vurrent directoryS
    # f is python feature to concate
    song = f'/home/rk/study/Courses/Data science Girlscript/Basic python/mp3Player/audio/{song}.ogg'

    # Load song with pygame mixer
    pygame.mixer.music.load(song)
    # Play song with pygame mixer
    pygame.mixer.music.play(loops=0)
    play_time()


# Create Stopped Variable
global stopped
stopped = False


def stop():
    # Stop the song
    pygame.mixer.music.stop()
    # Clear Playlist Bar
    playlistBox.selection_clear(ACTIVE)

    status_bar.config(text='')

    # Set our slider to zero
    song_slider.config(value=0)

    # Set Stop Variable To True
    global stopped
    stopped = True


# Create Function To Play The Next Song
def next_song():
    # Reset Slider position and status bar
    status_bar.config(text='')
    song_slider.config(value=0)

    # Get current song number
    next_one = playlistBox.curselection()
    # Add One To The Current Song Number Tuple/list
    next_one = next_one[0] + 1

    # Grab the song title from the playlist
    song = playlistBox.get(next_one)

    # Add directory structure stuff to the song title
    song = f'/home/rk/study/Courses/Data science Girlscript/Basic python/mp3Player/audio/{song}.ogg'
    # Load song with pygame mixer
    pygame.mixer.music.load(song)
    # Play song with pygame mixer
    pygame.mixer.music.play(loops=0)

    # Clear Active Bar in Playlist
    playlistBox.selection_clear(0, END)

    # Move active bar to next song
    playlistBox.activate(next_one)

    # Set Active Bar To next song
    playlistBox.selection_set(next_one, last=None)

# Create function to play previous song


def previous_song():
    # Reset Slider position and status bar
    status_bar.config(text='')
    song_slider.config(value=0)

    # Get current song number
    next_one = playlistBox.curselection()
    # Add One To The Current Song Number Tuple/list
    next_one = next_one[0] - 1

    # Grab the song title from the playlist
    song = playlistBox.get(next_one)
    # Add directory structure stuff to the song title
    song = f'/home/rk/study/Courses/Data science Girlscript/Basic python/mp3Player/audio/{song}.ogg'
    # Load song with pygame mixer
    pygame.mixer.music.load(song)
    # Play song with pygame mixer
    pygame.mixer.music.play(loops=0)

    # Clear Active Bar in Playlist
    playlistBox.selection_clear(0, END)

    # Move active bar to next song
    playlistBox.activate(next_one)

    # Set Active Bar To next song
    playlistBox.selection_set(next_one, last=None)


# Create Paused Variable
global paused
paused = False

# Create Pause Function


def pause(is_paused):
    global paused
    paused = is_paused

    if paused:
        # Unpause
        pygame.mixer.music.unpause()
        paused = False
    else:
        # Pause
        pygame.mixer.music.pause()
        paused = True


def slide(x):
    # Reconstruct song with directory structure stuff
    song = playlistBox.get(ACTIVE)
    song = f'/home/rk/study/Courses/Data science Girlscript/Basic python/mp3Player/audio/{song}.ogg'

    # Load song with pygame mixer
    pygame.mixer.music.load(song)
    # Play song with pygame mixer
    pygame.mixer.music.play(loops=0, start=song_slider.get())


# Define Button Images For Controls
back_btn_img = PhotoImage(file='images/back50.png')
forward_btn_img = PhotoImage(file='images/forward50.png')
play_btn_img = PhotoImage(file='images/play50.png')
pause_btn_img = PhotoImage(file='images/pause50.png')
stop_btn_img = PhotoImage(file='images/stop50.png')


# Create Button Frame
control_frame = Frame(main_frame)
control_frame.grid(pady=20)

# create play and pause buttons
back_button = Button(control_frame, image=back_btn_img,
                     borderwidth=0, command=previous_song)
forward_button = Button(control_frame, image=forward_btn_img,
                        borderwidth=0, command=next_song)
play_button = Button(control_frame, image=play_btn_img,
                     borderwidth=0, command=playSong)
pause_button = Button(control_frame, image=pause_btn_img,
                      borderwidth=0, command=lambda: pause(paused))
stop_button = Button(control_frame, image=stop_btn_img,
                     borderwidth=0, command=stop)
# put buttons to row and coloumn
back_button.grid(row=0, column=0, padx=10)
forward_button.grid(row=0, column=1, padx=10)
play_button.grid(row=0, column=2, padx=10)
pause_button.grid(row=0, column=3, padx=10)
stop_button.grid(row=0, column=4, padx=10)

# create menu
# Create Main Menu
my_menu = Menu(root)
root.config(menu=my_menu)

# Create Add Song Menu Dropdows
add_song_menu = Menu(my_menu, tearoff=0)
my_menu.add_cascade(label="Add Songs", menu=add_song_menu)
# Add One Song To Playlist
add_song_menu.add_command(
    label="Add Playlist to player", command=loadPlaylist)
# Add Many Songs to Playlist
add_song_menu.add_command(
    label="Add Songs To Playlist", command=addToPlaylist)

# Create Delete Song Menu Dropdowns
remove_song_menu = Menu(my_menu, tearoff=0)
my_menu.add_cascade(label="Remove Songs", menu=remove_song_menu)
remove_song_menu.add_command(
    label="Delete A Song From Playlist", command=delete_song)
remove_song_menu.add_command(
    label="Delete All Songs From Playlist", command=delete_all_songs)

# Create Status Bar
status_bar = Label(root, text='', bd=1, relief=GROOVE, anchor=E)
status_bar.pack(fill=X, side=BOTTOM, ipady=2)

# Create Song Slider
song_slider = ttk.Scale(main_frame, from_=0, to=100,
                        orient=HORIZONTAL, length=360, value=0, command=slide)
song_slider.grid(row=2, column=0, pady=20)

# Temporary Label
my_label = Label(root, text='')
my_label.pack(pady=20)

root.mainloop()
con.close()
