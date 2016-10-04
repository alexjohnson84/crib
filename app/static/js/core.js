//toggle functionality for discard section
var classHighlight = 'highlight';
var discard = $('.discard').click(function(e) {
  e.preventDefault();
  currentClass = $(this).get(0).className;
  if (currentClass == "discard card highlight" ||
  currentClass == "discard card best highlight" ||
  currentClass == "discard card highlight best"){
    $(this).removeClass(classHighlight);
  } else {
    $(this).addClass(classHighlight);
  }
});

function get_selection(){
  var discard_obj = document.getElementsByClassName("discard card highlight");
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
  var phase = document.getElementById('game-phase').innerHTML.substring(7)
  if (['Turn', 'Pegging'].indexOf(phase) >= 0){
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
}


function validate_form(n, legal_moves){
  var vil = validate_input_length(n);
  var vm = validate_move(legal_moves);
  return vil && vm;
}

function find_highest_match(move_scores){
  max_value = 0;
  best_selection = move_scores[1][0];
  for (i = 0; i < move_scores.length; i++) {
          if(move_scores[i][1] > max_value){
          	max_value = move_scores[i][1];
            best_selection = move_scores[i][0];
          }
       }
  return best_selection;
}

function compare_selection_to_response(move_scores){
  var user_move = get_selection();
  var best_move = find_highest_match(move_scores);
  console.log(best_move);
  console.log(user_move);
  var classBest = ' best';
  for(i=0; i < best_move.length; i++){
    var best_card = document.getElementById(best_move[i]);
    best_card.className += classBest;
  }
}
