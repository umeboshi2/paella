define (require, exports, module) ->
  $ = require 'jquery'
  jQuery = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  bootstrap = require 'bootstrap'
  Marionette = require 'marionette'
  MSGBUS = require 'msgbus'

  common_models = require 'common/models'

  require 'mainpage'
  
  require 'frontdoor/main'

  prepare_app = (app) ->
    app.addRegions
      mainview: 'body'
      
      content: '#main-content'
      header: '#main-header'
      footer: '#footer'
      
      sidebar: '#sidebar'
      rcontent: '#main-content'
      
    app.on 'start', ->
      Backbone.history.start() unless Backbone.history.started
      
    app.msgbus = MSGBUS

    app.addInitializer ->
      # execute code to generate basic page
      # layout
      MSGBUS.commands.execute 'mainpage:init'

      # then setup the routes
      MSGBUS.commands.execute 'frontdoor:route'
      MSGBUS.commands.execute 'simplerss:route'
      MSGBUS.commands.execute 'jellyfish:route'
      
    # connect events
    MSGBUS.events.on 'mainpage:show', (view) =>
      console.log 'mainpage:show called'
      app.mainview.show view
      
    MSGBUS.events.on 'mainbar:show', (view) =>
      console.log 'mainbar:show called'
      window.testview = view
      #app.mainbar.show view
      MSGBUS.events.trigger 'mainbar:displayed', view
      console.log 'doing nothing in mainpage:show handler'
      
    MSGBUS.events.on 'main-menu:show', (view) =>
      console.log 'main-menu:show called'
      app.main_menu.show view
      
    MSGBUS.events.on 'user-menu:show', (view) =>
      console.log 'user-menu:show called'
      app.user_menu.show view


    MSGBUS.events.on 'sidebar:show', (view) =>
      console.log 'sidebar:show called'
      app.sidebar.show view

    MSGBUS.events.on 'sidebar:close', () =>
      console.log 'sidebar:close called'
      app.sidebar.close()

      
    MSGBUS.events.on 'rcontent:show', (view) =>
      console.log 'rcontent:show called'
      app.rcontent.show view
      
    MSGBUS.events.on 'rcontent:close', () =>
      app.rcontent.close()
      
            
      
  app = new Marionette.Application()
  prepare_app app
                        
  module.exports = app
  
    
