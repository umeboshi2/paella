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
    apps:
      [
        {
          appname: 'diskrecipes'
          name: 'Disk Recipes'
          url: '#diskrecipes'
        }
        {
          appname: 'machines'
          name: 'Machines'
          url: '#machines'
        }
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
      'diskrecipes:route'
      'machines:route'
      ]
    
      
  module.exports = appmodel
  
  
    
