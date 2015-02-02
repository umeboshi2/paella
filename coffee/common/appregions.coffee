define (require, exports, module) ->
  $ = require 'jquery'
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  Wreqr = Backbone.Wreqr

  class ModalRegion extends Backbone.Marionette.Region
    el: '#modal'
    #events:
    #  show: (view) ->
    #    @showModal view
    events:
      'view:show': ->
        @showModal @
        
    getEl: (selector) ->
      $el = $ selector
      $el.attr 'class', 'modal bs-example-modal'
      #$el.on 'hidden', @close
      $el

    showModal: (view) ->
      @listenTo view, 'close', @hideModal, @
      @$el.modal 'show'

    hideModal: ->
      @$el.modal 'hide'
      
  class NavBarRegion extends Backbone.Marionette.Region
    el: '#main-navbar'

  basic_appregions = 
    mainview: 'body'
    navbar: NavBarRegion
    sidebar: '#sidebar'
    content: '#main-content'
    footer: '#footer'
    modal: ModalRegion
    
  user_appregions = 
    mainview: 'body'
    navbar: NavBarRegion
    sidebar: '#sidebar'
    content: '#main-content'
    footer: '#footer'
    modal: ModalRegion
    apptriggers:
      navbar:
        show: 'appregion:navbar:displayed'


  prepare_app = (app, appmodel, mainbus) ->
    regions = appmodel.get 'appregions'
    routes = appmodel.get 'approutes'
    mainbus.reqres.setHandler 'main:app:object', ->
      #console.log 'requesting app', app
      app
    #console.log 'handler set for main:app:object'  
    app.radio = Backbone.Wreqr.radio
    app.msgbus = mainbus
    app.appmodel = appmodel
    app.addRegions(regions)
    app.navbar.on 'show', =>
      #console.log "navbar is visible", appmodel
      if appmodel.get 'hasUser'
        #console.log "We have users for app"
        # trigger the creation of a user menu on the navbar
        mainbus.vent.trigger 'appregion:navbar:displayed'
    app.on 'start', ->
      Backbone.history.start() unless Backbone.history.started
    app.addInitializer ->
      # init page
      mainbus.commands.execute 'mainpage:init', appmodel
      # init routes
      for route in routes
        mainbus.commands.execute route

  module.exports =
    prepare_app: prepare_app
    basic_appregions: basic_appregions
    user_appregions: user_appregions
    
