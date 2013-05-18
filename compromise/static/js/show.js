$(function() {
	var tpl = _.template($('#question-div').html());
	var json = {"timestamp": 1368910890829, "_id": "5197ec2af349c76311d2aa30", "users": [], "questions": [{"index": 0, "name": "asd2", "min": 0, "max": 100, "answers": [{"name": "123"}], "type": "list"}]}

	$.each(json.questions, function(i, val) {
		$('#questions .controls').append(tpl({data: val}));
	});
	$('#save-event').click(function() {
		var questions = $('.question-show');
		$.each(questions, function(i,q){
			var answers = $(q).find('.answer');
			$.each(questions, function(j,a){
				json.questions[i].answers[j].current = $(a).find('input').val();
			});
		});
		$.post('/addenswer/', {json: JSON.stringify(data)}).done(function(msg) {
			console.log(msg);
		}).fail(function(msg) {
			console.log(msg);
		});
	});
});