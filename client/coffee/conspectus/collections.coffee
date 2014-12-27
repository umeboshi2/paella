define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  localStorage = require 'bblocalStorage'

  ########################################
  # Collections
  ########################################
  module.exports = null
  
