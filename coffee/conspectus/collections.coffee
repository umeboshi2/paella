define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  
  Models = require 'models'
  
  MSGBUS = require 'msgbus'
      

  ########################################
  # Collections
  ########################################
  class BaseCollection extends Backbone.Collection
    # wrap the parsing to retrieve the
    # 'data' attribute from the json response
    parse: (response) ->
      return response.data

  class PageCollection extends BaseCollection
    model: Models.Page

    
  # set handlers on message bus
  #
  main_page_collection = new PageCollection

  MSGBUS.reqres.setHandler 'pages:collection', ->
    main_page_collection

  MSGBUS.reqres.setHandler 'pages:getpage', (page_id) ->
    console.log 'handle pages:getpage ' + page_id
    model = main_page_collection.get page_id
    if model == undefined
      model = new Models.Page
        id: page_id
      main_page_collection.add model
    else
      model
      
  module.exports =
    PageCollection: PageCollection
