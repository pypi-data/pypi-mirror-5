requirejs.config({
	urlArgs: 'v=1',
	paths: {
		'theme': 'livedesk-embed/themes/ctkepr'
	}
});
require(['ctkepr.min'], function() {
	require(['../scripts/js/config'], function(){
		function loadCss(url) {
			var link = document.createElement("link");
			link.type = "text/css";
			link.rel = "stylesheet";
			link.href = url;
			document.getElementsByTagName("head")[0].appendChild(link);
		}
		loadCss(require.toUrl('theme/livedesk.css'));
		require(['livedesk-embed/main']);
	});
});