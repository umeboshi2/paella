define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  MainBus = require 'msgbus'
  
  Models = require 'sitetext/models'
  AppBus = require 'sitetext/msgbus'
  
  { BaseCollection } = require 'common/collections'
        

  ########################################
  # Collections
  ########################################
  rscroot = '/rest/v0/main'

  class PageCollection extends BaseCollection
    model: Models.PageModel
    url: rscroot + '/sitetext'

  main_page_list = new PageCollection
  AppBus.reqres.setHandler 'get-pages', ->
    main_page_list

  AppBus.reqres.setHandler 'get-page', (page_id) ->
    main_page_list.get page_id
    
  module.exports =
    PageCollection: PageCollection
    
    