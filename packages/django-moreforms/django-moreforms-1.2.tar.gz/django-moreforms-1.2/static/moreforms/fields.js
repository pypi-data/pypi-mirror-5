
/**
 * Main javascript file for interactive fields.
 * !! IMPORTANT !! Ensure JQuery is included.
 **/

/** Render a single choice.
 * Renders an option tag. The first element of choice is the HTML value. The
 * second element is the human-redable label. The function will compare the
 * choice's value against the FancyRadioSelect's value to appropriately
 * "select" the widget.
 * 
 * @param choice A pair containing a choice value and a choice label.
 * 
 * @return A rendered string representing an "option" tag.
 **/
function renderChoice(choice){
    val = choice[0]
    label = choice[1]
    
    if (this.value == choice)
        return "\t\t<td class=\"fancy-selected\" id=\"" + val  +"\"> " +
            label + "</td>\n";
    return "\t\t<td id=\"" + val  +"\"> " + label + "</td>\n";
}

/** Render the associated FancyRadioSelect
 **/
function render(){
    var doc = "<table class=\"fancy-select\" id=\"fancy-" + self.name +
        "\" >\n" + "   <tr>\n";
    
    for (var i = 0; i < this.choices.length; ++i)
        doc += renderChoice(this.choices[i])
        
    doc += "    </tr>\n" + "</table>";
}

function FancyRadioSelect(name, value, choices, maxSelect=1){
    this.name = name;
    this.value = value;
    this.choices = choices;
    this.maxSelect = maxSelect;
    
    // methods.
    this.render = render;
    this.renderChoice = renderChoice;
    
    // JQuery Callbacks
    
    var widget = this;

    $(document).ready(function(){
        $('table.fancy-select tr td').click(function(){
            
            var parentTable = $(this).closest('table');
            var selectedWidgets = parentTable.children('td.fancy-selected');
            var count = selectedWidgets.count();
            
            if (widget.maxSelect == 1){
                $('table.fancy-select tr td').removeClass('fancy-selected');
                $(this).addClass('fancy-selected');
            }else if (count < widget.maxSelect){
                $(this).toggleClass('fancy-selected');
            }else { //if (count >= widget.maxSelect)
                $(this).removeClass('fancy-selected');
            }
            
            selectedWidgets = parentTable.children('td.fancy-selected');
            
            var values = "";
            for (int i = 0; i < selectedWidgets.length; ++i)
                values += selectedWidgets.val() + ",";
            
            $(this).closest('input[type=hidden]').val(values);
            
            console.log('Setting hidden input to value: "' + values + '"')
            
        });
    });
}