define (require, exports, module) ->
  $ = require 'jquery'
  jQuery = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'

  AppRegions = require 'common/appregions'

  appmodel = new Backbone.Model
    hasUser: true
    brand:
      name: 'Paella'
      url: '/paella'
    apps: []
    appregions: AppRegions.user_appregions
    approutes: [
      'frontdoor:route'
      ]
    
  
  module.exports = appmodel
  
  
    
