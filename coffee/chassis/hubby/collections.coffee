define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'

  Models = require 'hubby/models'
  AppBus = require 'hubby/msgbus'
  
  ########################################
  # Collections
  ########################################
  class BaseCollection extends Backbone.Collection
    # wrap the parsing to retrieve the
    # 'data' attribute from the json response
    parse: (response) ->
      return response.data

  class MeetingCollection extends BaseCollection
    model: Models.SimpleMeetingModel
    url: 'http://hubby.littledebian.org/rest/v0/main/meeting'

  main_meeting_list = new MeetingCollection
  AppBus.reqres.setHandler 'meetinglist', ->
    main_meeting_list

  class ItemActionCollection extends BaseCollection
    model: Models.ItemActionModel

  make_item_action_collection = (itemid) ->
    url = 'http://hubby.littledebian.org/rest/v0/main/itemaction/' + itemid
    c = new ItemActionCollection
    c.url = url
    return c
    
  AppBus.reqres.setHandler 'item_action_collection', (itemid) ->
    make_item_action_collection itemid
    
  module.exports =
    MeetingCollection: MeetingCollection

    
    