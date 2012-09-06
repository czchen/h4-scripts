# -*- coding: utf-8 -*-

import sys
from Config import Config
from Logger import Logger
import facebook_unofficial_api

DEBUG = int(Config()['other']['debug'])

logger = Logger('h4_create_fb_event').__new__()

if __name__ == '__main__':
    f = facebook_unofficial_api.Facebook()

    if f.login():
        if DEBUG:
            print 'facebook login'
            #print f.getUID()

        event_id = f.create_event()

        if event_id:
            if DEBUG:
                print 'create event success : http://www.facebook.com/events/%s/' % (event_id)
            else:
                logger.info('create event success : http://www.facebook.com/events/%s/' % (event_id))
        else:
            if DEBUG:
                print 'create event failed'
            else:
                logger.error('create event failed')
    else:
        sys.exit()
