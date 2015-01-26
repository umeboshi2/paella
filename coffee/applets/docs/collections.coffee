define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  MainBus = require 'msgbus'
  localStorage = require 'bblocalStorage'
  
  Models = require 'wiki/models'
  AppBus = require 'wiki/msgbus'
  
      

  ########################################
  # Collections
  ########################################
  class PageCollection extends Backbone.Collection
    model: Models.Page
    url: '/paella/pages/index.json'
    
    
  # set handlers on message bus
  #
  main_page_collection = new PageCollection
  AppBus.reqres.setHandler 'pages:collection', ->
    main_page_collection

  AppBus.reqres.setHandler 'pages:getpage', (page_id) ->
    #console.log 'handle pages:getpage ' + page_id
    #model = main_page_collection.get page_id
    model = new Models.Page
      id: page_id
    window.mmodel = model
    #return model
    if model is undefined
      #console.log 'make new page model ' + page_id
      model = new Models.Page
        id: page_id
        content: ''
      main_page_collection.add model
      if page_id == 'intro'
        model.set 'content', 'This is the intro.'
        model.save()
    model
      
  module.exports =
    PageCollection: PageCollection
