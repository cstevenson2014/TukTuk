import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import *
import tkinter as tk
from PIL import ImageTk, Image
import eyed3
import pickle
import os
import requests
from bs4 import BeautifulSoup as bs
from pytube import YouTube
from moviepy.editor import *
from io import BytesIO
import threading
import pyperclip




##########################################################################################################################################################################
############################ Global Variables ############################################################################################################################
##########################################################################################################################################################################

softwareVersionString = 'v2.3'

#urlChunk1 = "https://www.bing.com/images/search?q=album+cover+"
#urlChunk2 = "&go=Search&qs=n&qft=filterui%3Aaspect-square"
#urlCombined = ""
artistNoSpaces = ""
albumNoSpaces = ""
artworkURLFiletype = ""
artworkURL = ""
coversList=[]
coversListIndex = 0

bgThreadIsRunning = 0

listOfCoverLinks = []

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
			'folder':'\U0001F5C0',		# does not work
			'left':'\U00002B05',
			'right':'\U00002B95',
			'info':'\U0001F6C8',
			'gear':'\U00002699',
			'pencil':'\U0001F589',		# does not work
			'document':'\U0001F5CE'		# does not work
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



##########################################################################################################################################################################
############################ Functions ###################################################################################################################################
##########################################################################################################################################################################




def browseOutput():
	print("The fool wants to choose an output directory...")
	
	filename = filedialog.askdirectory()
	if (filename != ''):
		folder_path_output.set(filename)
		print(filename)

def saveFile():

	global artworkURL

	if folder_path_output.get() == "":
		print("No destination directory set, cannot proceed")
		programStatus.set(symbol["warning"] + " You must choose an output directory first!")
		return

	print("saving the metadata to the file...")
	print("filename path: ", file_path_current.get())
	print("song title: ", songTitle.get())
	print("song artist: ", songArtist.get())
	print("song album: ", songAlbum.get())
	print("artwork URL: ", artworkURL)

	audiofile = eyed3.load(file_path_current.get())
	audiofile.tag.artist = songArtist.get()
	audiofile.tag.album = songAlbum.get()
	audiofile.tag.title = songTitle.get()

	if os.path.exists("cover.jpg"):																# If an old cover art image exists, delete it
		print("Previous cover art detected, deleting")
		os.remove("cover.jpg")

	if artworkURL != "":																# If user has specified a new album cover art, proceed through stripping out all old art and embedding the new art
		artworkURLFiletype = artworkURL[-4:]											# grab last 4 characters from URL, which should be the image format (.jpg, .png, etc.)
		print("artwork file type detected as:", artworkURLFiletype)
		print("program will save as .jpg regardless, because I'm lazy")							# This program forces image to be jpg because the eyeD3 module requires you to specify the image type in the function call. 

		with open('cover.jpg', 'wb') as handle:													# download the cover art image and store it in a predictable file
			response = requests.get(artworkURL, stream=True)

			if not response.ok:
				print(response)

			for block in response.iter_content(1024):
				if not block:
					break

				handle.write(block)

		imagedata = open("cover.jpg","rb").read()												# read image into memory

		try:																					# remove all embedded artwork from the file
			listOfImageDescriptions = [y.description for y in audiofile.tag.images]				# get a list of all image descriptions in an id3 tag
			print(listOfImageDescriptions)														# print list of descriptions for debug purposes
			for i in listOfImageDescriptions:													# iterate through each embedded image, by description
				audiofile.tag.images.remove(i)													# remove each image, specified by description
				print("removed cover art with description: ", i)								# print removal confirmation
			
		except:
			print("Error deleting previous art. desctiptions: ", listOfImageDescriptions)

		audiofile.tag.images.set(3,imagedata,"image/jpeg",u"Cover Art")							# insert our cover art as front cover, with description "Cover Art"

		os.remove("cover.jpg")																	# delete the cover art file




	audiofile.tag.save()																		# save the new tag information

	formattedFileName = songArtist.get() + ' - ' + songTitle.get() + '.mp3'

	os.rename('audio.mp3', formattedFileName)


	safelyMoveFile(formattedFileName, folder_path_output.get())


	print("##### Save success #####")
	writeConfigSettings()

	file_path_current.set("")
	songArtist.set("")
	songTitle.set("")
	songAlbum.set("")
	artworkURL = ""

	programStatus.set(symbol["checkmark"] + " File saved, ready for the next one, Cap'n!")

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

def downloadYoutubeVideo():
	print("Downloading youtube video...")
	programStatus.set(symbol['wait'] + " Downloading YouTube video...")
	yt = YouTube(youtubeURL.get())
	
	print('Video URL aquired')
	stream = yt.streams.get_by_itag('140')							#	<Stream: itag="140" mime_type="audio/mp4" abr="128kbps" acodec="mp4a.40.2" progressive="False" type="audio">
	print('Correct audio mp4 stream aquired')
	if os.path.exists("audio.mp4"):																# If an old audio download exists, delete it
		print("Previous audio.mp4 file detected, deleting")
		os.remove("audio.mp4")
	stream.download(filename='audio')
	print("Audio downloaded.")
	
	newFileName = convertMp4ToMp3('audio.mp4')
	#print('Moving downloaded audio to source directory')
	#safelyMoveFile(newFileName, folder_path_source.get())

	youtubeURL.set('')

	return newFileName

def convertMp4ToMp3(filePath: str):
	print('converting mp4 file to an mp3')
	programStatus.set(symbol['wait'] + " Extracting audio from video...")
	#root.update_idletasks
	clip = AudioFileClip(filePath, fps = 44100)
	clip.write_audiofile(filePath[0:-1] + '3')													# trim the trailing 4 off the filename and replace it with a 3 :)
											

	os.remove(filePath)																			# delete the mp4 file
	return filePath[0:-1] + '3'

def downloadTagSaveOneSong():
	
	bgThreadIsRunning = 1

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

	
	#root.update_idletasks

	audiofileName = downloadYoutubeVideo()
	file_path_current.set(audiofileName)
	programStatus.set(symbol['wait'] + " Saving song metadata...")
	#root.update_idletasks
	saveFile()
	displayAlbumCoverPreview(-1)
	programStatus.set(symbol["checkmark"] + " All finished")


	bgThreadIsRunning = 0

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
	youtubeURL.set(pyperclip.paste())
	try:
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
	print("Starting threaded download")
	t1 = threading.Thread(target=lambda: downloadTagSaveOneSong())
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

	# GUI Cluster 1 - Output Folder
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



##########################################################################################################################################################################
############################ Code ###################################################################################################################################
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
file_path_current = StringVar()
file_path_current.set("No File Selected")

# Set up TKinter StringVars
songTitle 		= StringVar()
songArtist 		= StringVar()
songAlbum 		= StringVar()
programStatus 	= StringVar()
youtubeURL 		= StringVar()
artIndexString 	= StringVar()
artSizeString 	= StringVar()
 
albumCoverImageResult = ""																	#	image file thumbnail (not text)
artIndexString.set("")
artSizeString.set("")
programStatus.set("Paste a YouTube link to get started")									#	inital prompt for user

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
btn2.place(x = 10, y = cluster1y, width=210, height=25)

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
btn7 = tk.Button(text="Proceed", command=startThreadedDownload, fg='white')
btn7.config(image=button_l, compound=CENTER)
btn7.place(x = cluster4x, y = cluster4y + spacer, width=260, height=25)




root.mainloop()