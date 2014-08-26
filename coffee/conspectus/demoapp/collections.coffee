define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'

  Models = require 'demoapp/models'
  MSGBUS = require 'msgbus'
      

  ########################################
  # Collections
  ########################################

  # FIXME
  module.exports =
    MSGBUS: MSGBUS
    

    
    