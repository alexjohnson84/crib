//toggle functionality for discard section
var classHighlight = 'highlight';
var discard = $('.discard').click(function(e) {
  e.preventDefault();
  currentClass = $(this).get(0).className;
  if (currentClass == "discard card highlight"){
    $(this).removeClass(classHighlight);
  } else {
    $(this).addClass(classHighlight);
  }
});

function get_selection(){
  var discard_obj = document.getElementsByClassName("discard card highlight");
  console.log(discard_obj);
  var selected_d = []
  for (i = 0; i < discard_obj.length; i++) {
        selected_d.push(discard_obj[i].id);
      }
  return selected_d
}


function validate_input_length(n){
  var selected_d = get_selection()
  if (selected_d.length != n){
    alrt_msg = "Please only select ";
    alert(alrt_msg.concat(String(n), " cards"));
    return false;
  } else {
    document.getElementById('discard_selection').value = selected_d;
    return true;
  }
}

function validate_move(legal_moves){
  console.log(legal_moves);

  if (legal_moves == null) {
    return true;
  } else {
    var move = get_selection()[0]
    if (legal_moves.indexOf(move) >= 0){
      return true;
    } else {
      alert('Illegal Move')
      return false;
    }
  }
}

function validate_form(n, legal_moves){
  var vil = validate_input_length(n);
  var vm = validate_move(legal_moves);
  return vil && vm;
}


//submit function
// function submit_discards(n){
//   var selected_d = [];
//   var x = document.getElementById("myhand");
//   // pull highlighted classes
//   var y = x.getElementsByClassName("discard highlight");
//   if (y.length == n){
//     var i;
//     for (i = 0; i < y.length; i++) {
//       selected_d.push(y[i].title);
//     }
//     //fill form with vals in order to post
//     document.getElementById('discard_selection').value = selected_d;
//     console.log(document.getElementById('discard_selection'))
//     document.getElementById('card_acts').submit()
//     console.log(document.getElementById('discard_selection').value)
//     //remove highlight from class
//     $(".highlight").removeClass("highlight");
//   } else {
//     //alert for not passing in 2 cards
//     alrt_msg = "Please only select ";
//     alert(alrt_msg.concat(String(n), " cards"));
//   }
// }
