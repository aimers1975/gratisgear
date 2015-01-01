#!/usr/bin/env python
import cloudstorage as gcs
from google.appengine.api import users
from google.appengine.api import urlfetch
from google.appengine.api import mail
from google.appengine.api import files, images
from google.appengine.ext import db
from google.appengine.ext import blobstore, deferred
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import app_identity
import datetime
from datetime import timedelta
from time import gmtime, strftime
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
import webapp2
from webapp2_extras import auth
from webapp2_extras import sessions
from webapp2_extras import security
from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError
import logging
import json
import cgi
import urllib
import urllib2
from urlparse import urlparse
import re
import os
import os.path
import uuid
import base64
import string

APP_ID_GLOBAL = 'gratisgear.appspot.com'
STORAGE_ID_GLOBAL = 'gratisgear'
#Probably not necessary to change default retry params, but here for example
my_default_retry_params = gcs.RetryParams(initial_delay=0.2,
                                          max_delay=5.0,
                                          backoff_factor=2,
                                          max_retry_period=15)
tmp_filenames_to_clean_up = []
gcs.set_default_retry_params(my_default_retry_params)
ds_key = ndb.Key(STORAGE_ID_GLOBAL, STORAGE_ID_GLOBAL)

class GratisUser(ndb.Model):
  userPin = ndb.StringProperty()
  userName = ndb.StringProperty()
  userEmail = ndb.StringProperty()
  userlatitude = ndb.FloatProperty()
  userlongitude = ndb.FloatProperty()


class articleImage(ndb.Model):
  imageid = ndb.StringProperty()
  comments = ndb.StringProperty()
  imagefileurl = ndb.StringProperty()
  imagecreationdate = ndb.StringProperty()
  imagearticleid = ndb.StringProperty()

class myArticle(ndb.Model):
  articlename = ndb.StringProperty()
  articleowner = ndb.StringProperty()
  articleid = ndb.StringProperty()
  articletype = ndb.StringProperty()
  articleimageurl = ndb.StringProperty #todo repeat this item
  articletimesviewed = ndb.IntegerProperty()
  articletags = ndb.StringProperty(repeated=True)
  articleprice = ndb.FloatProperty()
  articledescription = ndb.StringProperty()
  articleprivate = ndb.BooleanProperty()
  articlelatitude = ndb.FloatProperty()
  articlelongitude = ndb.FloatProperty()


class BaseHandler(webapp2.RequestHandler):
  def render_template(self, view_filename, params=None):
    if not params:
      params = {}
    path = os.path.join(os.path.dirname(__file__), 'views', view_filename)
    self.response.out.write(template.render(path, params))

class MainHandler(BaseHandler):
  def get(self):
    self.render_template('items.html')

class SendEmail(webapp2.RequestHandler):
  def post(self,target,in_subject,in_message):
    try:

      emailTargetAddress = target
      logging.info("Sending mail to: " + str(target))
      emailSenderAddress = "smart.closet.service@gmail.com"
      content = in_message
      logging.info('Mail content is: ' + str(in_message))
      message = mail.EmailMessage(sender=emailSenderAddress, subject=in_subject)

      if not mail.is_email_valid(emailTargetAddress):
        logging.info("The email is not valid.")
        self.response.out.write("Email address is not valid.")

      message.to = emailTargetAddress
      message.body = """%s""" %(content)
      message.send()
      self.display_message("Message successfully sent.")
    except:
      self.display_message("Unable to contact seller at this time or item is no longer available.")

class DeleteArticle(BaseHandler):
	def post(self):
		logging.info("Delete article called")

class CreateArticle(BaseHandler):
	def post(self):
		logging.info("Create article called")

application = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/CreateArticle', CreateArticle),
    ('/DeleteArticle', DeleteArticle),
    ('/SendEmail', SendEmail)
], debug=True)
