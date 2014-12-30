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
  
  MainPage.set_mainpage_init_handler MainBus
  
  
  # require applets
  require 'frontdoor/main'
  require 'wiki/main'

  
  app = new Marionette.Application()
    
  app.ready = false

  AppRegions.prepare_app app, appmodel, MainBus
  app.ready = true

  
  module.exports = app
  
    
