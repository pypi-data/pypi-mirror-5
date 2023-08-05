Dox
===

Markdown-oriented content authoring for Axilent.

Basic Idea
----

Initialization

	cd mydocs
	dox init
	"Enter Axilent Library Key"
	187fee27efc843ed88d7b32b0f706811
	"Enter Axilent Project"
	myproject
	"Enter content type"
	Article
	"Enter name of body field."
	body
	"Dox Initialized"
	
Post Content

	touch "Hello World" > hello.md
	dox upload
	"Uploading..."
	"Added hello.md"
	"Done."

Update Content
	
	touch "Yo, whazzzup" > hello.md
	dox upload
	"Uploading..."
	"Updating hello.md"
	"Done"
	
Deleting Content
	
	rm hello.md
	dox upload
	"Uploading..."
	"Archiving hello.md"
	"Done"
	
Known Limitations
---

* Only one content type supported.
* S3 Asset Fields not supported.

Other TODOs
---

Dox depends on [Sharrock](http://github.com/Axilent/sharrock), which currently requires a full installation of Django.  However Dox only really needs the Sharrock client – not the server capabilities.  In the future we'll package up a client-only version of Sharrock, and Dox will use that, negating the need for a full Django install.

