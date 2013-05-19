$(function() {
	var tpl = _.template($('#question-div').html());

	$.each(json.questions, function(i, val) {
		$('#questions .controls').append(tpl({data: val}));
	});


	$('#save-event').click(function() {
		var questions = $('.question-show');
		$.each(questions, function(i,q){
			var answers = $(q).find('.answer');
			//normalization
			var Normalizer = 0;
			$.each(answers, function(j,a){
				InvertN += $(a).find('input').val();
			});
			Normalizer = 100/InvertN;
			//end of normalization
			$.each(answers, function(j,a){
			//	json.questions[i].answers[j].current = $(a).find('input').val();	//line without normalization
			//line with normalization:
				json.questions[i].answers[j].current = $(a).find('input').val() / Normalizer;
			});
		});
		$.post('/addanswer/', {json: JSON.stringify(json)}).done(function(msg) {
			console.log(msg);
		}).fail(function(msg) {
			console.log(msg);
		});

	});
});