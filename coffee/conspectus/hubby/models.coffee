define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  MSGBUS = require 'msgbus'
  ########################################
  # Models
  ########################################
  class SimpleMeetingModel extends Backbone.Model

  class MainMeetingModel extends Backbone.Model
    url: () ->
      'http://hubby.littledebian.org/rest/v0/main/meeting/' + @id
    parse: (response) ->
      response.data

  class ItemActionModel extends Backbone.Model

  module.exports =
    SimpleMeetingModel: SimpleMeetingModel
    MainMeetingModel: MainMeetingModel
    ItemActionModel: ItemActionModel
    
