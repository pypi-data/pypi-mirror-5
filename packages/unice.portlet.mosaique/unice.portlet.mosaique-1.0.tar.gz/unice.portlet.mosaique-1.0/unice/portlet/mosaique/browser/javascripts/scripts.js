$( document ).ready(function() {

	$('.mosaique-video').fitVids();

	$('.mosaique-more-items').find('a').click(function(e) {
		e.preventDefault();
		$('.mosaique-col-list').slideDown();
	});
});