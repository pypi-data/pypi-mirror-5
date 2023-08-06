(function() {
  (function() {
    var collapse, expand;
    collapse = void 0;
    expand = void 0;
    collapse = function(that, children, speed) {
      if (speed === undefined) {
        children.hide("fast");
      } else {
        children.hide();
      }
      return $(that).attr("title", "Expand this branch").find(" > i").addClass("icon-folder-close").removeClass("icon-folder-open");
    };
    expand = function(that, children) {
      children.show("fast");
      return $(that).attr("title", "Collapse this branch").find(" > i").addClass("icon-folder-open").removeClass("icon-folder-close");
    };
    return $(function() {
      $(".tree li:has(ul)").addClass("parent_li").find(" > span.folder > span.name").attr("title", "Collapse this branch");
      $(".tree li.parent_li > span.folder").on("click", function(e) {
        var children, that;
        children = void 0;
        that = void 0;
        children = $(this).parent("li.parent_li").find(" > ul > li");
        that = $(this).find(" > span.name");
        if (children.is(":visible")) {
          collapse(that, children);
        } else {
          expand(that, children);
        }
        return e.stopPropagation();
      });
      $(".tree a.collapse_all").on("click", function(e) {
        $(".tree li.parent_li > ul > li").hide();
        return $(".tree li.parent_li > span.folder > span.name").attr("title", "Expand this branch").find(" > i").addClass("icon-folder-close").removeClass("icon-folder-open");
      });
      $(".tree a.expand_all").on("click", function(e) {
        $(".tree li.parent_li > ul > li").show();
        return $(".tree li.parent_li > span.folder > span.name").attr("title", "Collapse this branch").find(" > i").addClass("icon-folder-open").removeClass("icon-folder-close");
      });
      $(".tree li.parent_li > span.folder > span.actions").on("click", function(e) {
        return e.stopPropagation();
      });
      $(".tree li.parent_li > ul > li").hide();
      return $(".tree").show();
    });
  }).call(this);

}).call(this);
