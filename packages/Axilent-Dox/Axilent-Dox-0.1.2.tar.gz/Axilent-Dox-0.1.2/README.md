Dox
===

Markdown-oriented content authoring for Axilent.

Basic Idea
----

Installation

	pip install Axilent-Dox


Initialization

	cd mydocs
	dox init --library-key=abc123 --project=My\ Project --content-type=Article --body-field=body 
	
Post Content

	touch "Hello World" > hello.md
	dox up

Update Content
	
	touch "Yo, whazzzup" > hello.md
	dox up
	
Known Limitations
---

* Only one content type supported.
* S3 Asset Fields not supported.
* Due to the limitations of the Markdown parser, only the ASCII character set is supported.

Other TODOs
---

Dox depends on [Sharrock](http://github.com/Axilent/sharrock), which currently requires a full installation of Django.  However Dox only really needs the Sharrock client – not the server capabilities.  In the future we'll package up a client-only version of Sharrock, and Dox will use that, negating the need for a full Django install.

