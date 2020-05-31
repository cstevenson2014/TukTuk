const { app, BrowserWindow, clipboard, ipcMain }  = require('electron')

const path          = require('path')
const url           = require('url')
const fs            = require('fs');
const ytdl          = require('ytdl-core');
const ID3Writer     = require('browser-id3-writer');
const ffmpegPath    = require('@ffmpeg-installer/ffmpeg').path;
const ffmpeg        = require('fluent-ffmpeg');
var   gis           = require('g-i-s');
const http          = require('http');
const request       = require('request');
const Path          = require('path');
var ytpl            = require('ytpl');
const del           = require('del');
const Store         = require('electron-store');

ffmpeg.setFfmpegPath(ffmpegPath);
// ----- Packaging Commands ----------------------

// Generate MacOS App
//  electron-packager . --overwrite --platform=darwin --arch=x64 --icon=Assets/icon.icns --prune=true --out=release-builds

// Generate Windows Program
//  electron-packager . TukTuk-app --overwrite --asar=true --platform=win32 --arch=ia32 --icon=Assets/icon.jpg --prune=true --out=release-builds --version-string.CompanyName=CE --version-string.FileDescription=CE --version-string.ProductName="TukTuk"
//  requires Wine for some reason

//  Generate Linux App
//  electron-packager . TukTuk-app --overwrite --asar=true --platform=linux --arch=x64 --icon=Assets/icon.jpg --prune=true --out=release-builds

//  ----- To Do List ------------------------------
//
//  - Clear out temp files at startup
//  - Get system dialogs to work properly
//  - browse for output folder
//  - Download progress doesn't get sent to 2nd or later FFMPEG processes


var globalVideoURL            = ''
var globalOutputDirectory     = ''
var globalPlaylistArray       = ''
var searchResultsJSON         = ''
var globalCoverArtBuffer      = ''

const store = new Store();

globalCoverDefault             = 'Assets/default.jpg'   // If you change this, must also edit the index.HTML file
globalCoverLoading             = 'Assets/loading.gif'
const globalIconICNS          = 'Assets/icon.icns'
const globalIconPNG           = 'Assets/icon.png'

const arrayOfTitleFluff       = [ '(lyrics)',
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
                                  '[Lyric Video]',
                                  '[Video]',
                                  '(Video)'
                                ]








function createWindow () {
  // Create the browser window.
  const win = new BrowserWindow({
    width: 228,
    height: 510,
    minWidth: 228,
    minHeight: 510,
    resizable: false,
    //icon: 'Assets/icon.icns',
    webPreferences: {nodeIntegration: true,
      enableRemoteModule: true}
  })

  win.loadFile('index.html')

  //win.webContents.openDevTools()
}


app.whenReady().then(createWindow)
app.whenReady().then(initialize)

// Quit when all windows are closed.
app.on('window-all-closed', () => {
  // On macOS it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  // On macOS it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})







function resetGUI() {

  globalVideoURL = ''
  document.getElementById("textInputTitle").value = ''
  document.getElementById("textInputArtist").value = ''
  document.getElementById("textInputAlbum").value = ''
  document.getElementById('coverArt').src = gobalCoverDefault

}


function initialize() {
  console.log('Initializing...')
  if (!fs.existsSync('./tmp')){ 
    console.log('creating tmp folder...')
    fs.mkdirSync('./tmp'); 
  }

  (async () => {
    const deletedFilePaths = await del(['tmp/*']);
    //const deletedDirectoryPaths = await del(['tmp', 'public']);
  
    console.log('Deleted files:\n', deletedFilePaths.join('\n'));
    console.log('\n\n');
    //console.log('Deleted directories:\n', deletedDirectoryPaths.join('\n'));
  })();

  globalOutputDirectory = store.get('outputFolder')
  console.log('Output Folder: ' + globalOutputDirectory)

  console.log( 'ffmpeg path: ' + ffmpegPath );

  
}




ipcMain.on('get_globalCoverDefault', (event) => { event.returnValue = globalCoverDefault })
ipcMain.on('get_globalCoverLoading', (event) => { event.returnValue = globalCoverLoading })