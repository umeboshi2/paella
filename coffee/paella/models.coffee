define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  ########################################
  # Models
  ########################################

  class Page extends Backbone.Model
    url: () ->
      '/paella/pages/' + @id + '.json'


  Backbone.sync
  module.exports =
    Page: Page
    
