Pan
==============================================================================

A python command line tool with sane defaults for building academic articles 
from markdown using pandoc and (optionally) Stata.


Installation
--------------------

You will need to install pandoc first: http://johnmacfarlane.net/pandoc/installing.html

The install with pip::
	
	sudo pip install pan
	
Sudo is only needed to install for the system python to make the command line 
tool available everywhere; you can install in a virtualenv without sudo.





Output formats
------------------

rtf

html

plain

pdf (default)




Markdown header block options
------------------------------------


XXX 




Instructor-only content
------------------------------------

Sometimes presentations or worksheets will have content for instructors only 
(e.g. suggested answers). You can hide this content by wrapping it in a div tag with the `.instructor` class::

	<div class="instructor">Content for you only</div>
	
Then pass in the --instructor flag (or set it in the header block) when building to get the hidden stuff too.

Note: `.instructor` content is hidden by default.

	



Weaving documents with Stata
------------------------------------

Pan includes a Stata filter for pandoc to 'weave' documents with markdown, 
Stata code and LaTeX into pdfs. This means you can include a block like this in 
your markdown::

	~~~{.stata .run}
	di 2*2
	~~~
	
And see the following output in your pdf::

	. di 2*2
	4


If you want to hide some setup commands, add `>>>` after the comands you want hidden::

	~~~{.stata .run}
	use somedatafile
	>>>
	di "this text will not be shown because it does not follow the last >>>"
	>>>
	* but this will be shown
	describe
	~~~

Here, the loading command will not appear in the output. Only the block of code after the last `>>>` will be displayed.

You can also add a `.hide` class to the code block and the filter will run but not display results for the code. This is useful when generating graphs etc.  

Note exporting png or pdf will not work when running Stata in headless mode, so use .eps instead. Data will not persist between code blocks, so will need to be loaded each time, and intermediate steps stored in temporary files.




Referencing
------------------------------------

Include a file called `references.bib` somewhere in the folder hierarchy of your project
and pan will find it and pass to pandoc use it to generate a reference list. For example,
if you have a structure like this::

	references.bib
	studies
		clever_study
			article.markdown
			

The pan will pass the file references.bib from the top level when you build article.markdown.
See the `csl` header attribute below to change citation formats.


