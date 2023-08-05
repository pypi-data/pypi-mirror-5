#-*- coding: utf-8 -*-

from copy import deepcopy

from django.conf import settings


WYSIHTML5_EDITOR = getattr(settings, "WYSIHTML5_EDITOR", {})
WYSIHTML5_TOOLBAR = getattr(settings, "WYSIHTML5_TOOLBAR", {})

EDITOR_CONF = {
    # Give the editor a name, the name will also be set as class 
    # name on the iframe and on the iframe's body
    'name': 'null',
    # Whether the editor should look like the textarea (by adopting styles)
    'style': 'true',
    # Id of the toolbar element, pass falsey value if you don't want 
    # any toolbar logic
    'toolbar': 'null',
    # Whether urls, entered by the user should automatically become 
    # clickable-links
    'autoLink': 'true',
    # Object which includes parser rules (set this to 
    # examples/rules/spec.json or your own spec, otherwise only span 
    # tags are allowed!)
    'parserRules': 'wysihtml5ParserRules',
    # Parser method to use when the user inserts content via copy & paste
    'parser': 'wysihtml5.dom.parse || Prototype.K',
    # Class name which should be set on the contentEditable element in 
    # the created sandbox iframe, can be styled via the 'stylesheets' option
    'composerClassName': '"wysihtml5-editor"',
    # Class name to add to the body when the wysihtml5 editor is supported
    'bodyClassName': '"wysihtml5-supported"',
    # By default wysihtml5 will insert <br> for line breaks, set this to
    # false to use <p>
    'useLineBreaks': 'true',
    # Array (or single string) of stylesheet urls to be loaded in the 
    # editor's iframe
    'stylesheets': '["%s"]' % (settings.STATIC_URL + 
                               "wysihtml5/css/stylesheet.css"),
    # Placeholder text to use, defaults to the placeholder attribute 
    # on the textarea element
    'placeholderText': 'null',
    # Whether the composer should allow the user to manually resize 
    # images, tables etc.
    'allowObjectResizing': 'true',
    # Whether the rich text editor should be rendered on touch devices 
    # (wysihtml5 >= 0.3.0 comes with basic support for iOS 5)
    'supportTouchDevices': 'true'
}

TOOLBAR_CONF = {
    "formatBlockHeader": { 
        "active": True,
        "command_name": "formatBlock",
        "render_icon": "wysihtml5.widgets.render_formatBlockHeader_icon"
    },
    "formatBlockParagraph": { 
        "active": True,
        "command_name": "formatBlock",
        "render_icon": "wysihtml5.widgets.render_formatBlockParagraph_icon"
    },
    "bold": { 
        "active": True,
        "command_name": "bold",
        "render_icon": "wysihtml5.widgets.render_bold_icon"
    },
    "italic": { 
        "active": True,
        "command_name": "italic",
        "render_icon": "wysihtml5.widgets.render_italic_icon"
    },
    "underline": { 
        "active": True,
        "command_name": "underline",
        "render_icon": "wysihtml5.widgets.render_underline_icon"
    },
    "justifyLeft": { 
        "active": True,
        "command_name": "justifyLeft",
        "render_icon": "wysihtml5.widgets.render_justifyLeft_icon"
    },
    "justifyCenter": { 
        "active": True,
        "command_name": "justifyCenter",
        "render_icon": "wysihtml5.widgets.render_justifyCenter_icon"
    },
    "justifyRight": { 
        "active": True,
        "command_name": "justifyRight",
        "render_icon": "wysihtml5.widgets.render_justifyRight_icon"
    },
    "insertOrderedList": { 
        "active": True,
        "command_name": "insertOrderedList",
        "render_icon": "wysihtml5.widgets.render_insertOrderedList_icon"
    },
    "insertUnorderedList": { 
        "active": True,
        "command_name": "insertUnorderedList",
        "render_icon": "wysihtml5.widgets.render_insertUnorderedList_icon"
    },
    "insertImage": { 
        "active": True,
        "command_name": "insertImage",
        "render_icon": "wysihtml5.widgets.render_insertImage_icon",
        "render_dialog": "wysihtml5.widgets.render_insertImage_dialog"
    },
    "createLink": { 
        "active": True,
        "command_name": "createLink",
        "render_icon": "wysihtml5.widgets.render_createLink_icon",
        "render_dialog": "wysihtml5.widgets.render_createLink_dialog"
    },
    "insertHTML": { 
        "active": True,
        "command_name": "insertHTML",
        "command_value": "<blockquote>quote</blockquote>",
        "render_icon": "wysihtml5.widgets.render_insertHTML_icon"
    },
    "foreColor": { 
        "active": True,
        "command_name": "foreColor",
        "render_icon": "wysihtml5.widgets.render_foreColor_icon"
    },
    "changeView": { 
        "active": True,
        "command_name": "change_view",
        "render_icon": "wysihtml5.widgets.render_changeView_icon"
    },
}


def initialize_editor_conf():
    for key in WYSIHTML5_EDITOR:
        if key in EDITOR_CONF:
            EDITOR_CONF[key] = WYSIHTML5_EDITOR[key]


def initialize_toolbar_conf():
    for key in WYSIHTML5_TOOLBAR:
        if key in TOOLBAR_CONF:
            for subkey in WYSIHTML5_TOOLBAR[key]:
                TOOLBAR_CONF[key][subkey] = WYSIHTML5_TOOLBAR[key][subkey]
        else:
            TOOLBAR_CONF[key] = WYSIHTML5_TOOLBAR[key]

initialize_editor_conf()
initialize_toolbar_conf()
