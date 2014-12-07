# https://github.com/scottaj/marionette-form-view-demo
# 
define (require, exports, module) ->
  _ = require 'underscore'
  Backbone = require 'backbone'
  Marionette = require 'marionette'
  Masonry = require 'masonry'
  imagesLoaded = require 'imagesloaded'

  class PageableView extends Backbone.Marionette.CompositeView
    keycode_prev: 65
    keycode_next: 90
    keycommands: () ->
      prev: @keycode_prev
      next: @keycode_next

    handle_key_command: (command) ->
      if command in ['prev', 'next']
        @get_another_page command

    keydownHandler: (event_object) =>
      for key, value of @keycommands()
        if event_object.keyCode == value
          @handle_key_command key
          
    onDomRefresh: () ->
      window.pview = @
      $('html').keydown @keydownHandler
      @masonry = new Masonry @ui.container.selector,
        gutter: @layoutGutter || 2
        isInitLayout: false
        itemSelector: @itemSelector || '.item'
        columnWidth: @columnWidth || 100
      @set_layout()

    onBeforeDestroy: () ->
      #console.log "Remove @keydownHandler" + @keydownHandler
      $('html').unbind 'keydown', @keydownHandler
      
    set_layout: ->
      @ui.container.show()
      @masonry.reloadItems()
      @masonry.layout()
      @ui.total_records?.text "#{@collection.state.totalRecords} results"
      @ui.pagenumber?.text "Page #{@collection.state.currentPage}"
      
      @set_pagination_buttons()
      
    set_pagination_buttons: ->
      if @collection.state.currentPage == @collection.state.firstPage
        @ui.prev_page_button.hide()
      else
        @ui.prev_page_button.show()
      if @collection.state.currentPage == @collection.state.lastPage
        @ui.next_page_button.hide()
      else
        @ui.next_page_button.show()
      if @collection.state.totalRecords <= @collection.state.pageSize
        @ui.next_page_button.hide()
        

    _update_hashtable: (hashtable, basehash) ->
      hashtable = if hashtable then hashtable else {}
      for key of basehash
        if key not of hashtable
          hashtable[key] = basehash[key]
      return hashtable
      
    _base_events:
      'click @ui.next_page_button': 'get_next_page'
      'click @ui.prev_page_button': 'get_prev_page'
      
    events: (eventhash) ->
      @_update_hashtable eventhash, @_base_events

    _baseui:
      next_page_button: '#next-page-button'
      prev_page_button: '#prev-page-button'
      total_records: '#total-records'

    ui: (uihash) ->
      @_update_hashtable uihash, @_baseui
      
    get_another_page: (direction) ->
      @ui.container.hide()
      switch direction
        when 'prev' then response = @collection.getPreviousPage()
        when 'next' then response = @collection.getNextPage()
        else response = null
      if response
        response.done =>
          @set_layout()

    get_next_page: () ->
      @get_another_page 'next'

    get_prev_page: () ->
      @get_another_page 'prev'
      
  module.exports = PageableView
  
  
