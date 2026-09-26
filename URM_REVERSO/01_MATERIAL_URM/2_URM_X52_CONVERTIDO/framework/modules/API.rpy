
init -999 python in x52URM:
    _constant = True

    class x52API(x52NonPicklable):
        def __init__(self, modId, devMode=False):
            self._m1_API__modId = modId
            self.devMode = devMode
            self._m1_API__baseUrl = 'http://localhost:8888' if devMode else 'https://api.0x52.dev'
            self._m1_API__updates = None 
            self._m1_API__latestError = None
            self._m1_API__isUpdating = False
            self._m1_API__hwid = None
        
        @property
        def _m1_API__uaHeader(self):
            return '0x52Mod (Game; {}) (GameVersion; {}) (GameId; {}) (Id; {}) (ModId; {})'.format(renpy.config.name, renpy.config.version, renpy.config.save_directory, self.hwid, self._m1_API__modId)
        
        @property
        def hwid(self):
            """ Hardware ID """
            if self._m1_API__hwid == None:
                self._m1_API__hwid = self._m1_API__generateHwid()
            
            return self._m1_API__hwid
        
        def _m1_API__generateHwid(self):
            hwid = 'None'
            
            try: 
                import uuid
                hwid = str(uuid.UUID(int=uuid.getnode()))
            except:
                pass
            
            return hwid
        
        @property
        def updates(self):
            return self._m1_API__updates
        
        def updateAvailable(self, channel):
            if channel == 'beta':
                latestVersionName = self.latestBetaVersionName
            else:
                latestVersionName = self.latestStableVersionName
            
            if latestVersionName and latestVersionName != 'N/A':
                return latestVersionName
        
        @property
        def latestStableVersionName(self):
            if self._m1_API__updates:
                try:
                    for update in self._m1_API__updates:
                        if update['channel'] == 'stable':
                            return update['versionName']
                except Exception as e:
                    print('0x52: Failed to determine latest stable version. {}. (Got: {})'.format(e, self._m1_API__updates))
                return 'N/A'
        
        @property
        def latestBetaVersionName(self, stableFallback=True):
            """ Get the latest beta version. Returns latest stable if no beta was found (set `stableFallback` to `False` to prevent this) """
            if self._m1_API__updates:
                try:
                    for update in self._m1_API__updates:
                        if update['channel'] == 'beta':
                            return update['versionName']
                except Exception as e:
                    print('0x52: Failed to determine latest beta version. {}. (Got: {})'.format(e, self._m1_API__updates))
                
                if stableFallback:
                    return self.latestStableVersionName
                else:
                    return 'N/A'
        
        @property
        def isUpdating(self):
            return self._m1_API__isUpdating
        
        def performUpdate(self, channel, onSuccess, onError):
            self._m1_API__latestError = None
            
            def onUpdateSuccess():
                self._m1_API__isUpdating = False
                onSuccess()
            
            def onUpdateError(msg):
                self._m1_API__latestError = msg
                self._m1_API__isUpdating = False
                onError(msg)
            
            def threadedCall():
                try:
                    import urllib, zipfile, shutil
                    
                    
                    try:
                        import ssl
                        ssl._create_default_https_context = ssl._create_unverified_context
                    except Exception as e:
                        print('0x52: fetch(): {}'.format(e))
                    
                    if not archivePath:
                        onUpdateError('The mod is not loaded from an archive. This makes updating impossible')
                        return
                    
                    
                    if not renpy.os.access(archivePath, renpy.os.W_OK):
                        print('0x52: Unable to write archive file: "{}"'.format(archivePath))
                        onUpdateError('We don\'t have write access to the mod file, thus it cannot be updated')
                        return
                    
                    
                    availableUpdate = None
                    if self._m1_API__updates and len(self._m1_API__updates) > 0:
                        for update in self._m1_API__updates:
                            if update['channel'] == channel:
                                availableUpdate = update
                                break
                        
                        if not availableUpdate: 
                            availableUpdate = self._m1_API__updates[0]
                    
                    if not availableUpdate:
                        onUpdateError('There is no update available')
                        return
                    
                    
                    tmpFile = archivePath+'.tmp'
                    try:
                        if hasattr(urllib, 'request'): 
                            urllib.request.urlretrieve('{}/modversions/{}/download'.format(self._m1_API__baseUrl, availableUpdate['id']), tmpFile)
                        else:
                            urllib.urlretrieve('{}/modversions/{}/download'.format(self._m1_API__baseUrl, availableUpdate['id']), tmpFile)
                    except Exception as e:
                        onUpdateError('Failed to download file. {}'.format(e))
                        return
                    
                    
                    tmpRPAFile = archivePath+'.update'
                    try:
                        zip = zipfile.ZipFile(tmpFile)
                        for file in zip.filelist:
                            if file.filename.endswith('.rpa'):
                                if hasattr(renpy.os, 'O_BINARY'): 
                                    newRPA = renpy.os.open(tmpRPAFile, renpy.os.O_CREAT | renpy.os.O_WRONLY | renpy.os.O_TRUNC | renpy.os.O_BINARY)
                                else:
                                    newRPA = renpy.os.open(tmpRPAFile, renpy.os.O_CREAT | renpy.os.O_WRONLY | renpy.os.O_TRUNC)
                                renpy.os.write(newRPA, zip.read(file))
                                renpy.os.close(newRPA)
                                break
                        zip.close()
                    except Exception as e:
                        onUpdateError('Failed to extract update. {}'.format(e))
                        return
                    
                    
                    try:
                        renpy.os.remove(tmpFile)
                    except:
                        pass
                    
                    
                    self._m1_API__updates = None 
                    onUpdateSuccess()
                
                except Exception as e:
                    onUpdateError('An unknown error occured. {}'.format(e))
            
            renpy.invoke_in_thread(threadedCall)
        
        def fetchUpdate(self, onSuccess, onError):
            def onUpdates(data):
                self._m1_API__updates = data
                onSuccess()
            
            self._m1_API__updates = None
            self.fetch('/mods/update', onUpdates, onError)
        
        @property
        def latestError(self):
            return self._m1_API__latestError
        
        def fetch(self, url, onSuccess, onError, body=None, headers=None):
            import json
            try: 
                import urllib2 as request
                import urllib2 as error
            except:
                try: 
                    from urllib import request, error
                except Exception as e:
                    self._m1_API__latestError = 'Failed to load urllib: {}'.format(e)
                    return
            
            
            try:
                import ssl
                ssl._create_default_https_context = ssl._create_unverified_context
            except Exception as e:
                print('0x52: fetch(): {}'.format(e))
            
            self._m1_API__latestError = None
            
            headers = headers or {}
            headers['Accept'] = 'application/json'
            headers['Content-Type'] = 'application/json'
            headers['User-Agent'] = self._m1_API__uaHeader
            
            if isinstance(body, dict): 
                body = json.dumps(body)
            
            req = request.Request(self._m1_API__baseUrl+url, headers=headers, data=body)
            def threadedCall():
                try:
                    res = request.urlopen(req, timeout=5)
                    onSuccess(json.loads(res.read()))
                except ValueError as e:
                    self._m1_API__latestError = 'JSONDecodeError: {}'.format(e)
                    onError('JSONDecodeError: {}'.format(e))
                except error.URLError as e:
                    self._m1_API__latestError = 'URLError: {}'.format(e)
                    onError('URLError: {}'.format(e))
                except error.HTTPError as e:
                    self._m1_API__latestError = 'HTTPError: {}'.format(e)
                    onError('HTTPError: {}'.format(e))
                except Exception as e:
                    self._m1_API__latestError = 'Error: {}'.format(e)
                    onError('Error: {}'.format(e))
            
            renpy.invoke_in_thread(threadedCall)            
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
