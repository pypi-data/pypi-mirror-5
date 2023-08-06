$(document).on('ready', function() {


	/**
		Sets any authorization headers for the API
	**/
	var beforeSend = function(request) {
		request.setRequestHeader('Authorization', localStorage['tastypieDocAuth']);
	};
	if (TASTYPIEDOC_SETTINGS['beforeSend']) {
		beforeSend = new Function(TASTYPIEDOC_SETTINGS['beforeSend']);
	};


	/**
		Given a response from posting to an API endpoint, store an authorization header
		value in the localStorage
	**/
	var parseApiKey = function(resp) {
		localStorage['tastypieDocAuth'] = 'ApiKey ' + resp.user.email + ':' + resp.key;
		onSuccess(resp);
		return resp.key;
	};
	if (TASTYPIEDOC_SETTINGS['parseApiKey']) {
		parseApiKey = new Function('response', TASTYPIEDOC_SETTINGS['parseApiKey']);
	};


	/**
		Given a username and password, create an object to post to the server
		to get an API key back
	**/
	var encodeLogin = function(username, password) {
		return {
			username: username,
			password: password
		}
	};
	if (TASTYPIEDOC_SETTINGS['encodeLogin']) {
		encodeLogin = new Function('username', 'password', TASTYPIEDOC_SETTINGS['encodeLogin']);
	};



	/**
		Simple Syntax Highlighting
		Taken from http://stackoverflow.com/questions/4810841/json-pretty-print-using-javascript
	**/

	function jsonToHTMLString(obj) {
		json = JSON.stringify(obj, undefined, 2);
		result = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
		return result.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function(match) {
			var cls = 'number';
			if (/^"/.test(match)) {
				if (/:$/.test(match)) {
					cls = 'key';
				} else {
					cls = 'string';
				}
			} else if (/true|false/.test(match)) {
				cls = 'boolean';
			} else if (/null/.test(match)) {
				cls = 'null';
			}
			return '<span class="' + cls + '">' + match + '</span>';
		});
	}


	/**
		Replace the url template with the kwargs that the user has entered in 
		the applicable kwarg input fields. Return the actual url with values entered
		in it
	**/

	function parameterizeUrl($target) {
		var entType = $target.data('entitytype'),
			method = $target.data('method'),
			url = $target.data('url');

		$('#' + entType + '-' + method + '-kwargs input').each(function(i, e) {
			var $e = $(e),
				kwargVal = $e.val(),
				kwargName = $e.attr('name'),
				r = new RegExp('\{' + kwargName + '\}');

			url = url.replace(r, kwargVal)
		});
		return url;
	}



	function onError(resp) {
		console.log(resp);
		$('#action-error').show();
		$('#action-error-code').html(resp.status);
		$('#action-error-text').html(resp.statusText);
		$('#action-result').html(resp.responseText);
	}

	function onSuccess(resp) {
		console.log(resp);
		$('#action-result').html(jsonToHTMLString(resp));
		$('#action-error').hide();
	}



	$('#login-btn').on('click', function(e) {
		var username = $('#username-input').val(),
			password = $('#password-input').val(),
			url = TASTYPIEDOC_SETTINGS['api_root'] + TASTYPIEDOC_SETTINGS['apikey'];



		var data = encodeLogin(username, password);


		$.ajax({
			url: url,
			type: 'POST',
			data: JSON.stringify(data),
			dataType: 'json',
			contentType: 'application/json'
		}).success(parseApiKey).error(onError);

	});



	$('.call-endpoint').on('click', function(e) {

		var $t = $(e.currentTarget);
		var url = parameterizeUrl($t);

		$('#action-url').html(url);
		$.ajax({
			url: url,
			type: 'GET',
			beforeSend: beforeSend,
			dataType: 'json'
		}).success(onSuccess).error(onError);
	});



	$('.show-kwargs').on('click', function(e) {
		var $t = $(e.currentTarget),
			entType = $t.data('entitytype'),
			method = $t.data('method');

		$('.kwargs').slideUp(150);
		$('#' + entType + '-' + method + '-kwargs').slideDown(150);
	});

});