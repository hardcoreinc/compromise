$(function() {
	var tpl = _.template($('#question-div').html());

	$.each(json.questions, function(i, val) {
		$('#questions .controls').append(tpl({data: val}));
	});


	$('#save-event').click(function() {
		var questions = $('.question-show');
		$.each(questions, function(i,q){
			var answers = $(q).find('.answer');
			$.each(answers, function(j,a){
				json.questions[i].answers[j].current = $(a).find('input').val();
			});
		});
		$.post('/addanswer/', {json: JSON.stringify(json)}).done(function(msg) {
			console.log(msg);
		}).fail(function(msg) {
			console.log(msg);
		});

	});
});