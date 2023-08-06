CGI Image Thumbnailer
============================

*Author* Robert Sudwarts

For uploading files via web interface.

Basic scope of the problem
---------------------------

Functionality for:

  * uploading large files using buffered chunks
  * scaling down large images
  

Package Components
---------------------

    #. upload.writefile() accepts a FieldStorage instance and writes in
       buffered chunks to the specified directory.
    #. Image files can be written 'as is' or scaled to a specified size and
       [at the same time] as a thumbnail image of a specified size.
    #. A `Thumb` class to check for existence of thumbnail/create/delete etc


Change Log
------------

 * v.0.1.5 when scaling image to thumbnail image is given file extension .jpg 
           
 * v.0.1.4 added "Pillow>=2.0.0" as a dependency to setup.py.
           This package is required instead of PIL

 * v.0.1.3 added conditional 'scale' to writefile() so that this package can be used for all types of files (not just images)
