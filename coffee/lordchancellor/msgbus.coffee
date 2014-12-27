define (require, exports, module) ->
  Marionette = require 'marionette'
  Wreqr = Backbone.Wreqr
  module.exports = Wreqr.radio.channel 'global'
