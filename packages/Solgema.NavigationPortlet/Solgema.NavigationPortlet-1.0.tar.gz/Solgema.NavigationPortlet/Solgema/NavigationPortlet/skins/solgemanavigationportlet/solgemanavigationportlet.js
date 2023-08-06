function initjScrollPane(portlet) {
    var item = $(portlet).find('dl.portletNavigationTree dd.portletItem');
    item.css({'height': 'auto', 'position':'relative'});
    var maxHeight = $(portlet).css('max-height');
    if (maxHeight) {
        var navTreeMaxHeight = maxHeight.replace('px', '');
    } else {
        var navTreeMaxHeight = 600;
    }
    if ( item.height() > navTreeMaxHeight ) {
        item.css({'height': navTreeMaxHeight+'px', 'position':'relative'});
        item.jScrollPane();
        var container = $(portlet).find('.jspContainer');
        container.css('height', navTreeMaxHeight+'px');
        var current = $(portlet).find('dl.portletNavigationTree dd.portletItem a.navTreeCurrentNode');
        if ( current.length!=0 ) {
            $(portlet).find('dl.portletNavigationTree dd.portletItem').data('jsp').scrollToElement(current, true);
        }
    }
};

function updateScrollPane() {
    var portlet = $(this).parents('.SolgemaNavigationPortlet.useScrollPane');
    var item = $(portlet).find('dl.portletNavigationTree dd.portletItem');
    item.css({'height': 'auto', 'position':'relative'});
    var maxHeight = $(portlet).css('max-height');
    if (maxHeight) {
        var navTreeMaxHeight = maxHeight.replace('px', '');
    } else {
        var navTreeMaxHeight = 600;
    }
    if ( item.height() > navTreeMaxHeight ) item.css({'height': navTreeMaxHeight+'px', 'position':'relative'});
    var container = $(portlet).find('.jspContainer');
    if (container.length==0) {
        initjScrollPane(portlet);
        var jspAPI = $(portlet).find('dl.portletNavigationTree dd.portletItem').data('jsp');
    } else {
        var jspAPI = $(portlet).find('dl.portletNavigationTree dd.portletItem').data('jsp');
        if (jspAPI) jspAPI.reinitialise();
    }
    if ( item.height() > navTreeMaxHeight ) {
        container.css('height', navTreeMaxHeight+'px');
    } else {
        container.css('height', 'auto');
    }
    if (jspAPI) jspAPI.scrollToElement($(this), true);
};

function toggleNavtree(portlet, link, container) {
    if (container.hasClass('navTreeClosed')) {
        container.find('ul:first').slideToggle(400, updateScrollPane);
        container.removeClass('navTreeClosed').addClass('navTreeOpen');
        link.removeClass('navTreeClosed').addClass('navTreeOpen');
        var item = $(portlet).find('dl.portletNavigationTree dd.portletItem');
    } else {
        container.find('ul:first').slideToggle(400, updateScrollPane);
        container.removeClass('navTreeOpen').addClass('navTreeClosed');
        link.removeClass('navTreeOpen').addClass('navTreeClosed');
    }
};

function navtreeCollapsible(event) {
    if (event.which = 1) {
        if ( event.pageX > $(this).find('span:last').offset().left ) return true;
        event.preventDefault();
        var portletWrapper = $(this).parents('div.portletWrapper:first');
        var portlet = $(this).parents('div.SolgemaNavigationPortlet:first');
        var portletDL = $(this).parents('dl:first');
        var classes = portletWrapper.attr('class').split(' ');
        for (i = 0; i < classes.length; i++) {
            if ( classes[i].match('kssattr-portlethash-') ) var navTreeHash = classes[i].replace('kssattr-portlethash-', '');
        }
        if (portletWrapper.attr('data-portlethash')!== undefined) {
            var navTreeHash = portletWrapper.attr('data-portlethash');
        }
        var link = $(this);
        var container = $(this).parents('li.navTreeFolderish:first');
        if (container.length==0) return true;
        var innercontainer = $(this).parents('.outer_section:first');
        var content = innercontainer.children('ul.navTree:first');
        if (content.length==0) {
            $('#kss-spinner').show();
            var classes = $(this).attr('class').split(' ');
            for (i = 0; i < classes.length; i++) {
                if ( classes[i].match('navtreepath-') ) var navTreePath = classes[i].replace('navtreepath-', '');
                if ( classes[i].match('navtreelevel-') ) var navTreeLevel = classes[i].replace('navtreelevel-', '');
            }

            $.get("@@navTreeItem", { portlethash: navTreeHash, navtreepath: navTreePath, navtreelevel: navTreeLevel },
                function (data) {
                    if (data) {
                        innercontainer.append(data);
                        innercontainer.find('a.navTreeText').unbind('click');
                        if ($(portletDL).hasClass('contextMenuEnabled')) {
                            try {
                                innercontainer.find('a.navTreeText').bind("contextmenu", openContextualContentMenu);
                            } catch(err) {}
                        }
                        innercontainer.find('a.navTreeText').click(navtreeCollapsible).end().each(function() {
                            var container = $(this).parents('li.navTreeFolderish:first');
                            var state = container.hasClass('navTreeClosed') ? 'collapsed' : 'expanded';
                            if (state =='collapsed') container.find('ul').css('display','none');
                            toggleNavtree(portlet, link, container);
                            $('#kss-spinner').css('display','none');
                        });
                    } else {
                        if (container.hasClass('navTreeClosed')) {
                            container.removeClass('navTreeClosed').addClass('navTreeOpen');
                            link.removeClass('navTreeClosed').addClass('navTreeOpen');
                        } else {
                            container.removeClass('navTreeOpen').addClass('navTreeClosed');
                            link.removeClass('navTreeOpen').addClass('navTreeClosed');
                        }
                    $('#kss-spinner').css('display','none');
                    }
                }
            );
        } else {
            toggleNavtree(portlet, link, container);
        }
    } else if (event.which = 3) {
        return false;
        $('a.navTreeText').removeClass('selected');
        $(this).addClass('selected');
    }
};

function activateNavtreeCollapsibles() {
    var portlet = $('.SolgemaNavigationPortlet.useScrollPane');
    initjScrollPane(portlet);
    $('.SolgemaNavigationPortlet.useScrollPane dl.portletNavigationTree').addClass('javaNavTree');
    $('.SolgemaNavigationPortlet.useScrollPane li.navTreeFolderish').find('a.navTreeText:first').click(navtreeCollapsible).end().each(function() {
        var container = $(this).parents('li.navTreeFolderish:first');
        var state = container.hasClass('navTreeClosed') ?
                     'collapsed' : 'expanded';
        if (state =='collapsed') container.find('ul').css('display','none');

    });
};

$(activateNavtreeCollapsibles);

