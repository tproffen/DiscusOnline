// Some validation routines and other helpers

function valuevalidation(field, min, max, def, alertbox, datatype)
{
  if (isNaN(field.value) || field.value < min || field.value > max) {
    field.value=def; 
    if (alertbox!="") {alert(alertbox);} 
    return false;
  } else {
    return true;
  }
}
