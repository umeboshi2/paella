define (require, exports, module) ->
  $ = require 'jquery'
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  Util = require 'common/util'

  basic_appregions = 
    mainview: 'body'
    navbar: '#main-navbar'
    sidebar: '#sidebar'
    content: '#main-content'
    footer: '#footer'

  user_appregions = 
    mainview: 'body'
    navbar: '#main-navbar'
    usermenu: '#user-menu'
    sidebar: '#sidebar'
    content: '#main-content'
    footer: '#footer'
    apptriggers:
      navbar:
        show: 'appregion:navbar:displayed'

  # just show and empty being handled
  # no triggers for empty yet
  add_view_handlers = (mainbus, app, regions, region) ->
    prefix = "appregion:#{region}"
    #console.log "prefix is #{prefix}"
    signal = "#{prefix}:show"
    show_trigger = false
    apptriggers = regions.apptriggers
    #console.log "apptriggers #{[key for key of apptriggers]}"
    if apptriggers and region of apptriggers and 'show' of apptriggers[region]
      show_trigger = apptriggers[region].show
      console.log "show_trigger #{show_trigger}"
    mainbus.vent.on signal, (view) =>
      #[ignore, sigregion, method] = signal.split ':'
      #console.log "#{signal} #{method} called on #{sigregion}=#{region}"
      app[region]?.show view
      if show_trigger
        mainbus.vent.trigger show_trigger, view
    signal = "#{prefix}:empty"
    mainbus.vent.on signal, (view) =>
      #[ignore, sigregion, method] = signal.split ':'
      #console.log "#{signal} #{method} called on #{sigregion}=#{region}"
      if region of app
        app[region]?.empty()

  add_region_view_handlers = (mainbus, app, regions) ->
    for region of regions
      add_view_handlers mainbus, app, regions, region
      
  prepare_app = (app, appmodel, regions, mainbus, routes) ->
    app.addRegions(regions)
    app.on 'start', ->
      Backbone.history.start() unless Backbone.history.started
    app.msgbus = mainbus
    app.addInitializer ->
      # set event handlers
      add_region_view_handlers mainbus, app, regions
      # init page
      mainbus.commands.execute 'mainpage:init', appmodel
      # init routes
      for route in routes
        mainbus.commands.execute route

  class BootStrapAppRouter extends Backbone.Marionette.AppRouter
    onRoute: (name, path, args) ->
      #console.log "onRoute name: #{name}, path: #{path}, args: #{args}"
      Util.navbar_set_active path
      
  module.exports =
    BootStrapAppRouter: BootStrapAppRouter
    prepare_app: prepare_app
    basic_appregions: basic_appregions
    user_appregions: user_appregions
    
