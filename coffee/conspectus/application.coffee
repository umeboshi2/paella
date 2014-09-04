define (require, exports, module) ->
  $ = require 'jquery'
  jQuery = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  bootstrap = require 'bootstrap'
  Marionette = require 'marionette'

  
  MainBus = require 'msgbus'
  Models = require 'models'
  
  MainPage = require 'common/mainpage'
  MainPage.set_init_page_handler MainBus
  
  
  require 'frontdoor/main'
  require 'wiki/main'
  require 'bumblr/main'
  require 'hubby/main'

  { prepare_app } = require 'common/approuters'
  
  appmodel = new Backbone.Model
    brand:
      name: 'Conspectus'
      url: '#'
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
      ]

  appregions =
    mainview: 'body'
    navbar: '#main-navbar'
    sidebar: '#sidebar'
    content: '#main-content'
    footer: '#footer'
    
  approutes = [
    'frontdoor:route'
    'wiki:route'
    'bumblr:route'
    'hubby:route'
    ]
    
      
  app = new Marionette.Application()
    
  app.ready = false

  prepare_app app, appmodel, appregions, MainBus, approutes
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
  
    
