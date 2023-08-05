# Third party libraries

These are the dependencies of various wq.app modules as well as some other useful libraries.  Most of these have been patched to support better integration as AMD modules.

## Library versions

Library                 |  Version  |  Notes
------------------------| --------- | -------------------------------------------
[d3.js]                 |    3.1.6  |  wrapped as AMD module
[es5-shim.js]           |   2.0.11  |  no changes
[highlight.js]          |  b26a4c6  |  tools/build.py -n -tamd css javascript markdown python scss 
[jquery]                |    1.9.1  |  patched to define anonymous AMD module
[jquery.mobile]         |    1.3.1  |  custom deps to ensure router loads first
[jquery.mobile.router]  |  570d7de  |  [#76]; patched with relative jQuery dependency
[jquery.validate]       |   1.11.0  |  wrapped as AMD module
[leaflet]               |  aae54a3  |  patched to define anonymous AMD module<br>commented out disableClickPropagation in Popup._initLayout
[leaflet.markercluster] |  6fda9a2  |  wrapped as AMD module (returns modified Leaflet object)
[marked]                |    0.2.8  |  no changes
[mustache.js]           |    0.7.2  |  no changes
[proj4js]               |    1.1.0  |  wrapped as AMD module
[proj4leaflet]          |  f4f5b6d  |  wrapped as AMD module (returns modified Leaflet object)
[requirejs], [r.js]     |    2.1.6  |  no changes; r.js is in /util

[d3.js]:                 https://github.com/mbostock/d3
[es5-shim.js]:           https://github.com/kriskowal/es5-shim
[highlight.js]:          https://github.com/isagalaev/highlight.js
[jquery]:                https://github.com/jquery/jquery
[jquery.mobile]:         https://github.com/jquery/jquery-mobile
[jquery.mobile.router]:  https://github.com/azicchetti/jquerymobile-router
[#76]:                   https://github.com/azicchetti/jquerymobile-router/pull/76
[jquery.validate]:       https://github.com/jzaefferer/jquery-validation
[leaflet]:               https://github.com/Leaflet/Leaflet
[leaflet.markercluster]: https://github.com/Leaflet/Leaflet.markercluster
[marked]:                https://github.com/chjj/marked
[mustache.js]:           https://github.com/janl/mustache.js
[proj4js]:               http://trac.osgeo.org/proj4js/
[proj4leaflet]:          https://github.com/kartena/Proj4Leaflet
[requirejs]:             https://github.com/jrburke/requirejs
[r.js]:                  https://github.com/jrburke/r.js
