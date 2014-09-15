define (require, exports, module) ->
  $ = require 'jquery'
  jQuery = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'

  AppRegions = require 'common/appregions'
  
  appmodel = new Backbone.Model
    hasUser: true
    brand:
      name: 'Chassis'
      url: '/'
    apps:
      [
        {
          appname: 'useradmin'
          name: 'Accounts'
          url: '#useradmin'
        }
        {
          appname: 'sitetext'
          name: 'Site Text'
          url: '#sitetext'
        }
      ]
    appregions: AppRegions.user_appregions
    approutes: [
      'frontdoor:route'
      'useradmin:route'
      'sitetext:route'
      ]
    
      
  module.exports = appmodel
  
  
    
