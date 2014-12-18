define (require, exports, module) ->
  $ = require 'jquery'
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  MainBus = require 'msgbus'

  WikiBus = require 'wiki/msgbus'
  
  AppBus = require 'machines/msgbus'
  Views = require 'machines/views'
  Models = require 'machines/models'
  
    
  marked = require 'marked'
  Collections = require 'collections'

  Util = require 'common/util'

  { SideBarController } = require 'common/controllers'

  side_bar_data = new Backbone.Model
    entries: [
      {
        name: 'List'
        url: '#machines'
      }
      {
        name: 'New Recipy'
        url: '#machines/newrecipe'
      }
      {
        name: 'List Raid'
        url: '#machines/listraid'
      }
      {
        name: 'New Raid'
        url: '#machines/newraid'
      }
      ]

  class Controller extends SideBarController
    mainbus: MainBus
    sidebarclass: Views.SideBarView
    sidebar_model: side_bar_data
      
    make_main_content: ->
      @make_sidebar()
      @list_recipes()


    list_recipes: ->
      @make_sidebar()
      rlist = AppBus.reqres.request 'recipe:collection'
      response = rlist.fetch()
      response.done =>
        view = new Views.SimpleRecipeListView
          collection: rlist
        @App.content.show view
        Util.scroll_top_fast()

    list_raid_recipes: ->
      @make_sidebar()
      rlist = AppBus.reqres.request 'raid_recipe:collection'
      response = rlist.fetch()
      response.done =>
        view = new Views.SimpleRaidRecipeListView
          collection: rlist
        @App.content.show view
        Util.scroll_top_fast()

    edit_recipe: (name) ->
      @make_sidebar()
      recipe = new Models.Recipe
      recipe.name = name
      response = recipe.fetch()
      response.done =>
        view = new Views.EditRecipeView
          model: recipe
        @App.content.show view
        Util.scroll_top_fast()
        
      
    new_recipe: () ->
      @make_sidebar()
      view = new Views.NewRecipeView
      @App.content.show view
      Util.scroll_top_fast()
      
    new_raid_recipe: () ->
      @make_sidebar()
      view = new Views.NewRaidRecipeView
      @App.content.show view
      Util.scroll_top_fast()
      
    set_header: (title) ->
      header = $ '#header'
      header.text title
      
    start: ->
      #console.log 'controller.start called'
      if @App.content.hasView()
        console.log 'empty content....'
        @App.content.empty()
      if @App.sidebar.hasView()
        console.log 'empty sidebar....'
        @App.sidebar.empty()
      @set_header 'VT Dendro'
      @make_main_content()
      #console.log 'machines started'

  module.exports = Controller
  
