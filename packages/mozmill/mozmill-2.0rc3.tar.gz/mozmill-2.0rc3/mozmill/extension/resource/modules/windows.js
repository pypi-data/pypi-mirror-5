/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, you can obtain one at http://mozilla.org/MPL/2.0/. */

var EXPORTED_SYMBOLS = ["init", "map"];

const Cc = Components.classes;
const Ci = Components.interfaces;
const Cu = Components.utils;

// imports
var utils = {}; Cu.import('resource://mozmill/stdlib/utils.js', utils);

var uuidgen = Cc["@mozilla.org/uuid-generator;1"].getService(Ci.nsIUUIDGenerator);

/**
 * The window map is used to store information about the current state of
 * open windows, e.g. loaded state
 */
var map = {
  _windows : { },

  /**
   * Check if a given window id is contained in the map of windows
   *
   * @param {Number} aWindowId
   *        Outer ID of the window to check.
   * @returns {Boolean} True if the window is part of the map, otherwise false.
   */
  contains : function (aWindowId) {
    return (aWindowId in this._windows);
  },

  /**
   * Retrieve the value of the specified window's property.
   *
   * @param {Number} aWindowId
   *        Outer ID of the window to check.
   * @param {String} aProperty
   *        Property to retrieve the value from
   * @return {Object} Value of the window's property
   */
  getValue : function (aWindowId, aProperty) {
    if (!this.contains(aWindowId)) {
      return undefined;
    } else {
      var win = this._windows[aWindowId];

      return (aProperty in win) ? win[aProperty]
        : undefined;
    }
  },

  /**
   * Remove the entry for a given window
   *
   * @param {Number} aWindowId
   *        Outer ID of the window to check.
   */
  remove : function (aWindowId) {
    if (this.contains(aWindowId))
      delete this._windows[aWindowId];
    //dump("* current map: " + JSON.stringify(this._windows) + "\n");
  },

  /**
   * Update the property value of a given window
   *
   * @param {Number} aWindowId
   *        Outer ID of the window to check.
   * @param {String} aProperty
   *        Property to update the value for
   * @param {Object}
   *        Value to set
   */
  update : function (aWindowId, aProperty, aValue) {
    if (!this.contains(aWindowId))
      this._windows[aWindowId] = { };

    this._windows[aWindowId][aProperty] = aValue;
    //dump("* current map: " + JSON.stringify(this._windows) + "\n");
  },

  /**
   * Update the internal loaded state of the given content window. To identify
   * an active (re)load action we make use of an uuid.
   *
   * @param {Window} aWindow - The window to update
   * @param {Boolean} aIsLoaded - Has the window been loaded
   */
  updatePageLoadStatus : function (aWindow, aIsLoaded) {
    var id = utils.getWindowId(aWindow);
    this.update(id, "loaded", aIsLoaded);

    var uuid = this.getValue(id, "id_load_in_transition");

    // If no uuid has been set yet or when the page gets unloaded create a new id
    if (!uuid || !aIsLoaded) {
      uuid = uuidgen.generateUUID();
      this.update(id, "id_load_in_transition", uuid);
    }

    // dump("*** Page status updated: id=" + id + ", loaded=" + aIsLoaded + ", load_uuid=" + uuid + "\n");
  },

  /**
   * This method only applies to content windows, where we have to check if it has
   * been successfully loaded or reloaded. An uuid allows us to wait for the next
   * load action triggered by e.g. controller.open().
   *
   * @param {Window} aWindow - The content window to check
   *
   * @returns {Boolean} True if the content window has been loaded
   */
  hasPageLoaded : function (aWindow) {
    var id = utils.getWindowId(aWindow);

    var load_current = this.getValue(id, "id_load_in_transition");
    var load_handled = this.getValue(id, "id_load_handled");

    var isLoaded = this.contains(id) && this.getValue(id, "loaded") &&
                   (load_current !== load_handled);

    if (isLoaded) {
      // Backup the current uuid so we can check later if another page load happened.
      this.update(id, "id_load_handled", load_current);

      // dump("** Page has been finished loading: id=" + id + ", uuid=" + load_current + "\n");
    }

    return isLoaded;
  }
};


// Observer when a new top-level window is ready
var windowReadyObserver = {
  observe: function (aSubject, aTopic, aData) {
    attachEventListeners(aSubject);
  }
};


// Observer when a top-level window is closed
var windowCloseObserver = {
  observe: function (aSubject, aTopic, aData) {
    var id = utils.getWindowId(aSubject);
    map.remove(id);
    // dump("*** DOMWindow close event: id=" + id + "\n");
  }
};


/**
 * Attach event listeners
 *
 * @param {ChromeWindow} aWindow
 *        Window to attach listeners on.
 */
function attachEventListeners(aWindow) {
  // These are the event handlers
  var pageShowHandler = function (aEvent) {
    var doc = aEvent.originalTarget;

    // Only update the flag if we have a document as target
    // see https://bugzilla.mozilla.org/show_bug.cgi?id=690829
    if ("defaultView" in doc) {
      // dump("*** pageshow event: baseURI=" + doc.baseURI + "\n");
      map.updatePageLoadStatus(doc.defaultView, true);
    }

    // We need to add/remove the unload/pagehide event listeners to preserve caching.
    aWindow.getBrowser().addEventListener("beforeunload", beforeUnloadHandler, true);
    aWindow.getBrowser().addEventListener("pagehide", pageHideHandler, true);
  };

  var DOMContentLoadedHandler = function (aEvent) {
    var doc = aEvent.originalTarget;

    var errorRegex = /about:.+(error)|(blocked)\?/;
    if (errorRegex.exec(doc.baseURI)) {
      // Wait about 1s to be sure the DOM is ready
      utils.sleep(1000);

      // Only update the flag if we have a document as target
      if ("defaultView" in doc) {
        // dump("*** DOMContentLoaded event: baseURI=" + doc.baseURI + "\n");
        map.updatePageLoadStatus(doc.defaultView, true);
      }

      // We need to add/remove the unload event listener to preserve caching.
      aWindow.getBrowser().addEventListener("beforeunload", beforeUnloadHandler, true);
    }
  };

  // beforeunload is still needed because pagehide doesn't fire before the page is unloaded.
  // still use pagehide for cases when beforeunload doesn't get fired
  var beforeUnloadHandler = function (aEvent) {
    var doc = aEvent.originalTarget;

    // Only update the flag if we have a document as target
    if ("defaultView" in doc) {
      // dump("*** beforeunload event: baseURI=" + doc.baseURI + "\n");
      map.updatePageLoadStatus(doc.defaultView, false);
    }

    aWindow.getBrowser().removeEventListener("beforeunload", beforeUnloadHandler, true);
  };

  var pageHideHandler = function (aEvent) {
    // If event.persisted is false, the beforeUnloadHandler should fire
    // and there is no need for this event handler.
    if (aEvent.persisted) {
      var doc = aEvent.originalTarget;

      // Only update the flag if we have a document as target
      if ("defaultView" in doc) {
        // dump("*** pagehide event: baseURI=" + doc.baseURI + "\n");
        map.updatePageLoadStatus(doc.defaultView, false);
      }

      aWindow.getBrowser().removeEventListener("beforeunload", beforeUnloadHandler, true);
    }
  };

  var onWindowLoaded = function (aEvent) {
    // dump("*** DOMWindow load event: baseURI=" + aWindow.document.baseURI + "\n");
    map.update(utils.getWindowId(aWindow), "loaded", true);

    // Check if we have a browser window. If that's the case attach handlers for tabs
    var browser = ("getBrowser" in aWindow) ? aWindow.getBrowser() : null;
    if (browser) {
      // Note: Error pages will never fire a "pageshow" event. For those we
      // have to wait for the "DOMContentLoaded" event. That's the final state.
      // Error pages will always have a baseURI starting with
      // "about:" followed by "error" or "blocked".
      browser.addEventListener("DOMContentLoaded", DOMContentLoadedHandler, true);

      // Page is ready
      browser.addEventListener("pageshow", pageShowHandler, true);

      // Leave page (use caching)
      browser.addEventListener("pagehide", pageHideHandler, true);
    }
  };

  // If the window has already been finished loading, call the load handler
  // directly. Otherwise attach it to the current window.
  if (aWindow.content) {
    onWindowLoaded();
  } else {
    aWindow.addEventListener("load", onWindowLoaded, false);
  }
}

function init() {
  // Activate observer for new top level windows
  var observerService = Cc["@mozilla.org/observer-service;1"].
                        getService(Ci.nsIObserverService);
  observerService.addObserver(windowReadyObserver, "toplevel-window-ready", false);
  observerService.addObserver(windowCloseObserver, "outer-window-destroyed", false);

  // Attach event listeners to all already open top-level windows
  var enumerator = Cc["@mozilla.org/appshell/window-mediator;1"].
                   getService(Ci.nsIWindowMediator).getEnumerator("");
  while (enumerator.hasMoreElements()) {
    var win = enumerator.getNext();
    attachEventListeners(win);

    // For top-level windows which are already open set the loaded state
    // to the current readyState. For slowly loading windows (like for debug
    // builds) it will be overwritten again by the onload listener later.
    var loaded = (win.document.readyState === 'complete');
    map.update(utils.getWindowId(win), "loaded", loaded);
  }
}
