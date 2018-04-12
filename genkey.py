import os
''' AUTO GENERATE SECRET KEY '''
key = os.urandom(64)
    try:
        with open('CTFd/.ctfd_secret_key', 'wb') as secret:
            secret.write(key)
            secret.flush()
            secret.close()
            print 'Generate Succeed'
    except (OSError, IOError):
            print 'Generate Failed'