js.tableselect
**************

Introduction
============

This library provides a widget which you can use to transform a multiselect
to a searchable sortable table which has selectable rows.
Packaged for `fanstatic`_.

.. _`fanstatic`: http://fanstatic.org


Create and use
==============

Once included, simply call $(select_element).tableselect(); to transform
your simple multiselect element to a searchable table select widget containing
values and labels. Click on rows to select them.

aoColumn and aaData values need to be provided in the global "tableselect"
object with the Id of the original multiselect as key. First column must
contain the values of the options of the original multiselect.
In the example below this column is hidden:

   tableselect['my_multiselect']['aoColumns'] = [
        {"bVisible": false, "bSearchable": false},
        {"sTitle": "Title", "bSearchable": true},
        {"sTitle": "Description", "bSearchable": true}];

   tableselect['my_multiselect']['aaData'] = [
         ["value_of_first_option", "title", "description"],
         ["value_of_second_option", "foo", "bar"]] ;

  $('#my_multiselect').tableselect();
