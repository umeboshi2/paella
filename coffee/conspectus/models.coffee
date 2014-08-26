define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  ########################################
  # Models
  ########################################

  class Page extends Backbone.Model
    url: () ->
      pathname = '/hubby/pages/'
      if window.location.pathname == '/index.local.html'
        pathname = '/pages/'
      return pathname + @id + '.json'

  module.exports =
    Page: Page
    
