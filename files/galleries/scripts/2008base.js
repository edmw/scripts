/***************************************************************************
** Helper
****************************************************************************/

function $(id){
  if(arguments.length > 1){
    var i, l, elements = []
    
    for(i = 0, l = arguments.length; i < l; i++){
      elements.push($(arguments[i]))
    }
    
    return elements;
  }
  var element = id
  
  if(typeof id == 'string'){
    element = document.getElementById(id)
  }
  
  return element
}

/***************************************************************************
** DOM Helper
****************************************************************************/

function displayStyle(element, state){
  if(state == 0){
    element.style.display = "none";
  }
  else{
    element.style.display = "block";
  }
}