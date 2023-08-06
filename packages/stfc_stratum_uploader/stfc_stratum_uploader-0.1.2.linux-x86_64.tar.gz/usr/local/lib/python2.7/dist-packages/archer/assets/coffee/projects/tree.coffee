(->
  collapse = undefined
  expand = undefined
  collapse = (that, children, speed) ->
    if speed is `undefined`
      children.hide "fast"
    else
      children.hide()
    $(that).attr("title", "Expand this branch").find(" > i").addClass("icon-folder-close").removeClass "icon-folder-open"

  expand = (that, children) ->
    children.show "fast"
    $(that).attr("title", "Collapse this branch").find(" > i").addClass("icon-folder-open").removeClass "icon-folder-close"

  $ ->
    $(".tree li:has(ul)").addClass("parent_li").find(" > span.folder > span.name").attr "title", "Collapse this branch"
    $(".tree li.parent_li > span.folder").on "click", (e) ->
      children = undefined
      that = undefined
      children = $(this).parent("li.parent_li").find(" > ul > li")
      that = $(this).find(" > span.name")
      if children.is(":visible")
        collapse that, children
      else
        expand that, children
      e.stopPropagation()

    $(".tree a.collapse_all").on "click", (e) ->
      $(".tree li.parent_li > ul > li").hide()
      $(".tree li.parent_li > span.folder > span.name").attr("title", "Expand this branch").find(" > i").addClass("icon-folder-close").removeClass "icon-folder-open"

    $(".tree a.expand_all").on "click", (e) ->
      $(".tree li.parent_li > ul > li").show()
      $(".tree li.parent_li > span.folder > span.name").attr("title", "Collapse this branch").find(" > i").addClass("icon-folder-open").removeClass "icon-folder-close"

    $(".tree li.parent_li > span.folder > span.actions").on "click", (e) ->
      e.stopPropagation()

    $(".tree li.parent_li > ul > li").hide()
    $(".tree").show()

).call this
