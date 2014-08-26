define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  MSGBUS = require 'msgbus'
  ########################################
  # Models
  ########################################
  class SimpleModel extends Backbone.Model

  module.exports =
    SimpleModel: SimpleModel
