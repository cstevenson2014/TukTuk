import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import *
import tkinter as tk
from PIL import ImageTk, Image
import eyed3
import pickle
import os
import time
import requests
from bs4 import BeautifulSoup as bs
from pytube import YouTube
from pytube import Playlist
from moviepy.editor import *
from io import BytesIO
import threading
import pyperclip
from random import randint





##########################################################################################################################################################################
############################ Global Variables ############################################################################################################################
##########################################################################################################################################################################

softwareVersionString = 'v2.4'

artistNoSpaces = ""
albumNoSpaces = ""
artworkURLFiletype = ""
artworkURL = ""
coversList=[]
coversListIndex = 0

bgThreadIsRunning = 0
playlistDownloadActive = 0
playlistDownloadIndex = 0

flagEndPlaylistDownloads = 0
#flagSkipPlaylistDownload = 0

listOfCoverLinks = []
listOfPlaylistLinks = []

pickleFileName = 'config.pk'
configList = 	{	
				"destination":""
				}


symbol = 	{										# These are the unicode symbols used around the program
			'alpha':945, 
			'beta':946, 
			'gamma': 947, 
			'delta': 948, 
			'epsilon':949, 
			'recall':'\U000021BB',
			'warning':'\U000026A0',
			'checkmark':'\U00002714',
			'wait':'\U000023F3',
			'folder':'\U0001F5C0',					# does not work
			'left':'\U00002B05',
			'right':'\U00002B95',
			'info':'\U0001F6C8',
			'gear':'\U00002699',
			'pencil':'\U0001F589',					# does not work
			'document':'\U0001F5CE'					# does not work
			}

songParameters = 	{								# Song paramters grouped as a dictionary, to be used if multi downloads are implemented (threading)
					'Used':0,
					'destination':"",
					'title':"",
					'artist':"",
					'album':"",
					'artworkUsed':"",
					'artworkURL':"",
					'title':"",
					'title':"",
					}

listOfTitleCrapToRemove = 	[						# List of common strings to remove from YouTube titles
							'(lyrics)',
							'[lyrics]',
							'(Lyrics)',
							'[Lyrics]',
							'(Audio)',
							'[Audio]',
							'(audio)',
							'[audio]',
							'[Official Video]',
							'(Official Video)',
							'[Official Audio]',
							'(Official Audio)',
							'(Official Music Video)',
							'[Official Music Video]',
							'(Lyric Video)',
							'[Lyric Video]'
							]


class song:

	def __init__(self, title, artist, album, videoURL):
		self.title = title
		self.artist = artist
		self.album = album
		self.videoURL = videoURL
		self.artFile = 'temp' + str(randomInt(8)) + '.jpg'
		self.videoFile = 'temp' + str(randomInt(8)) + '.mp4'
		self.audioFile = 'temp' + str(randomInt(8)) + '.mp3'
		self.artURL = ''
		self.playlist = 0
	








##########################################################################################################################################################################
############################ Functions ###################################################################################################################################
##########################################################################################################################################################################


def randomInt(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

def browseOutput():
	print("The fool wants to choose an output directory...")
	
	filename = filedialog.askdirectory()
	if (filename != ''):
		folder_path_output.set(filename)
		print(filename)

def saveFile(songObject: song):

	#global artworkURL

	if folder_path_output.get() == "":
		print("No destination directory set, cannot proceed")
		programStatus.set(symbol["warning"] + " You must choose an output directory first!")
		return

	print("saving the metadata to the file...")
	print("filename path: ", songObject.audioFile)
	print("song title: ", songObject.title)
	print("song artist: ", songObject.artist)
	print("song album: ", songObject.album)

	audiofile = eyed3.load(songObject.audioFile)
	audiofile.tag.artist = songObject.artist
	audiofile.tag.album = songObject.album
	audiofile.tag.title = songObject.title

	if downloadCoverArt(songObject) != 0:
		print("Failed to download cover art")

	if songObject.artURL != '':
		imagedata = open(songObject.artFile,"rb").read()										# read image into memory

		try:																					# remove all embedded artwork from the file
			listOfImageDescriptions = [y.description for y in audiofile.tag.images]				# get a list of all image descriptions in an id3 tag
			print(listOfImageDescriptions)														# print list of descriptions for debug purposes
			for i in listOfImageDescriptions:													# iterate through each embedded image, by description
				audiofile.tag.images.remove(i)													# remove each image, specified by description
				print("removed cover art with description: ", i)								# print removal confirmation
			
		except:
			print("Error deleting previous art. desctiptions: ", listOfImageDescriptions)
	

		audiofile.tag.images.set(3,imagedata,"image/jpeg",u"Cover Art")							# insert our cover art as front cover, with description "Cover Art"

		os.remove(songObject.artFile)															# delete the cover art file




	audiofile.tag.save()																		# save the new tag information

	formattedFileName = songObject.artist + ' - ' + songObject.title + '.mp3'

	os.rename(songObject.audioFile, formattedFileName)


	safelyMoveFile(formattedFileName, folder_path_output.get())


	print("##### Save success #####")
	writeConfigSettings()

	

	programStatus.set(symbol["checkmark"] + " File saved, ready for the next one, Cap'n!")

def downloadCoverArt(songObject: song):

	if songObject.artURL != '':
		try:
			with open(songObject.artFile, 'wb') as handle:													# download the cover art image and store it in a predictable file
				response = requests.get(songObject.artURL, stream=True)

				if not response.ok:
					print(response)
					return 1

				for block in response.iter_content(1024):
					if not block:
						break

					handle.write(block)
		except: return 99
	else: return 0

def findCoverArtThumbnails(artist: str, album: str):
	global coversListIndex
	global coversList

	coversListIndex = 0

	listOfCoverImages = []
	listOfImageLinks = []
	coversList = []
	artIndexString.set("Searching...")

	if artist == "" or album == "":
		artIndexString.set("")
		artSizeString.set("")
		programStatus.set("Enter an artist and album first")
		return

	try:
		urlCombined = 'https://www.covermytunes.com/search.php?search_query=' + artist.replace(" ", "+") + '+' + album.replace(" ", "+")
		print("Searching for album art with this request:")
		print(urlCombined)
		r = requests.get(urlCombined, verify=False)
		page = r.text
		text_file = open("Output.text", "w")
		text_file.write(page)
		text_file.close()
		soup=bs(page,'html.parser')

		listOfDivs = soup.findAll('div', class_='ProductImage')  

		artIndexString.set("Fetching...")

		for i in listOfDivs:
			listOfImageLinks.append(i.find('a')['href'])

		for i in range(0, len(listOfImageLinks) - 10 ):
			listOfImageLinks.pop()

		j = 1

		for i in listOfImageLinks:
			artSizeString.set(str(j) + ' of ' + str(len(listOfImageLinks)))
			r = requests.get(i, verify=False)
			page = r.text
			soup=bs(page,'html.parser')
			coversList.append(soup.find('img',attrs={'class':'productimg'})['src'])
			j = j + 1

		print('found cover art!')

		displayAlbumCoverPreview(0)
		os.remove('Output.text')
	except:
		if j > 1:
			print('found cover art!')
			displayAlbumCoverPreview(0)
		else:
			artIndexString.set("Error")
		return

def safelyMoveFile(sourceFile: str, destinationFolder: str):
	# Verify destination is clear of a duplicate file
	if os.path.isfile(destinationFolder + '/' + os.path.basename(sourceFile)):
		print("Duplicate file exists in output directory, will not copy")
		return 1

	try:
		os.rename(sourceFile, destinationFolder + '/' + os.path.basename(sourceFile))
	except:
		print('Failed to move a file for some reason')
		return 2

def writeConfigSettings():
	print("Writing updates to config pickle (Rick)")

	configList["destination"] = folder_path_output.get()

	with open(pickleFileName, 'wb') as fi:
		pickle.dump(configList, fi)

def readConfigSettings():
	print("Reading config pickle settings")

	global configList
	try:
		with open(pickleFileName, 'rb') as fi:
			configList = pickle.load(fi)
	except (OSError, IOError) as e:
		with open(pickleFileName, 'wb') as fi:
			pickle.dump(configList, fi)

	if "" ==configList["destination"]:
		print("Config file doesnt have a destination, defaulting to current directory.")
		folder_path_output.set(os.getcwd())
	else:
		folder_path_output.set(configList["destination"])

def downloadYoutubeVideo(songObject: song):
	print("Downloading youtube video...")
	programStatus.set(symbol['wait'] + " Downloading YouTube video...")
	try:
		yt = YouTube(songObject.videoURL)
	except:
		return 2
	print('Video URL aquired')
	try:
		stream = yt.streams.get_by_itag('140')							#	<Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2" progressive="False" type="audio">
		print('Correct audio mp4 stream aquired')
		stream.download(filename=songObject.videoFile[:-4])
		print("Audio downloaded to: ", songObject.videoFile)
	except:
		return 3

	if convertMp4ToMp3(songObject.videoFile, songObject.audioFile) != 0:
		print('Error converting mp4 to mp3.')
		programStatus.set(symbol['alarm'] + " Error converting mp4 to mp3")
		return 1

	

	return 0

def convertMp4ToMp3(inputFile: str, outputFile: str):
	print('converting mp4 file to an mp3')
	programStatus.set(symbol['wait'] + " Extracting audio from video...")

	clip = AudioFileClip(inputFile, fps = 44100)
	clip.write_audiofile(outputFile)									
											
	os.remove(inputFile)																			# delete the mp4 file
	return 0

def downloadTagSaveOneSong(songObject: song):

	global btn7
	global bgThreadIsRunning
	
	bgThreadIsRunning = 1
	btn7["state"] = "disabled"

	if downloadYoutubeVideo(songObject) != 0:
		print("error downloading youtube video")
		programStatus.set(symbol['alarm'] + " Error downloading YouTube video")


	programStatus.set(symbol['wait'] + " Saving song metadata...")
	
	saveFile(songObject)


	

	if (songObject.playlist == 1):
		songTitle.set("")
		songArtist.set("")
		youtubeURL.set('')
	else:
		clearGUI
	
	if songObject.playlist == 0:	programStatus.set(symbol["checkmark"] + " All finished")
	else:							programStatus.set(symbol["wait"] + " Loading next...")


	bgThreadIsRunning = 0
	btn7["state"] = "active"

def displayAlbumCoverPreview(index: int):

	global coversList
	global albumCoverImageResult
	global cluster3x
	global cluster3y
	global artworkURL
	global w1

	if index == -1:
		print('clearing cover art...')
		albumCoverImageResult = ""
		tk.Label(image=albumCoverImageResult, bg='black').place(x = cluster3x + 110, y = cluster3y, width=150, height=150)
		coversList.clear()
		coversList.append("")

		programStatus.set("No cover art will be used")
		artSizeString.set('')
		artIndexString.set('')
		return

	print('Display cover: ' + str(index))

	if coversList[0] == '':
		print('no covers found yet, unable to display a preview image')
		programStatus.set("Must Find Art before displaying it")
	else:
		try:
			print('attempting to display album from URL:')
			print(coversList[index])

			artIndexString.set(str(index + 1) + " of " + str(len(coversList)))
			artSizeString.set("loading...")
			response = requests.get(coversList[index])
			img_data = response.content
			largeImage = Image.open(BytesIO(img_data))
			thumbnail = largeImage.resize((150, 150), Image.ANTIALIAS)
			albumCoverImageResult = ImageTk.PhotoImage(thumbnail)
			width, height = largeImage.size
			tk.Label(root, image=albumCoverImageResult, bg='black').place(x = cluster3x + 110, y = cluster3y, width=150, height=150)
			
			programStatus.set('This cover will be used')
			artworkURL = coversList[index]
			artSizeString.set(str(width) + "x" + str(height))

		except:
			artSizeString.set("error")
			artworkURL = ""
		
def displayNextAlbumCover():
	global coversListIndex

	coversListIndex = coversListIndex + 1

	if coversListIndex > len(coversList):
		coversListIndex = coversListIndex - 1

	
	displayAlbumCoverPreview(coversListIndex)

def displayPrevAlbumCover():
	global coversListIndex
	if coversListIndex > 0:
		coversListIndex = coversListIndex - 1
	else:
		coversListIndex = 0
	
	displayAlbumCoverPreview(coversListIndex)

def useThisAlbumCover():
	songAlbumArtURL.set(coversList[coversListIndex])

def pasteYouTubeLink():

	global listOfPlaylistLinks
	global playlistDownloadActive


	link = pyperclip.paste()
	youtubeURL.set(link)
	print('Pasted link: ', link )
	try:
		if ( 'youtube' in link ):
			if ('&list' in link):
				print("Uh oh, playlist detected")
				try:
					listOfPlaylistLinks = Playlist(link)
					print("You're about to download a playlist. ", len(listOfPlaylistLinks), " videos detected.", )
					displayMessageBox("You're about to download a playlist of videos. Album information and cover art will be retained in case it's the same for each song.")
					tempString = "Fetched playlist with " + str(len(listOfPlaylistLinks)) + " videos"
					programStatus.set("Fetched playlist with " + str(len(listOfPlaylistLinks)) + " videos")

					t3 = threading.Thread(target=lambda: managePlaylistDownload())
					t3.start()

				except:
					programStatus.set(symbol["warning"] + " Failed to fetch playlist videos!")
					return
			else:
				yt = YouTube(youtubeURL.get())
				songTitle.set(extractTitleArtist(yt.title)[0])
				songArtist.set(extractTitleArtist(yt.title)[1])
	except:
		songTitle.set(yt.title)

	programStatus.set("Enter an album title then click Find Art")

def extractTitleArtist(videoTitle: str):
	try:
		data = videoTitle.split(" - ")
		artist = data[0]
		title = data[1]
	except:
		title = videoTitle
		artist = videoTitle
	try:
		for i in listOfTitleCrapToRemove:
			title = title.replace(i, "")
		title = title.strip()
	except:
		pass

	try:
		for i in listOfTitleCrapToRemove:
			artist = artist.replace(i, "")
		artist = artist.strip()
	except:
		pass
		
	return [title, artist]

def startThreadedDownload():

	print("verifying all needed data is present to create song instance")

	programStatus.set(symbol['wait'] + " Processing...")

	if youtubeURL.get() == '':
		programStatus.set(symbol["warning"] + " Paste a YouTube URL to download")
		return
	if folder_path_output.get() == '':
		programStatus.set(symbol["warning"] + " Select an Output Directory to proceed")
		return
	if songTitle.get() == '':
		programStatus.set(symbol["warning"] + " Enter a Track Name to proceed")
		return
	if songArtist.get() == '':
		programStatus.set(symbol["warning"] + " Enter an Artist to proceed")
		return
	if songAlbum.get() == '':
		programStatus.set(symbol["warning"] + " Enter an Album to proceed")
		return

	songObject = song(songTitle.get(), songArtist.get(), songAlbum.get(), youtubeURL.get())

	if artworkURL != '':	songObject.artURL = artworkURL
	if playlistDownloadActive == 1:	songObject.playlist = 1

	print("Starting threaded download.")
	
	t1 = threading.Thread(target=lambda: downloadTagSaveOneSong(songObject))
	t1.start()

def startThreadedAlbumSearch(artist: str, album: str):
	print("Starting threaded album art search")
	t2 = threading.Thread(target=lambda: findCoverArtThumbnails(artist, album))
	t2.start()

def openSettingsWindow():
	print('opening settings window...')
	settings = Toplevel()
	settings.title("TukTuk Settings")
	settings.configure(bg='gray16', width=350, height=60)
	settings.resizable(False, False)

	global button_s

	spacer = 30
	cluster1x = 10
	cluster1y = 0

	# Label - Output Folder
	tk.Label(settings, text="Output Folder: ", bg='gray16', fg='white', justify=LEFT, anchor=W).place(x = cluster1x, y = cluster1y, width=200, height=25)
	tk.Label(settings, textvariable=folder_path_output, bg='gray16', fg='white', justify=LEFT, anchor=W).place(x = cluster1x, y = cluster1y + spacer, width=200, height=25)

	# Button - Browse for Folder
	btn1 = tk.Button(settings, text=symbol['gear'], command=browseOutput, fg='white')
	btn1.config(image=button_s, compound=CENTER)
	btn1.place(x = cluster1x + 290, y = cluster1y + spacer, width=40, height=25)

def displayMessageBox(message: str):
	print('opening message window...')
	messageBox = Toplevel()
	messageBox.configure(bg='gray16', padx=20, pady=20)
	messageBox.resizable(False, False)

	global button_m

	tk.Label(messageBox, text=message, bg='gray16', fg='white', wraplength=200, justify=CENTER).pack()
	btn1 = tk.Button(messageBox, text='Dismiss', command=lambda: messageBox.destroy(), fg='white')
	btn1.config(image=button_m, compound=CENTER, width=45, height=25)
	btn1.pack()

def managePlaylistDownload():

	global listOfPlaylistLinks
	global playlistDownloadActive
	global bgThreadIsRunning
	global btn2
	global cluster1y
	global cluster1x
	global button_m
	global playlistDownloadIndex
	global flagEndPlaylistDownloads


	i = 1
	playlistDownloadIndex = 0
	playlistDownloadActive = 1

	print('Playlist download started...')

	btn2.place_forget()

	btn21 = tk.Button(text="Cancel All", command=cancelPlaylistDownloads, fg='white')
	btn21.config(image=button_m, compound=CENTER)
	btn21.place(x = cluster1x, y = cluster1y, width=100, height=25)

	btn22 = tk.Button(text="Skip Song", command=skipCurrentPlaylistDownload, fg='white')
	btn22.config(image=button_m, compound=CENTER)
	btn22.place(x = cluster1x + 110, y = cluster1y, width=100, height=25)

	for link in listOfPlaylistLinks:
		proceedButton.set("Review then download video " + str(i))
		programStatus.set(symbol["wait"] + " Loading next...")
		print('### Download video ' + str(i) + ' ###')
		print('Link: ' + link)
		youtubeURL.set(link)
		yt = YouTube(link)
		songTitle.set(extractTitleArtist(yt.title)[0])
		songArtist.set(extractTitleArtist(yt.title)[1])

		programStatus.set("Confirm information, then downlaod")

		while (bgThreadIsRunning == 0):									# wait for user to start to download video
			time.sleep(1)
			if (flagEndPlaylistDownloads == 1): break
			if playlistDownloadIndex != (i - 1): break
		while (bgThreadIsRunning == 1):									# wait video to download completely
			time.sleep(1)
			if (flagEndPlaylistDownloads == 1): break
			if playlistDownloadIndex != (i - 1): break

		if playlistDownloadIndex == (i - 1):	playlistDownloadIndex = playlistDownloadIndex + 1
		i = i + 1

		if (flagEndPlaylistDownloads == 1): break

	playlistDownloadActive = 0
	btn21.place_forget()
	btn22.place_forget()
	btn2.place(x = 10, y = cluster1y, width=210, height=25)
	programStatus.set("Paste a YouTube link to get started")									#	inital prompt for user
	proceedButton.set('Proceed')
	listOfPlaylistLinks = []
	playlistDownloadActive = 0
	flagEndPlaylistDownloads = 0
	clearGUI



	

def cancelPlaylistDownloads():
	global flagEndPlaylistDownloads
	flagEndPlaylistDownloads = 1


def skipCurrentPlaylistDownload():
	global playlistDownloadIndex
	playlistDownloadIndex = playlistDownloadIndex + 1

def clearGUI():
	songTitle.set("")
	songArtist.set("")
	youtubeURL.set('')
	songAlbum.set("")
	artworkURL = ""
	displayAlbumCoverPreview(-1)





##########################################################################################################################################################################
############################ GUI ####################################################################################################################################
##########################################################################################################################################################################


# Set up TKinter GUI Stuff
root = Tk()
root.title("TukTuk " + softwareVersionString)
root.geometry("280x385")
root.configure(bg='black')
root.resizable(False, False)

# Initialize default values
folder_path_output = StringVar()
folder_path_output.set("")


# Set up TKinter StringVars
songTitle 		= StringVar()
songArtist 		= StringVar()
songAlbum 		= StringVar()
programStatus 	= StringVar()
youtubeURL 		= StringVar()
artIndexString 	= StringVar()
artSizeString 	= StringVar()
proceedButton	= StringVar()
 
albumCoverImageResult = ""																	#	image file thumbnail (not text)
artIndexString.set("")
artSizeString.set("")
programStatus.set("Paste a YouTube link to get started")									#	inital prompt for user
proceedButton.set('Proceed')

readConfigSettings()																		#	import configuration data

# GUI Button BG Image
button_m = PhotoImage(file="btn_100x25_gray.png")
button_s = PhotoImage(file="btn_50x25_gray.png")
button_l = PhotoImage(file="btn_260x25_gray.png")

# GUI Cluster 1 - Output Folder
spacer = 30
cluster1x = 10
cluster1y = 10

# Button - Open Settings Window
btn1 = tk.Button(text=symbol['gear'], command=openSettingsWindow, fg='white')
btn1.config(image=button_s, compound=CENTER)
btn1.place(x = cluster1x + 220, y = cluster1y, width=40, height=25)

# Button - Paste Video
btn2 = tk.Button(text="Paste YouTube Link", command=pasteYouTubeLink, fg='white')
btn2.config(image=button_l, compound=CENTER)
btn2.place(x = cluster1x, y = cluster1y, width=210, height=25)

# GUI Cluster 2 - Song Metadata Fields
cluster2x = cluster1x
cluster2y = cluster1y + 40

# Title
tk.Label(text="Title: ", bg='black', fg='white', anchor=W).place(x = cluster2x, y = cluster2y, width=100, height=25)
tk.Entry(width=32, textvariable=songTitle, bg='black', fg='white', insertbackground='white', highlightcolor='cyan', relief=FLAT, highlightthickness=1).place(x = cluster2x + 110, y = cluster2y, width=150, height=25)


# Artist
tk.Label(text="Artist: ", bg='black', fg='white', anchor=W).place(x = cluster2x, y = cluster2y + spacer, width=100, height=25)
tk.Entry(width=32, textvariable=songArtist, bg='black', fg='white', highlightcolor='cyan', insertbackground='white', relief=FLAT, highlightthickness=1).place(x = cluster2x + 110, y = cluster2y + spacer, width=150, height=25)

# Album
tk.Label(text="Album: ", bg='black', fg='white', anchor=W).place(x = cluster2x, y = cluster2y + 2*spacer, width=100, height=25)
tk.Entry(width=32, textvariable=songAlbum, bg='black', fg='white', insertbackground='white', highlightcolor='cyan', relief=FLAT, highlightthickness=1).place(x = cluster2x + 110, y = cluster2y + 2*spacer, width=150, height=25)

# GUI Cluster 3 - Cover Art Controls
cluster3x = cluster1x
cluster3y = cluster2y + 100

# Button - Find Art
btn3 = tk.Button(text="Find Art", command=lambda: startThreadedAlbumSearch(songArtist.get(), songAlbum.get()), fg='white')
btn3.config(image=button_m, compound=CENTER)
btn3.place(x = cluster3x, y = cluster3y, width=100, height=25)

# Button - Left, Previous Cover
btn4 = tk.Button(text=symbol['left'], command=displayPrevAlbumCover, fg='white')
btn4.config(image=button_s, compound=CENTER)
btn4.place(x = cluster3x, y = cluster3y + spacer, width=45, height=25)

# Button - Right, Next Cover
btn5 = tk.Button(text=symbol['right'], command=displayNextAlbumCover, fg='white')
btn5.config(image=button_s, compound=CENTER)
btn5.place(x = cluster3x + 55, y = cluster3y + spacer, width=45, height=25)

# Button - Clear Artwork
btn6 = tk.Button(text="Clear", command= lambda: displayAlbumCoverPreview(-1), fg='white')
btn6.config(image=button_m, compound=CENTER)
btn6.place(x = cluster3x, y = cluster3y + 2*spacer, width=100, height=25)

# Label - Cover Information
tk.Label(textvariable=artIndexString, bg='black', fg='white').place(x = cluster3x, y = cluster3y + 3*spacer, width=100, height=25)
tk.Label(textvariable=artSizeString, bg='black', fg='white').place(x = cluster3x, y = cluster3y + 4*spacer, width=100, height=25)

# GUI Cluster 4 - Bottom Status
cluster4x = cluster1x
cluster4y = cluster3y + 170

# Label - Bottom Status Message
tk.Label(textvariable=programStatus, bg='black', fg='white').place(x = cluster4x, y = cluster4y, width=260, height=25)

# Button - Proceed
btn7 = tk.Button(textvariable=proceedButton, command=startThreadedDownload, fg='white')
btn7.config(image=button_l, compound=CENTER)
btn7.place(x = cluster4x, y = cluster4y + spacer, width=260, height=25)




root.mainloop()