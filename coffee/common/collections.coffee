define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  PageableCollection = require 'backbone.paginator'

  ########################################
  # Collections
  ########################################
  class BaseCollection extends Backbone.Collection
    # wrap the parsing to retrieve the
    # 'data' attribute from the json response
    parse: (response) ->
      return response.data

  class OffsetLimitCollection extends PageableCollection
    queryParams:
      pageSize: 'limit'
      offset: () ->
        @state.currentPage * @state.pageSize
        
  module.exports =
    BaseCollection: BaseCollection
    OffsetLimitCollection: OffsetLimitCollection
    
