Introduction
============

This is an add-on for `RedTurtle Video`__ product for Plone. Additional documentation can be found in the main product's page.

__ https://pypi.python.org/pypi/redturtle.video

Add this to your Plone installation for beeing able to use `MediaCore`__ video link as valid URLs for "Video link" content type.

__ http://mediacore.com/

In order to serve content from Mediacore you need to configure an adapter and specify the domain name.   
Is possible to add an adapter to your application in many way:

 - directly to the buildout section on a .cfg file (example below):
 - within a configure.zcml in collective.rtvideo.mediacore
 - within an other package which implements redturtle.video.interfaces.IRTRemoteVideo

::

 [instance]
 ...
 eggs =
     collective.rtvideo.mediacore
     ...

 zcml-additional =
     <configure xmlns="http://namespaces.zope.org/zope">
         <adapter for = "redturtle.video.interfaces.IRTRemoteVideo zope.publisher.interfaces.browser.IHTTPRequest"
             provides = "collective.rtvideo.mediacore.videoembedcode.IMediaCoreEmbedCode"
             factory = "collective.rtvideo.mediacore.videoembedcode.JWPlayerEmbedCode"
             name= "your.domain"/>
     </configure>

..

Note
----
This plugin alone is not enougth. 
Mediacore must provides a view to serve some information about media as JSON.
See `mediacore.mediainfo`__ package for more details.

__ https://pypi.python.org/pypi/mediacore.mediainfo/

