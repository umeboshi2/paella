define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
    
  ########################################
  # Models
  ########################################
  class Machine extends Backbone.Model
    url: () ->
      "/paella/rest/v0/main/admin/machines/#{@name}"
    
  module.exports =
    Machine: Machine
