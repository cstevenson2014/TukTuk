# TukTuk
## Purpose
Download music from YouTube in a clean, organized manner. This program downloads the video, extracts audio, embeds metadata, embeds album artwork, and then saves the finished file to your output directory.

## Features
- Intelligent title/artist extraction from YouTube title
- Automatically finds album artwork based on artist/album information
- Works with both YouTube videos and playlists

## Installation
I've provided source code, as well as a standalone macOS application.
### macOS
1. Download application from [here](https://www.icloud.com/iclouddrive/0qzPyGAKNvV9hGYfhsoK6cN1A#TukTuk)
2. Run
### Source Code
1. Download the "Source Code" folder
1. cd into the folder and run the following commands
'''
npm install
npm start
'''

![Screenshot](/Screenshots/2020-5-31.png?raw=true)

## Updates
### v3.1 - May 31, 2020
- Recreated program from scratch using Electron/NodeJS

### v2.4 - April 26, 2020
- Added support for downloading playlists

### v2.3 - April 25, 2020
- Moved settings to popup window
- Bug fixes

### v2.2 - April 6, 2020
- Made cursors white so you can see them
- Default directory is current directory, if none set

### v2.1 - April 4, 2020
- Modified GUI for dark theme, should maintain look accross platforms
- Changed cover art searches from Bing to CoverMyTunes.com, results are much higher quality
