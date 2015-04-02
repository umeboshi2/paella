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
        name: 'New Machine'
        url: '#machines/newmachine'
      }
      ]

  class Controller extends SideBarController
    mainbus: MainBus
    sidebarclass: Views.SideBarView
    sidebar_model: side_bar_data
      
    make_main_content: ->
      @make_sidebar()
      @list_machines()


    list_machines: ->
      @make_sidebar()
      collection = AppBus.reqres.request 'machine:collection'
      response = collection.fetch()
      response.done =>
        view = new Views.SimpleMachineListView
          collection: collection
        window.lmview = view
        @App.content.show view
        Util.scroll_top_fast()

    view_machine: (name) ->
      console.log 'view_machine called'
      @make_sidebar()
      machine = new Models.Machine
      machine.name = name
      response = machine.fetch()
      response.done =>
        view = new Views.BasicMachineView
          model: machine
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
        
    new_machine: () ->
      console.log 'new_machine called'
      @make_sidebar()
      collection = AppBus.reqres.request 'machine:collection'
      machine = new Backbone.Model
      view = new Views.NewMachineView
        model: machine
        collection: collection
        
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
  
