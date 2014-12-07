define (require, exports, module) ->
  $ = require 'jquery'
  jQuery = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  bootstrap = require 'bootstrap'
  Marionette = require 'marionette'

  AppRegions = require 'common/appregions'
  Views = require 'common/mainviews'
  MainPage = require 'common/mainpage'
  
  MainBus = require 'msgbus'
  
  { set_get_current_user_handler } = require 'common/models'

  appmodel = require 'appmodel'
  
  current_user_url = '/paella/rest/v0/main/current/user'
  set_get_current_user_handler MainBus, current_user_url
      
  
  MainPage.set_mainpage_init_handler MainBus
  MainPage.set_main_navbar_handler MainBus

  layout = Views.BootstrapNoGridLayout
  navbar = Views.BootstrapNavBarView
  MainPage.set_init_page_handler MainBus, 'nogridpage', layout, navbar

  
  
  # require applets
  require 'frontdoor/main'
  require 'wiki/main'
  require 'bumblr/main'
  require 'hubby/main'
  require 'bookstore/main'
  
  appmodel = new Backbone.Model
    hasUser: true
    brand:
      name: 'Chassis'
      url: '/'
    apps:
      [
        {
          appname: 'wiki'
          name: 'Wiki'
          url: '#wiki'
        }
        {
          appname: 'bumblr'
          name: 'Bumblr'
          url: '#bumblr'
        }
        {
          appname: 'hubby'
          name: 'Hubby'
          url: '#hubby'
        }
        {
          appname: 'bookstore'
          name: 'Bookstore'
          url: '#bookstore'
        }
      ]
    appregions: AppRegions.user_appregions
    approutes: [
      'frontdoor:route'
      'wiki:route'
      'bumblr:route'
      'hubby:route'
      'bookstore:route'
      ]
      
  app = new Marionette.Application()
  app.ready = false

  user = MainBus.reqres.request 'get-current-user'
  response = user.fetch()
  response.done ->
    AppRegions.prepare_app app, appmodel, MainBus
    app.ready = true

  
  module.exports = app
  
    
