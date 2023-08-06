# Purpose of Field Tree

This plugin is a wrapper for dynamic form rendering, and works even for users
that block scripts (gasp! I know!).

The most common form of the "I really need JavaScript for this" attitude is
dynamic form rendering, where one select box renders another select box and so
on. One example you may have encountered is the obligitory Country-State-City
select box.

This plugin makes it easy to render a form based on input. Plus, it works
without JavaScript! The plugin will automatically detect if JasvaScript is
turned off, and render a submit button for continuing.

Consequently, the form is resubmitted whether someone is using Javascript or no
Javascript. **Any developer using this plugin must plan accordingly.**

# Requirements

Since this is a Django plugin, obviously django must be installed. Besides that,
you must have jquery installed and linked within the page that uses FieldTree
in order to use the javascript functionality.

# Getting Started


1. You can install moreforms by typing

    $ pip install django-moreforms
    
in the command line.

2. Ensure that 'moreforms' is listed in INSTALLED_APPS in `settings.py`:

    INSTALLED_APPS = (
        ...
        'moreforms',
        ...
    )
    
3. Finally, to construct the FieldTree, do the following:

    from django import forms
    from moreforms import FieldTree as T, FieldLeaf as L
    
    class MyForm(forms.Form):
        name = forms.CharField(...)
        age = forms.IntegerField(...)
        ...
        
        # Every form with a FieldTree must have a delete_field method. I'll
        # explain later...
        def delete_field(self, name):
            del self.field[name]
        
        # Make sure to override the __init__ method.
        def __init__(self, *args, **kwargs):
        
            request = kwargs.pop('request', None) # Don't add request as an
                                                    #  argument itself.
                                                    
            super(MyForm, self).__init__(*args, **kwargs)
            
            tree = T(request, self,
                L(None, 'name', children=(
                    L('.*', 'age'),
                ))
            )
            
            tree.vacuum()
                
4. Within the django template you need to load the template tags:

    {% load moreforms %}
    
    {{ form.as_p }} {% auto_submit %}
    
`auto_submit` will render both the javascript and the non-script portions
of the FieldTree.
                
## What the code does.

`FieldTree` is, essentially a tree, where each leaf has a regular expression,
a name of a field, and (optionally) any children, which--in themselves--are
leaves.

The **regular expression** is what is expected from the parent's field. In
the above example, we want to render the 'age' field if the value of
'name' is posted. Note that the top-most leaf ('name') has `None` as the
regexp. This is becaue **the top-most leaf must have a None regexp.**

## That's it!

Now, just create the form in the view, taking care to pass in `request` as well.

    def my_view(request):
    
        form = MyForm(request)
        return render(request, 'some_page.html', {'form' : form})
        
# A Few Notes

## `delete_field` function.

Since a FieldTree cannot delete the fields on the passed-in form directly,
they must be deleted manually from the form. Basically you just need the lines
provided in the example.

## Default input value

If you want a default input value (e.g. automatically fill in the submitted
`name`), do the following in the form:

    class MyForm(forms.Form):
        ...
        def __init__(self, *args, **kwargs):
            ...
            super(...).__init__(...)
            ...
            self.initial = {'name' : ... }
            
This is standard for django forms, but just thought you'd like to know.

## You might want a note...

You might want a note preceeding the form to explain how the TreeField works.
