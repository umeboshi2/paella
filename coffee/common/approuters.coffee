define (require, exports, module) ->
  $ = require 'jquery'
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  Util = require 'common/util'

  prepare_app = (app, appmodel, regions, mainbus, routes) ->
    app.addRegions(regions)
    app.on 'start', ->
      Backbone.history.start() unless Backbone.history.started
    app.msgbus = mainbus
    app.addInitializer ->
      # set event handlers
      mainbus.vent.on 'mainpage:show', (view) =>
        app.mainview.show view
      mainbus.vent.on 'sidebar:show', (view) =>
        app.sidebar.show view
      mainbus.vent.on 'sidebar:close', (view) =>
        if 'sidebar' in app
          app.sidebar.destroy()
      mainbus.vent.on 'main-navbar:show', (view) =>
        app.navbar.show view
      mainbus.vent.on 'user-menu:show', (view) =>
        app.user-menu.show view
      mainbus.vent.on 'rcontent:show', (view) =>
        app.content.show view
      mainbus.vent.on 'rcontent:close', (view) =>
        if app.content?.currentView?
          app.content.empty()
      # init page
      mainbus.commands.execute 'mainpage:init', appmodel
      # init routes
      for route in routes
        mainbus.commands.execute route

  class BootStrapAppRouter extends Backbone.Marionette.AppRouter
    onRoute: (name, path, args) ->
      #console.log 'onRoute name: ' + name
      #console.log 'onRoute path: ' + path
      #console.log 'onRoute args:' + args
      Util.navbar_set_active path
      
  module.exports =
    BootStrapAppRouter: BootStrapAppRouter
    prepare_app: prepare_app