define (require, exports, module) ->
  Backbone = require 'backbone'
  MainBus = require 'msgbus'

  Controller = require 'bookstore/controller'
  AppBus = require 'bookstore/msgbus'

  { BootStrapAppRouter } = require 'common/approuters'
  { navigate_to_url } = require 'common/util'
  
    
  # require this for msgbus handlers
  require 'bookstore/collections'

  class Router extends BootStrapAppRouter
    appRoutes:
      #'bookstore': 'start'
      'bookstore': 'defaultSearch'
      'bookstore/search/:searchTerm': 'search'

  MainBus.commands.setHandler 'bookstore:route', () ->
    console.log "bookstore:route being handled"
    books = AppBus.reqres.request 'book:entities'
    #response = books.fetch()
    #response.done =>
    controller = new Controller MainBus
    controller.collection = books
    controller.defaultSearchTerm = 'West Highland Terrier'
    AppBus.vent.on 'list:book:clicked', (book) ->
      controller.showBookDetail book
    AppBus.vent.on 'search:term', (searchTerm) ->
      navigate_to_url "bookstore/search/#{searchTerm}"
    router = new Router
      controller: controller
    console.log 'router created'
      
