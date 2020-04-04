from tkinter import ttk
from tkinter import filedialog
from tkinter import *
from PIL import ImageTk, Image
import tkinter
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

softwareVersionString = 'v1.4'

urlChunk1 = "https://www.bing.com/images/search?q=album+cover+"
urlChunk2 = "&go=Search&qs=n&qft=filterui%3Aaspect-square"
urlCombined = ""
artistNoSpaces = ""
albumNoSpaces = ""
artworkURLFiletype = ""
coversList=[]
coversListIndex = 0

bgThreadIsRunning = 0

pickleFileName = 'config.pk'
configList = 	{	
				"destination":"", 
				"title":"title", 
				"artist":"artist", 
				"album":"album",
				"art":"https://www.google.com"
				}


symbol = 	{	
			'alpha':945, 
			'beta':946, 
			'gamma': 947, 
			'delta': 948, 
			'epsilon':949, 
			'recall':'\U000021BB',
			'warning':'\U000026A0',
			'checkmark':'\U00002714',
			'wait':'\U000023F3'
			}

songParameters = 	{
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



##########################################################################################################################################################################
############################ Functions ###################################################################################################################################
##########################################################################################################################################################################




def browseOutput():
	print("The fool wants to choose an output directory...")
	filename = filedialog.askdirectory()
	folder_path_output.set(filename)
	print(filename)

def saveFile():

	if folder_path_output.get() == "":
		print("No destination directory set, cannot proceed")
		programStatus.set(symbol["warning"] + " You must choose an output directory first!")
		return

	print("saving the metadata to the file...")
	print("filename path: ", file_path_current.get())
	print("song title: ", songTitle.get())
	print("song artist: ", songArtist.get())
	print("song album: ", songAlbum.get())
	print("artwork URL: ", songAlbumArtURL.get())

	audiofile = eyed3.load(file_path_current.get())
	audiofile.tag.artist = songArtist.get()
	audiofile.tag.album = songAlbum.get()
	audiofile.tag.title = songTitle.get()

	if os.path.exists("cover.jpg"):																# If an old cover art image exists, delete it
		print("Previous cover art detected, deleting")
		os.remove("cover.jpg")

	if songAlbumArtURL.get() != "":																# If user has specified a new album cover art, proceed through stripping out all old art and embedding the new art
		artworkURLFiletype = songAlbumArtURL.get()[-4:]											# grab last 4 characters from URL, which should be the image format (.jpg, .png, etc.)
		print("artwork file type detected as:", artworkURLFiletype)
		print("program will save as .jpg regardless, because I'm lazy")							# This program forces image to be jpg because the eyeD3 module requires you to specify the image type in the function call. 

		with open('cover.jpg', 'wb') as handle:													# download the cover art image and store it in a predictable file
			response = requests.get(songAlbumArtURL.get(), stream=True)

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



	""" if os.path.isfile(folder_path_output.get() + '/' + os.path.basename(file_path_current.get())):
		print("Duplicate file exists in output directory, will not copy")
		programStatus.set(symbol["warning"] + " Duplicate file exists in output directory!")
		return


	try:
		os.rename(file_path_current.get(), folder_path_output.get() + '/' + os.path.basename(file_path_current.get()))
	except:
		print("Failed to move file for some reason")
		programStatus.set(symbol["warning"] + " Failed to move the file to output folder") """

	print("##### Save success #####")
	writeConfigSettings()

	file_path_current.set("")
	songArtist.set("")
	songTitle.set("")
	songAlbum.set("")
	songAlbumArtURL.set("")

	programStatus.set(symbol["checkmark"] + " File saved, ready for the next one, Cap'n!")

def searchAndPullAlbumArt():

	global coversList

	coversList = []

	

	urlCombined = urlChunk1 + songArtist.get().replace(" ", "+") + '+' + songAlbum.get().replace(" ", "+") + urlChunk2
	print("Searching for album art with this request:")
	print(urlCombined)
	r = requests.get(urlCombined)
	page = r.text
	soup=bs(page,'html.parser')

	covers = soup.findAll('a',attrs={'class':'thumb'})
	
	for v in covers:
		tmp = v['href']
		coversList.append(tmp)

	print('found cover art!')

	displayAlbumCoverPreview(0)

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

	#configList["source"] = folder_path_source.get()
	configList["destination"] = folder_path_output.get()
	configList["title"] = songTitle.get()
	configList["artist"] = songArtist.get()
	configList["album"] = songAlbum.get()
	configList["art"] = songAlbumArtURL.get()

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

	#folder_path_source.set(configList["source"])
	folder_path_output.set(configList["destination"])

def recallTrackName():
	songTitle.set(configList["title"])

def recallArtist():
	songArtist.set(configList["artist"])

def recallAlbum():
	songAlbum.set(configList["album"])

def recallArt():
	songAlbumArtURL.set(configList["art"])

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
	programStatus.set(symbol["checkmark"] + " All finished :)")

	ttk.Label(mainframe, image="").grid(column=2, row=8, rowspan=4, sticky=(W, E, N, S))

	bgThreadIsRunning = 0

def displayAlbumCoverPreview(index: int):

	global coversList
	global albumCoverImageResult

	if coversList[0] == '':
		print('no covers found yet, unable to display a preview image')
		programStatus.set("Must Find Art before displaying it")
	else:
		try:
			print('attempting to display album from URL:')
			print(coversList[index])
			response = requests.get(coversList[index])
			img_data = response.content
			largeImage = Image.open(BytesIO(img_data))
			thumbnail = largeImage.resize((150, 150), Image.ANTIALIAS)
			albumCoverImageResult = ImageTk.PhotoImage(thumbnail)
			width, height = largeImage.size
			ttk.Label(mainframe, image=albumCoverImageResult).grid(column=2, row=8, rowspan=4, sticky=(W, E, N, S))
			programStatus.set("Artwork " + str(index) + " - Displayed | " + str(width) + "x" + str(height) )
			songAlbumArtURL.set(coversList[index])

		except:
			programStatus.set("Artwork " + str(index) + " - Bad result, can't display")
			songAlbumArtURL.set("")
		
def displayNextAlbumCover():
	global coversListIndex
	coversListIndex = coversListIndex + 1
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
		title = title.replace("[Official Video]", "")
		title = title.replace("(Official Video)", "")
		title = title.replace("[Official Audio]", "")
		title = title.replace("(Official Audio)", "")
		title = title.replace("(Official Music Video)", "")
		title = title.replace("[Official Music Video]", "")
		title = title.replace("(Lyric Video)", "")
		title = title.replace("[Lyric Video]", "")

		title = title.strip()
	except:
		pass

	try:

		artist = artist.replace("[Official Video]", "")
		artist = artist.replace("(Official Video)", "")
		artist = artist.replace("[Official Audio]", "")
		artist = artist.replace("(Official Audio)", "")
		artist = artist.replace("(Official Music Video)", "")
		artist = artist.replace("[Official Music Video]", "")
		artist = artist.replace("(Lyric Video)", "")
		artist = artist.replace("[Lyric Video]", "")

		artist = artist.strip()
	except:
		pass
		
	return [title, artist]

def startThreadedDownload(*args):
   t = threading.Thread(target=lambda: downloadTagSaveOneSong())
   t.start()
	#	Thread(target=originalfunc, args=(PLACEHOLDER,))

##########################################################################################################################################################################
############################ Code ###################################################################################################################################
##########################################################################################################################################################################


# Set up TKinter Stuff
root = Tk()
root.title("TukTuk " + softwareVersionString)
mainframe = ttk.Frame(root, padding="12 12 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Initialize default values
folder_path_output = StringVar()
folder_path_output.set("")
file_path_current = StringVar()
file_path_current.set("No File Selected")

# Set up TKinter StringVars
songTitle = StringVar()
songArtist = StringVar()
songAlbum = StringVar()
programStatus = StringVar()
songAlbumArtURL = StringVar()
youtubeURL = StringVar()

 
albumCoverImageResult = ""																	#	image file thumbnail (not text)

programStatus.set("Paste a YouTube link to get started")									#	inital prompt for user

readConfigSettings()																		#	import configuration data



# Row One
ttk.Label(mainframe, text="YouTube URL: ").grid(column=1, row=1, sticky=W)
ttk.Label(mainframe, textvariable=youtubeURL).grid(column=2, row=1, sticky=W)
ttk.Button(mainframe, text="Paste", command=pasteYouTubeLink).grid(column=3, row=1, sticky=E)

# Row Two
ttk.Label(mainframe, text="Output Directory: ").grid(column=1, row=2, sticky=W)
ttk.Label(mainframe, textvariable=folder_path_output).grid(column=2, row=2, sticky=W)
ttk.Button(mainframe, text="Browse", command=browseOutput).grid(column=3, row=2, sticky=E)

# Row Three

# Row Four
ttk.Label(mainframe, text="Song Title: ").grid(column=1, row=4, sticky=W)
entryTitle = ttk.Entry(mainframe, width=32, textvariable=songTitle)
entryTitle.grid(column=2, row=4, sticky=W)
ttk.Button(mainframe, text=symbol["recall"], command=recallTrackName).grid(column=3, row=4, sticky=E)

# Row Five
ttk.Label(mainframe, text="Artist: ").grid(column=1, row=5, sticky=W)
entryArtist = ttk.Entry(mainframe, width=32, textvariable=songArtist)
entryArtist.grid(column=2, row=5, sticky=W)
ttk.Button(mainframe, text=symbol["recall"], command=recallArtist).grid(column=3, row=5, sticky=E)

# Row Six
ttk.Label(mainframe, text="Album: ").grid(column=1, row=6, sticky=W)
entryAlbum = ttk.Entry(mainframe, width=32, textvariable=songAlbum)
entryAlbum.grid(column=2, row=6, sticky=W)
ttk.Button(mainframe, text=symbol["recall"], command=recallAlbum).grid(column=3, row=6, sticky=E)

# Row Seven
ttk.Label(mainframe, text="Album Art URL: ").grid(column=1, row=7, sticky=W)
entryArtURL = ttk.Entry(mainframe, width=32, textvariable=songAlbumArtURL)
entryArtURL.grid(column=2, row=7, sticky=W)
ttk.Button(mainframe, text=symbol["recall"], command=recallArt).grid(column=3, row=7, sticky=E)

# Row Eight
ttk.Label(mainframe, image=albumCoverImageResult).grid(column=2, row=8, rowspan=4, sticky=(W, E, N, S))
ttk.Button(mainframe, text="Find Art", command=searchAndPullAlbumArt).grid(column=3, row=8, sticky=(W, E))

# Row Nine
ttk.Button(mainframe, text="Prev Cover", command=displayPrevAlbumCover).grid(column=3, row=9, sticky=(W, E))

# Row Ten
ttk.Button(mainframe, text="Next Cover", command=displayNextAlbumCover).grid(column=3, row=10, sticky=(W, E))

# Row Eleven

# Row Twelve
ttk.Label(mainframe, text="Status: ").grid(column=1, row=12, sticky=W)
ttk.Label(mainframe, textvariable=programStatus, width=32).grid(column=2, row=12, sticky=(W, E))
ttk.Button(mainframe, text="Proceed", command=startThreadedDownload).grid(column=3, row=12, sticky=(W, E))



for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)



root.mainloop()
