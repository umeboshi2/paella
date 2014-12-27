define (require, exports, module) ->
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  Masonry = require 'masonry'
  imagesLoaded = require 'imagesloaded'
      
  Models = require 'models'

  Templates = require 'bookstore/templates'
  AppBus = require 'bookstore/msgbus'
  
  FormView = require 'common/views/formview'
  { navigate_to_url } = require 'common/util'
    
  BaseEditPageView = require 'common/views/editor'
  BaseSideBarView = require 'common/views/sidebar'

  class FrontDoorMainView extends Backbone.Marionette.ItemView
    template: Templates.frontdoor_main

  class SideBarView extends BaseSideBarView
    
  class BookView extends Backbone.Marionette.ItemView
    template: Templates.book_view
    className: 'book'
    events:
      'click': ->
        AppBus.vent.trigger 'list:book:clicked', @model

  class BookList extends Backbone.Marionette.CompositeView
    template: Templates.booklist_view
    id: 'booklist'
    childView: BookView
    childViewContainer: 'div.books'
    events:
      scroll: 'loadmorebooks'

    #onRenderCollection: ->
    #  @set_image_layout()

        
    set_image_layout: ->
      #console.log 'set_image_layout called'
      items = $ '.book'
      #window.items = items
      container = 'div.books'
      #console.log "The items are #{items}"
      imagesLoaded items, =>
        #console.log "imagesLoaded for #{container} #{@masonry}"
        #console.log @masonry
        @masonry.addItems items
        @masonry.layout()

    set_layout: ->
      items = $ '.book'
      imagesLoaded items, =>
        @masonry.reloadItems()
        @masonry.layout()
        
    loadmorebooks: ->
      totalHeight = @.$("> div").height()
      scrollTop = @.$el.scrollTop() + @.$el.height()
      margin = 200
      #msg = "th:#{totalHeight},st:#{scrollTop},elheight:#{@.$el.height()}"
      #console.log msg
      if ((scrollTop + margin) >= totalHeight)
        #console.log "BOOKLIST: >>search"
        AppBus.vent.trigger "search:more"

    onDomRefresh: () ->
      msnry = new Masonry 'div.books',
        itemSelector: '.book'
        columnWidth: 5
        isInitLayout: false
        itemSelector: '.book'
      window.msnry = msnry
      @masonry = msnry

    onRenderCollection: ->
      #@set_image_layout()
      @set_layout()
      
      
  class BookLayout extends Backbone.Marionette.LayoutView
    template: Templates.bookstore_layout
    regions:
      search: '#searchBar'
      books: '#bookContainer'

  class SearchView extends Backbone.Marionette.ItemView
    el: '#searchBar'
    events:
      'change #searchTerm': 'search'

    initialize: ->
      $spinner = @.$('#spinner')
      AppBus.vent.on 'search:start', =>
        $spinner.fadeIn()
      AppBus.vent.on 'search:stop', =>
        $spinner.fadeOut()
      AppBus.vent.on 'search:term', (term) =>
        @.$('#searchTerm').val(term)

    search: ->
      searchTerm = @.$("#searchTerm").val().trim()
      #console.log "searchTerm change vent handled from SearchView: #{searchTerm}"
      if searchTerm.length > 0
        AppBus.vent.trigger "search:term", searchTerm
      else
        AppBus.vent.trigger "search:noSearchTerm"
      
  class BookDetailView extends Backbone.Marionette.ItemView
    template: Templates.book_detail_view
    className: 'modal bookdetail'

    # not used in this app
    modelEvents:
      "change:name" : -> console.log "name changed"

    events:
      "click #close-dialog" : ->
        console.log "book/list/BookDetailView >> close click"
        # this event is handled by the Mariionette.Region.Dialog
        # extension class >> see config(FIXME new location)
        @trigger "dialog:close"  
    



  module.exports =
    FrontDoorMainView: FrontDoorMainView
    SideBarView: SideBarView
    BookView: BookView
    BookList: BookList
    BookLayout: BookLayout
    SearchView: SearchView
    BookDetailView: BookDetailView
    
