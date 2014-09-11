define (require, exports, module) ->
  $ = require 'jquery'
  jQuery = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  bootstrap = require 'bootstrap'
  Marionette = require 'marionette'

  
  MainBus = require 'msgbus'
  Models = require 'models'
  AppRegions = require 'common/appregions'

  { set_get_current_user_handler } = require 'common/models'

  current_user_url = '/rest/v0/main/current/user'
  set_get_current_user_handler MainBus, current_user_url
      
  MainPage = require 'common/mainpage'
  MainPage.set_init_page_handler MainBus
  MainPage.set_main_navbar_handler MainBus
  
  require 'frontdoor/main'

  appmodel = new Backbone.Model
    brand:
      name: 'Cenotaph'
      url: '#'
    apps:
      [
        {
          appname: 'conspectus'
          name: 'Conspectus'
          url: '/app/conspectus'
        }
      ]
    appregions: AppRegions.user_appregions
    approutes: [
      'frontdoor:route'
      ]
    
      
  app = new Marionette.Application()
    
  app.ready = false

  user = MainBus.reqres.request 'get-current-user'
  response = user.fetch()
  response.done ->
    AppRegions.prepare_app app, appmodel, MainBus
    app.ready = true

  # These are handlers to retrieve the colors
  # from the navbars, and are used to create
  # the default color for the fullcalendar
  # events.
  MainBus.reqres.setHandler 'get-navbar-color', ->
    navbar = $ '#main-navbar'
    navbar.css 'color'
    
  MainBus.reqres.setHandler 'get-navbar-bg-color', ->
    navbar = $ '#main-navbar'
    navbar.css 'background-color'
    
  
  module.exports = app
  
    
