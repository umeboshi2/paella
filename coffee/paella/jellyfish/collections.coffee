define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'

  Models = require 'jellyfish/models'
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
    model: Models.PageModel
    url: '/rest/sitetext'

  main_page_list = new PageCollection
  MSGBUS.reqres.setHandler 'wiki:pagelist', ->
    main_page_list

  MSGBUS.reqres.setHandler 'wiki:pagecontent', (page_id) ->
    main_page_list.get page_id
      
  module.exports =
    PageCollection: PageCollection

    
    