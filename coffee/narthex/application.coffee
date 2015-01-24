define (require, exports, module) ->
  $ = require 'jquery'
  jQuery = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  bootstrap = require 'bootstrap'
  Marionette = require 'marionette'

  AppRegions = require 'common/appregions'
  MainPage = require 'common/mainpage'

  MainBus = require 'msgbus'
  appmodel = require 'appmodel'
    
  { set_get_current_user_handler } = require 'common/models'

  current_user_url = '/paella/rest/v0/main/current/user'
  set_get_current_user_handler MainBus, current_user_url
      
  MainPage.set_mainpage_init_handler MainBus
  MainPage.set_main_navbar_handler MainBus
  
  require 'frontdoor/main'
      
  app = new Marionette.Application()
    
  app.ready = false

  user = MainBus.reqres.request 'get-current-user'
  response = user.fetch()
  response.done ->
    AppRegions.prepare_app app, appmodel, MainBus
    app.ready = true
  
  module.exports = app
  
    
