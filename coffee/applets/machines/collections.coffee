define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  PageableCollection = require 'backbone.paginator'

  MainBus = require 'msgbus'
  localStorage = require 'bblocalStorage'

  AppBus = require 'machines/msgbus'
  
  CommonCollections = require 'common/collections'

  ########################################
  # Collections
  ########################################
  class OffsetLimitCollection extends CommonCollections.OffsetLimitCollection
    mode: 'server'
    full: true
    
    parse: (response) ->
      #console.log "parsing response", response
      #window.gcresponse = response
      total_count = response.total_count
      @state.totalRecords = total_count
      super response.data

  class BaseCollection extends OffsetLimitCollection
    state:
      firstPage: 0
      pageSize: 30

  class MachineCollection extends BaseCollection
    url: '/paella/rest/v0/main/admin/machines'

  main_machine_collection = new MachineCollection
  AppBus.reqres.setHandler 'machine:collection', ->
    main_machine_collection
    
  module.exports =
    MachineCollection: MachineCollection
    
