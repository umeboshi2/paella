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
  MainPage.set_mainpage_init_handler MainBus
  MainPage.set_main_navbar_handler MainBus
  
  
  require 'frontdoor/main'
  require 'useradmin/main'
  require 'sitetext/main'
  
  appmodel = new Backbone.Model
    hasUser: true
    brand:
      name: 'Chassis'
      url: '/'
    apps:
      [
        {
          appname: 'useradmin'
          name: 'Accounts'
          url: '#useradmin'
        }
        {
          appname: 'sitetext'
          name: 'Site Text'
          url: '#sitetext'
        }
      ]
    appregions: AppRegions.user_appregions
    approutes: [
      'frontdoor:route'
      'useradmin:route'
      'sitetext:route'
      ]
    
      
  app = new Marionette.Application()
    
  app.ready = false

  user = MainBus.reqres.request 'get-current-user'
  response = user.fetch()
  response.done ->
    AppRegions.prepare_app app, appmodel, MainBus
    app.ready = true

  
  module.exports = app
  
    
