define (require, exports, module) ->
  $ = require 'jquery'
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  MainBus = require 'msgbus'

  Views = require 'bookstore/views'
  AppBus = require 'bookstore/msgbus'
  # make sure handlers are set
  require 'bookstore/collections'
  
  { SideBarController } = require 'common/controllers'
  

  class Marionette.Region.Dialog extends Marionette.Region
    constructor: ->
      _.extend @, Backbone.Events

    onShow: (view) ->
      @setupBindings view
      options = @getDefaultOptions(_.result(view, 'dialog'))
      #console.log options
      @$el.modal options,
        close: (e, ui) =>
          @closeDialog()

    getDefaultOptions: (options={}) ->
      _.defaults options,
        show: true
        keyboard: true

    setupBindings: (view) ->
      @listenTo view, 'dialog:close', @closeDialog

    closeDialog: ->
      #console.log "Marionette.Region.Dialog>> calling in the cleaner!"
      @$el.modal "hide"
      @stopListening()
      @close()      

  dialog_data =
    title: "Edit Event"
    className: "dialogClass"
    buttons: false
    
  side_bar_data = new Backbone.Model
    entries: [
      {
        name: 'Home'
        url: '#'
      }
      ]

  class Controller extends SideBarController
    mainbus: MainBus
    sidebarclass: Views.SideBarView
    sidebar_model: side_bar_data

    make_main_content: ->
      @make_sidebar()

    listBooks: (books) ->
      @layout = @getLayout()
      @layout.on 'show', =>
        @showSearchBar()
        @showBookList books
      AppBus.vent.trigger 'app:show', @layout

    showBookDetail: (book) ->
      console.log "controller>> showBookDetail"
      view = @getDetailView book
      view.on "dialog:button:clicked", ->
        console.log "editView instance dialog:button:clicked"
      AppBus.vent.trigger "app:show:modal", view

    getDetailView: (book) ->
      new Views.BookDetailView
        model: book

    showBookList: (items) ->
      bookListView = @getBookListView items
      @layout.books.show bookListView

    getBookListView: (items) ->
      new Views.BookList
        collection: items

    showSearchBar: ->
      searchView = @getSearchView()
      @layout.search.attachView searchView

    getSearchView: ->
      new Views.Search

    getLayout: ->
      new Views.Layout

    search: (searchTerm) ->
      @listBooks @collection
      AppBus.vent.trigger 'search:term', searchTerm

    defaultSearch: ->
      #console.log "APP:Booklist>> API.defaultsearch"
      @search books.previousSearch or @defaultTerm

      
  module.exports = Controller
  
