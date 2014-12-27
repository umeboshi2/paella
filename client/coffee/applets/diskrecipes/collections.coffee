define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  PageableCollection = require 'backbone.paginator'

  MainBus = require 'msgbus'
  localStorage = require 'bblocalStorage'

  AppBus = require 'diskrecipes/msgbus'
  
  CommonCollections = require 'common/collections'

  ########################################
  # Collections
  ########################################
  class OffsetLimitCollection extends CommonCollections.OffsetLimitCollection
    mode: 'server'
    full: true
    
    parse: (response) ->
      #console.log "parsing response", response
      #window.gcresponse = response
      total_count = response.total_count
      @state.totalRecords = total_count
      super response.data

  class BaseCollection extends OffsetLimitCollection
    state:
      firstPage: 0
      pageSize: 30

  class RecipeCollection extends BaseCollection
    url: '/paella/rest/v0/main/recipes'

  class RaidRecipeCollection extends BaseCollection
    url: '/paella/rest/v0/main/raidrecipes'
    
  main_recipe_collection = new RecipeCollection
  AppBus.reqres.setHandler 'recipe:collection', ->
    main_recipe_collection
    
  main_raid_recipe_collection = new RaidRecipeCollection
  AppBus.reqres.setHandler 'raid_recipe:collection', ->
    main_raid_recipe_collection
    
  module.exports =
    RecipeCollection: RecipeCollection
    RaidRecipeCollection: RaidRecipeCollection
    
