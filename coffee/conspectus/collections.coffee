define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'

  MainBus = require 'msgbus'
  Models = require 'models'
  
  class PageCollection extends Backbone.Collection
    model: Models.Page
    url: '/paella/pages/index.json'

  main_page_collection = new PageCollection
  MainBus.reqres.setHandler 'pages:collection', ->
    main_page_collection

  MainBus.reqres.setHandler 'pages:getpage', (name) ->
    # FIXME need to add code to fetch if collection empty
    main_page_collection.get(name)

  ########################################
  # Collections
  ########################################
  module.exports =
    PageCollection: PageCollection
    
  
