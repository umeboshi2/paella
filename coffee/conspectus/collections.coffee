define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  
  Models = require 'models'
  
  MSGBUS = require 'msgbus'
  localStorage = require 'bblocalStorage'
  
      

  ########################################
  # Collections
  ########################################
  class PageCollection extends Backbone.Collection
    localStorage: new localStorage('pages')
    model: Models.Page

    
  # set handlers on message bus
  #
  main_page_collection = new PageCollection
  MSGBUS.reqres.setHandler 'pages:collection', ->
    main_page_collection

  MSGBUS.reqres.setHandler 'pages:getpage', (page_id) ->
    console.log 'handle pages:getpage ' + page_id
    model = main_page_collection.get page_id
    window.mmodel = model
    #return model
    if model is undefined
      console.log 'make new page model ' + page_id
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
