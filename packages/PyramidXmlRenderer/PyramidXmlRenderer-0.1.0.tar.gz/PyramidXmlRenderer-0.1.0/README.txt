pyramid_xml_renderer
====================

pyramid_xml_renderer gives the ability to convert structures to xml string (serializers.dumps)
and contains class XML (__init__.py) that can be used in pyramid framework to render structures to xml page
Typical usage in Pyramid (__init__.py of your app) looks like this::

    #!/usr/bin/env python

    from xml_renderer import XML
    config.add_renderer('your_url_to_serve', XML())
