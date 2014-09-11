define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'

  AppBus = require 'bookstore/msgbus'
    
  ########################################
  # Models
  ########################################
  class Book extends Backbone.Model

      
  module.exports =
    Book: Book
